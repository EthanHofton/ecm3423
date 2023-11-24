import OpenGL.GL as gl
import imgui
import numpy as np
import glm

from scene import Scene
from model import ModelFromMesh, CompModel, ModelFromObjInstanced
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

class City(Scene):

    def __init__(self):
        Scene.__init__(self, 1200, 800, "City")

        self.setup_scene()

        self.trans = [0, 0, 0]
        self.rot_axis = [0, 0, 0]
        self.rot_angle = 0
        self.scale = [1, 1, 1]


    def setup_scene(self):
        self.directional_light = DirectionalLight()
        self.skybox = SkyBox(self, "skybox/ame_ash", extension="bmp")
        self.city_map = CityMap(3, 5)
        # self.add_floor(100, 100)
        self.add_buildings("buildings_pack1")

    def add_floor(self, w, h):
        self.floor = ModelFromMesh(self, SquareMesh(), shader=PhongShader())
        self.floor.M.rotate([1, 0, 0], glm.radians(-90))
        self.floor.M.scale([w, 1, h])
        self.models.append(self.floor)

    def add_buildings(self, pack):
        towers, roads = self.city_map.generate_city(pack, "road/road.obj", self)
        self.models.extend(towers)
        self.models.append(roads)

    def draw(self, framebuffer=False):
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