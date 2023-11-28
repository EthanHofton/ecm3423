import OpenGL.GL as gl
import imgui
import numpy as np
import glm

from matutils import unhomog
from transform import TransformMatrix
from scene import Scene
from model import ModelFromMesh, CompModel, ModelFromObjInstanced, ModelFromObj
from mesh import CubeMesh, SquareMesh, SphereMesh
from shaders import PhongShader, BaseShaderProgram, PhongShaderInstanced, PhongShaderNormalMapInstancedMatrices
from light import LightSource, SpotLight
from model_loader import ModelLoader
from fbo import Framebuffer, FramebufferTexture
from skybox import SkyBox
from environment_map import EnvironmentMap, EnvironmentShader, EnvironmentShaderRefractive
from texture import Texture
from material import Material
from city_map import CityMap
from light import DirectionalLight
from coordinate_system import CoordinateSystem
from car import Car, CarInstanced
from imgui_windows import show_lighting_settings, show_scene_settings, show_light_settings

class City(Scene):
    """
    Represents a city scene in a computer graphics application.
    """

    def __init__(self):
        """
        Initializes the City object.
        """
        Scene.__init__(self, 1200, 800, "City")
        self.car_offsets = []

        self.setup_scene()
        self.camera._pos = glm.vec3(CoordinateSystem.get_world_pos(0, 1) + [0, 3, 0])
        self.camera._update_vectors()
        
        # setup vars
        self.police_light_timer = 0
        self.POLICE_LIGHT_TIME = 1
        self.red_light = True
        self.player_spotlight = None
        self.update_tank_env_map = False

    def setup_scene(self):
        """
        Sets up the city scene by adding buildings, cars, police cars, environment map, dinos, and traffic lights.
        """
        self.directional_light = DirectionalLight()
        self.skybox = SkyBox(self, "skybox/blue_clouds", extension="jpg")

        self.city_map = CityMap(5, 5)

        self.add_floor(200, 200)
        self.add_buildings("buildings_pack1")

        self.add_cars(25)
        self.add_police_cars()
        self.add_env_map()
        self.add_dinos(20)
        self.add_traffic_light()

    def add_cars(self, n):
        """
        Adds cars to the city scene.

        Args:
            n (int): The number of cars to add.
        """
        self.cars = {}
        self.car_models = [
            'police_stealth/police_stealth.obj',
            'taxi/taxi.obj',
            'car_white/car_white.obj',
            'car_red/car_red.obj',
            'police/police.obj',
        ]

        for i in range(n):
            self.add_car(self.car_models[i % len(self.car_models)])

    def _get_unoccupied_intersection(self):
        """
        Gets an unoccupied intersection in the city map.

        Returns:
            tuple: The coordinates of the unoccupied intersection.
        
        Raises:
            Exception: If no more intersections are available.
        """
        rand_offset = self.city_map.get_random_intersection(blacklist=self.car_offsets)
        if rand_offset is None:
            raise Exception("No more intersections available")
        self.car_offsets.append(rand_offset)
        return rand_offset

    def add_floor(self, w, h):
        """
        Adds a floor to the city scene.

        Args:
            w (int): The width of the floor.
            h (int): The height of the floor.
        """
        floor_material = Material(map_Kd="brickwall.jpg", map_bump="brickwall_normal.jpg")
        self.floor = ModelFromMesh(self, SquareMesh(material=floor_material), shader=PhongShader('phong_normal_map'))
        self.floor.M.rotate([1, 0, 0], glm.radians(-90))
        self.floor.M.scale([w, 1, h])
        self.floor.mesh.textureCoords *= 120
        self.floor.update()
        self.models.append(self.floor)

    def add_buildings(self, pack):
        """
        Adds buildings to the city scene.

        Args:
            pack (str): The name of the building pack to use.
        """
        towers, roads, roads_h = self.city_map.generate_city(pack, "road/road_horizontal_textured.obj", "road/road_textured.obj", self)
        self.models.extend(towers)
        self.models.append(roads)
        self.models.append(roads_h)

    def add_car(self, file):
        """
        Adds a car to the city scene.

        Args:
            file (str): The file path of the car model.
        """
        positions_1 = [(0.25, 0.25), (0.25, 2.75), (2.75,2.75), (2.75,0.25)]
        positions_2 = [(0.25, 2.75), (2.75,2.75), (2.75,0.25), (0.25, 0.25)]
        positions_3 = [(2.75,2.75), (2.75,0.25), (0.25, 0.25), (0.25, 2.75)]
        positions_4 = [(2.75,0.25), (0.25, 0.25), (0.25, 2.75), (2.75,2.75)]

        car_positions = [positions_1, positions_2, positions_3, positions_4]

        offset = self._get_unoccupied_intersection()
        for i in range(len(car_positions)):
            car_positions[i] = [(x + offset[0], y + offset[1]) for x, y in car_positions[i]]

        if file in self.cars:
            car = self.cars[file]
            for positions in car_positions:
                car.add_car(positions)
            car.add_num_instances(4)
            return

        animation_time = np.random.uniform(3, 5)
        car = CarInstanced(self, file, num_instance=4, animation_time=animation_time)
        car.M.translate(np.array([0, CoordinateSystem.ROAD_OFFSET, 0], 'f'))

        for positions in car_positions:
            car.add_car(positions)

        self.cars[file] = car
        self.models.append(car)

    def add_police_cars(self):
        """
        Adds police cars to the city scene.
        """
        # load police cars
        animation_time = np.random.uniform(1, 3)
        self.police_car = CarInstanced(self, 'police/police.obj', num_instance=3, animation_time=animation_time)
        self.police_car.M.translate(np.array([0, CoordinateSystem.ROAD_OFFSET, 0], 'f'))

        positions_1 = [(-2, -2), (4, -2)]
        positions_2 = [(4, -2), (4, 4)]
        positions_3 = [(-2, -3.5), (-2, 4)]

        self.police_car.add_car(positions_1)
        self.police_car.add_car(positions_2)
        self.police_car.add_car(positions_3)

        self.police_car_lights = []
        constant = 1
        linear = 0.07
        quadratic = 0.017
        red = [1, 0, 0]
        blue = [0, 0, 1]
        self.police_car_lights.append(LightSource(Ia=red, Id=red, Is=red, constant=constant, linear=linear, quadratic=quadratic))
        self.police_car_lights.append(LightSource(Ia=blue, Id=blue, Is=blue, constant=constant, linear=linear, quadratic=quadratic))
        self.police_car_lights.append(LightSource(Ia=red, Id=red, Is=red, constant=constant, linear=linear, quadratic=quadratic))

        for light in self.police_car_lights:
            self.lights.append(light)

        self.models.append(self.police_car)

    def add_env_map(self):
        """
        Adds an environment map to the city scene.
        """
        self.tank_env_map = EnvironmentMap(width=1024, height=1024)
        self.tank_shader = EnvironmentShader(map=self.skybox.cube_map)
        self.tank = ModelFromObj(self, 'tank/tank.obj', shader=self.tank_shader)
        self.tank.M.translate(np.array([0, CoordinateSystem.ROAD_OFFSET, 0], 'f'))
        self.tank.M.translate(CoordinateSystem.get_world_pos(-2, -4))
        self.models.append(self.tank)

    def update_police_lights(self, dt):
        """
        Updates the police car lights.

        Args:
            dt (float): The time since the last update.
        """
        self.police_light_timer += dt

        if self.police_light_timer > self.POLICE_LIGHT_TIME:
            for light in self.police_car_lights:
                if light.Ia[0] == 1:
                    light.Ia = [0, 0, 1]
                    light.Id = [0, 0, 1]
                    light.Is = [0, 0, 1]
                else:
                    light.Ia = [1, 0, 0]
                    light.Id = [1, 0, 0]
                    light.Is = [1, 0, 0]
            self.police_light_timer = 0
        
        for index, light in enumerate(self.police_car_lights):
            light.position = self.police_car.shader.matricies[index].get_position() + np.array([0, 0.5, 0])

    def update_player_spotlight(self):
        """
        Updates the player spotlight.
        """
        if self.player_spotlight is None:
            return

        self.player_spotlight.position = self.camera._pos
        self.player_spotlight.direction = self.camera.front()

    def add_dinos(self, n):
        """
        Adds dinos to the city scene.

        Args:
            n (int): The number of dinos to add.
        """
        # load dino
        swarm_size = 4
        self.dyno_shader = PhongShaderNormalMapInstancedMatrices()
        self.dyno = ModelFromObjInstanced(self, 'dyno/dyno.obj', shader=self.dyno_shader, num_instances=n*5)
        self.dyno.M.translate(np.array([0, CoordinateSystem.ROAD_OFFSET, 0], 'f'))
        self.models.append(self.dyno)

        self.dyno_positions = []
        for i in range(n):
            offset = None

            while offset is None or offset in self.dyno_positions:
                offset_x = np.random.randint(0, len(self.city_map.road_positions))
                offset_y = np.random.randint(0, len(self.city_map.road_positions[offset_x]))
                offset = self.city_map.road_positions[offset_x][offset_y]

            self.dyno_positions.append(offset)
            dyno_swarm_orientation = np.random.uniform(0, 2 * np.pi)
            for i in range(swarm_size):
                dino_matrix = TransformMatrix()
                dino_orientation_offset = np.random.uniform(-np.pi / 4, np.pi / 4)
                dino_position_offset = np.random.uniform(-5, 5, 2)
                dino_matrix.rotate([0, 1, 0], dyno_swarm_orientation + dino_orientation_offset)
                dino_matrix.translate(CoordinateSystem.get_world_pos(offset[0], offset[1]))
                dino_matrix.translate([dino_position_offset[0], 0, dino_position_offset[1]])
                self.dyno_shader.add_matrix(dino_matrix)

    def draw(self, framebuffer=False):
        """
        Draws the city scene.

        Args:
            framebuffer (bool): Whether to draw to a framebuffer or the screen.
        """
        if not framebuffer:
            # update the scene
            self.update()

            # clear the screen
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

            # draw the skybox
            self.skybox.draw()        

        for model in self.models:
            model.draw()

        if not framebuffer:
            self.imgui_windows()

    def draw_reflections(self):
        """
        Draws the reflections in the city scene.
        """
        self.skybox.draw()
        for model in self.models:
            if model == self.tank:
                continue
            model.draw()

    def add_traffic_light(self):
        """
        Adds traffic lights to the city scene.
        """
        n = 25
        self.traffic_light_shader = PhongShaderInstanced('phong_instanced_normal_map')
        self.traffic_light = ModelFromObjInstanced(self, 'traffic_light/tf.obj', shader=self.traffic_light_shader, num_instances=n)

        self.traffic_light_lights = []
        
        count = 0
        corner_offset_x = 0.6
        corner_offset_z = 0.6
        for x, intersection_row in enumerate(self.city_map.intersection_positions):
            if x == len(self.city_map.intersection_positions) - 1:
                continue
            for y, intersection in enumerate(intersection_row):
                if y == len(intersection_row) - 1:
                    continue

                if count >= n:
                    break
                self.traffic_light_shader.add_offset(CoordinateSystem.get_world_pos(intersection[0] + corner_offset_x, intersection[1] + corner_offset_z))

                light = LightSource()
                light.Ia = [0, 1, 0]
                light.Id = [0, 1, 0]
                light.Is = [0, 1, 0]
                self.traffic_light_lights.append(light)
                count += 1

    def update(self):
        """
        Updates the city scene.
        """
        for car in self.cars.values():
            car.update(self.delta_time)
        self.police_car.update(self.delta_time)

        self.update_police_lights(self.delta_time)
        self.update_player_spotlight()
        
        if self.update_tank_env_map:
            self.tank_env_map.update(self, self.tank)

    def imgui_windows(self):
        """
        Displays ImGui windows for the city scene.
        """
        show_lighting_settings(self)
        show_scene_settings(self)
        imgui.show_metrics_window()

if __name__ == "__main__":
    sandbox = City()
    sandbox.run()