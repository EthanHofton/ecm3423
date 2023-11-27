import OpenGL.GL as gl
import imgui
import numpy as np
import glm

from scene import Scene
from model import ModelFromMesh, CompModel, ModelFromObjInstanced, ModelFromObj
from mesh import CubeMesh, SquareMesh, SphereMesh
from shaders import PhongShader, BaseShaderProgram, PhongShaderInstanced
from light import LightSource
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

class City(Scene):

    def __init__(self):
        Scene.__init__(self, 1200, 800, "City")

        self.setup_scene()

        self.trans = [0, 0, 0]
        self.rot_axis = [0, 0, 0]
        self.rot_angle = 0
        self.scale = [1, 1, 1]
        
        # setup vars
        self.police_light_timer = 0
        self.red_light = True


    def setup_scene(self):
        self.directional_light = DirectionalLight()
        self.skybox = SkyBox(self, "skybox/blue_clouds", extension="jpg")
        # self.skybox = SkyBox(self, "skybox/yellow_clouds", extension="jpg")
        # self.city_map = CityMap(3, 5)
        self.city_map = CityMap(5, 5)
        self.add_floor(200, 200)
        self.add_buildings("buildings_pack1")

        self.cars = []
        self.add_car('police/police.obj', (1, 1))

        self.add_dino_scene()
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

        if self.police_light_timer > 0.5:
            self.police_light_timer = 0
            if self.red_light:
                self.police_red_light.intensity = 1
                self.police_blue_light.intensity = 0
            else:
                self.police_red_light.intensity = 0
                self.police_blue_light.intensity = 1
            self.red_light = not self.red_light

    def draw(self, framebuffer=False):
        for car in self.cars:
            car.update(self.delta_time)
        self.update_police_lights(self.delta_time)


        if not framebuffer:
            # clear the screen
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

            # draw the skybox
            self.skybox.draw()        

        for model in self.models:
            model.draw()

        if not framebuffer:

            # update the environment map with regrards to the sphere
            for index, light in enumerate(self.lights):
                self.imgui_light_settings(light, index)

            self.imgui_light_settings(self.directional_light, "directional light")
            self.imgui_model_settings(self.floor, "floor")

            imgui.show_metrics_window()

    def draw_reflections(self):
        pass
        
    def imgui_light_settings(self, light, index):
        imgui.begin(f"Light Source {index}")

        # create a slider for the light position
        if hasattr(light, 'position'):
            changed, light.position = imgui.drag_float3("position", *light.position)
        if hasattr(light, 'direction'):
            changed, light.direction = imgui.drag_float3("direction", *light.direction)
        changed, light.Ia = imgui.color_edit3("Ia", *light.Ia)
        changed, light.Id = imgui.color_edit3("Id", *light.Id)
        changed, light.Is = imgui.color_edit3("Is", *light.Is)

        if isinstance(light, LightSource):
            changed, light.constant = imgui.drag_float("constant", light.constant, 0.01)
            changed, light.linear = imgui.drag_float("linear", light.linear, 0.01)
            changed, light.quadratic = imgui.drag_float("quadratic", light.quadratic, 0.01)
            changed, light.intensity = imgui.drag_float("intensity", light.intensity, 0.01)

        imgui.end()


    def imgui_model_settings(self, model, index):
        imgui.begin(f"Model {index}")
        imgui.push_id(str(index))

        imgui.text("transformation")

        imgui.separator()    

        changed, self.trans = imgui.drag_float3("translation", *self.trans)
        changed, self.rot_axis = imgui.drag_float3("rotation axis", *self.rot_axis)
        changed, self.rot_angle = imgui.drag_float("rotation angle", self.rot_angle)
        changed, self.scale = imgui.drag_float3("scale", *self.scale)

        if imgui.button("apply"):
            model.M.translate(self.trans)
            model.M.rotate(self.rot_axis, glm.radians(self.rot_angle))
            model.M.scale(self.scale)

        if imgui.button("reset"):
            self.trans = [0, 0, 0]
            self.rot_axis = [0, 0, 0]
            self.rot_angle = 0
            self.scale = [1, 1, 1]


        if hasattr(model, 'mesh'):
            imgui.text("material")
            imgui.separator()    

            changed, model.mesh.material.Ka = imgui.color_edit3("Ka", *model.mesh.material.Ka)
            changed, model.mesh.material.Kd = imgui.color_edit3("Kd", *model.mesh.material.Kd)
            changed, model.mesh.material.Ks = imgui.color_edit3("Ks", *model.mesh.material.Ks)
            changed, model.mesh.material.Ns = imgui.slider_float("Ns", model.mesh.material.Ns, 0, 100)
            changed, model.mesh.material.alpha = imgui.slider_float("alpha", model.mesh.material.alpha, 0, 1)

        imgui.pop_id()
        imgui.end()


if __name__ == "__main__":
    sandbox = City()

    sandbox.run()