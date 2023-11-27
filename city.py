import OpenGL.GL as gl
import imgui
import numpy as np
import glm

from scene import Scene
from model import ModelFromMesh, CompModel, ModelFromObjInstanced, ModelFromObj
from mesh import CubeMesh, SquareMesh, SphereMesh
from shaders import PhongShader, BaseShaderProgram, PhongShaderInstanced
from light import LightSource, SpotLight
from model_loader import ModelLoader
from fbo import Framebuffer, FramebufferTexture
from skybox import SkyBox
from environment_map import EnvironmentMap, EnvironmentShader
from texture import Texture
from material import Material
from city_map import CityMap
from light import DirectionalLight
from coordinate_system import CoordinateSystem
from car import Car, CarInstanced
from imgui_windows import show_lighting_settings, show_scene_settings, show_light_settings

class City(Scene):

    def __init__(self):
        Scene.__init__(self, 1200, 800, "City")

        self.setup_scene()
        
        # setup vars
        self.police_light_timer = 0
        self.POLICE_LIGHT_TIME = 0.5
        self.red_light = True
        self.player_spotlight = None


    def setup_scene(self):
        self.directional_light = DirectionalLight()
        self.skybox = SkyBox(self, "skybox/blue_clouds", extension="jpg")

        # self.city_map = CityMap(3, 5)
        self.city_map = CityMap(5, 5)
        self.add_floor(200, 200)
        # self.add_buildings("buildings_pack1")

        self.cars = []
        # self.add_car('police/police.obj', (1, 1))

        self.spot_lights.append(SpotLight())

        # self.add_dino_scene()
        # self.add_car('police_stealth/police_stealth.obj', (4, 4))
        # self.add_car('taxi/taxi.obj', (-1, -1))
        # self.add_car('car_white/car_white.obj', (-4, 1))
        # self.add_car('car_red/car_red.obj', (3, -1))

    def add_floor(self, w, h):
        floor_material = Material(map_Kd="brickwall.jpg", map_bump="brickwall_normal.jpg")
        self.floor = ModelFromMesh(self, SquareMesh(material=floor_material), shader=PhongShader('phong_normal_map'))
        self.floor.M.rotate([1, 0, 0], glm.radians(-90))
        self.floor.M.scale([w, 1, h])
        self.floor.mesh.textureCoords *= 120
        self.floor.update()
        self.models.append(self.floor)

    def add_buildings(self, pack):
        towers, roads, roads_h = self.city_map.generate_city(pack, "road/road_horizontal_textured.obj", "road/road_textured.obj", self)
        self.models.extend(towers)
        self.models.append(roads)
        self.models.append(roads_h)

    def add_car(self, file, offset):
        positions_1 = [(0, 0), (0, 2.75), (2.75,2.75), (2.75,0)]
        positions_2 = [(0, 2.75), (2.75,2.75), (2.75,0), (0, 0)]
        positions_3 = [(2.75,2.75), (2.75,0), (0, 0), (0, 2.75)]
        positions_4 = [(2.75,0), (0, 0), (0, 2.75), (2.75,2.75)]

        car_positions = [positions_1, positions_2, positions_3, positions_4]
        for i in range(len(car_positions)):
            car_positions[i] = [(x + offset[0], y + offset[1]) for x, y in car_positions[i]]

        car = CarInstanced(self, file, num_instance=4)
        car.M.translate(np.array([0, CoordinateSystem.ROAD_OFFSET, 0], 'f'))

        for positions in car_positions:
            car.add_car(positions)

        self.cars.append(car)
        self.models.append(car)

    def add_dino_scene(self):
        # load police cars
        self.police_car = ModelFromObj(self, 'police/police.obj', shader=PhongShader('phong_normal_map'))
        self.police_car.M.translate(np.array([0, CoordinateSystem.ROAD_OFFSET, 0], 'f'))
        self.police_car.M.translate(CoordinateSystem.get_world_pos(-2, -2))

        # add colored lights to police car
        light_pos = self.police_car.M.get_position() + [0, 0.5, 0]
        self.police_red_light = LightSource(position=light_pos, Ia=[1, 0, 0], Id=[1, 0, 0], Is=[1, 0, 0], linear=0.2, quadratic=0.01)
        self.police_blue_light = LightSource(position=light_pos, Ia=[0, 0, 1], Id=[0, 0, 1], Is=[0, 0, 1], linear=0.2, quadratic=0.01)

        self.lights.append(self.police_blue_light)
        self.lights.append(self.police_red_light)

        self.models.append(self.police_car)

        # load dino
        self.dyno = ModelFromObj(self, 'dyno/dyno.obj', shader=PhongShader('phong_normal_map'))
        self.dyno.M.translate(np.array([0, CoordinateSystem.ROAD_OFFSET, 0], 'f'))
        self.dyno.M.translate(CoordinateSystem.get_world_pos(-4, -2))
        self.models.append(self.dyno)

    def update_police_lights(self, dt):
        self.police_light_timer += dt

        if self.police_light_timer > self.POLICE_LIGHT_TIME:
            self.police_light_timer = 0
            if self.red_light:
                self.police_red_light.intensity = 1
                self.police_blue_light.intensity = 0
            else:
                self.police_red_light.intensity = 0
                self.police_blue_light.intensity = 1
            self.red_light = not self.red_light

    def update_player_spotlight(self):
        if self.player_spotlight is None:
            return

        self.player_spotlight.position = self.camera._pos
        self.player_spotlight.direction = self.camera.front()

    def draw(self, framebuffer=False):
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
        pass

    def update(self):
        for car in self.cars:
            car.update(self.delta_time)
        # self.update_police_lights(self.delta_time)
        # self.update_player_spotlight()

    def imgui_windows(self):
        show_lighting_settings(self)
        show_scene_settings(self)
        show_light_settings(self.spot_lights[-1], "spotlight")
        imgui.show_metrics_window()


if __name__ == "__main__":
    sandbox = City()
    sandbox.run()