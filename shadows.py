import OpenGL.GL as gl
import imgui
import numpy as np
import glm

from scene import Scene
from model import ModelFromMesh, CompModel
from mesh import CubeMesh, SquareMesh, SphereMesh
from shaders import PhongShader
from light import LightSource
from model_loader import ModelLoader
from fbo import Framebuffer, FramebufferTexture
from skybox import SkyBox
from environment_map import EnvironmentMap, EnvironmentShader
from texture import Texture
from material import Material

class Sandbox(Scene):

    def __init__(self):
        Scene.__init__(self, 1200, 800, "Sandbox")

        self.lights.append(LightSource(self))

        self.setup_scene()

        self.trans = [0, 0, 0]
        self.rot_axis = [0, 0, 0]
        self.rot_angle = 0
        self.scale = [1, 1, 1]


    def setup_scene(self):
        wood_texture = Texture('wood.png')


        self.floor = ModelFromMesh(self, SquareMesh(material=Material(map_Kd=wood_texture)), shader=PhongShader())
        self.floor.M.rotate([1, 0, 0], glm.radians(-90))
        self.floor.M.scale([30, 30, 30])
        self.floor.mesh.textureCoords *= 30
        self.floor.update()


        boxes = []
        for i in range(5):
            boxes.append(Box(self, random_pos=True))
            self.models.append(boxes[-1])

        self.models.append(self.floor)

    def draw(self, framebuffer=False):
        if not framebuffer:
            # clear the screen
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        for model in self.models:
            model.draw()

        if not framebuffer:

            # update the environment map with regrards to the sphere
            for index, light in enumerate(self.lights):
                self.imgui_light_settings(light, index)

            for index, model in enumerate(self.models):
                self.imgui_model_settings(model, index)

            imgui.show_metrics_window()

    def draw_reflections(self):
        pass
        
    def imgui_light_settings(self, light, index):
        imgui.begin(f"Light Source {index}")

        # create a slider for the light position
        changed, light.position = imgui.drag_float3("position", *light.position)
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


class Box(ModelFromMesh):

    def __init__(self, scene, random_pos=True):
        boxMaterial = Material(map_Kd=Texture('container.png'), map_Ks=Texture('container_specular.png'), Ns=32)
        ModelFromMesh.__init__(self, scene, CubeMesh(material=boxMaterial, inside=True), shader=PhongShader())

        if random_pos:
            scale = np.random.uniform(0.5, 1)
            self.M.scale([scale, scale, scale])
            self.M.rotate([1, 0, 0], np.random.uniform(0, 360))
            self.M.rotate([0, 1, 0], np.random.uniform(0, 360))
            self.M.rotate([0, 0, 1], np.random.uniform(0, 360))
            self.M.translate([np.random.uniform(-10, 10), np.random.uniform(0, 5), np.random.uniform(-10, 10)])


if __name__ == "__main__":
    sandbox = Sandbox()

    sandbox.run()