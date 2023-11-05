import OpenGL.GL as gl
import imgui
import glm

from scene import Scene
from model import ModelFromMesh
from mesh import CubeMesh, SquareMesh, SphereMesh
from shaders import PhongShader
from light import LightSource
from model_loader import ModelLoader
from fbo import Framebuffer, FramebufferTexture
from skybox import SkyBox
from environment_map import EnvironmentMap, EnvironmentShader

class Sandbox(Scene):

    def __init__(self):
        Scene.__init__(self, 1200, 800, "Sandbox")
        model_loader = ModelLoader()

        self.lights.append(LightSource(self))
        self.lights.append(LightSource(self))


        self.models.append(ModelFromMesh(self, model_loader.load_model('bunny/bunny.obj')[0], shader=PhongShader()))
        self.models[-1].M.translate([-5,0,0])

        self.skybox = SkyBox(self, 'skybox/sb_frozendusk', extension='jpg')

        self.env_map = EnvironmentMap()

        self.sphere = ModelFromMesh(self, SphereMesh(), shader=EnvironmentShader(map=self.env_map))
        self.sphere.M.scale([2,2,2])

        self.trans = [0, 0, 0]
        self.rot_axis = [0, 0, 0]
        self.rot_angle = 0
        self.scale = [1, 1, 1]

    def draw(self, framebuffer=False):
        if not framebuffer:
            # clear the screen
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        self.draw_reflections()

        if not framebuffer:

            self.env_map.update(self)
            self.sphere.draw()

            for index, light in enumerate(self.lights):
                self.imgui_light_settings(light, index)

            for index, model in enumerate(self.models):
                self.imgui_model_settings(model, index)

            imgui.show_metrics_window()

    def draw_reflections(self):
        self.skybox.draw()

        for model in self.models:
            model.draw()
        
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


        imgui.text("material")
        imgui.separator()    

        changed, self.models[index].mesh.material.Ka = imgui.color_edit3("Ka", *self.models[index].mesh.material.Ka)
        changed, model.mesh.material.Kd = imgui.color_edit3("Kd", *model.mesh.material.Kd)
        changed, model.mesh.material.Ks = imgui.color_edit3("Ks", *model.mesh.material.Ks)
        changed, model.mesh.material.Ns = imgui.slider_float("Ns", model.mesh.material.Ns, 0, 100)
        changed, model.mesh.material.alpha = imgui.slider_float("alpha", model.mesh.material.alpha, 0, 1)

        imgui.pop_id()
        imgui.end()

if __name__ == "__main__":
    sandbox = Sandbox()

    sandbox.run()