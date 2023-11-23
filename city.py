import OpenGL.GL as gl
import imgui
import numpy as np
import glm
import os

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

class City(Scene):

    def __init__(self):
        Scene.__init__(self, 1200, 800, "City")

        # self.lights.append(LightSource(self))

        self.setup_scene()

        self.trans = [0, 0, 0]
        self.rot_axis = [0, 0, 0]
        self.rot_angle = 0
        self.scale = [1, 1, 1]


    def setup_scene(self):
        self.skybox = SkyBox(self, "skybox/ame_ash", extension="bmp")
        self.add_floor(100, 100)
        self.add_buildings(10, 10, "buildings_pack1")
        self.add_roads(10, 10)

    def add_floor(self, w, h):
        self.floor = ModelFromMesh(self, SquareMesh(), shader=PhongShader())
        self.floor.M.rotate([1, 0, 0], glm.radians(-90))
        self.floor.M.scale([w, 1, h])
        self.models.append(self.floor)

    def add_buildings(self, num_rows, num_cols, pack):
        # get all obj files in the models folder
        objs = []
        for file in os.listdir(f"models/{pack}/"):
            if file.endswith(".obj"):
                objs.append(f"{pack}/{file}")

        towers = []

        for obj in objs:
            towers.append(Towers(self, obj, num_instances=100))

        building_models = []
        for i in range(num_rows):
            for j in range(num_cols):
                towers[np.random.randint(0, len(towers))].add_tower(i, j)

        for tower in towers:
            self.models.append(tower)

    def add_roads(self, num_rows, num_cols):
        road_shader = PhongShaderInstanced()
        road_model = ModelFromObjInstanced(self, "road/road.obj", shader=road_shader, num_instances=num_rows * num_cols)        
        road_model.M.rotate([0, 1, 0], glm.radians(90))

        for i in range(num_cols):
            for j in range(num_rows):
                road_shader.add_offset(np.array([(j) * -10, 0, (i + 0.5) * 20]))

        self.models.append(road_model)

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


class Tower(CompModel):

    def __init__(self, scene, file, col, row):
        model_loader = ModelLoader()
        self.row_width = 10
        self.col_width = 10

        building_meshes = model_loader.load_model(file, generate_normals=True, flip_uvs=True, flip_winding=False, optimize_meshes=True)
        building_models = []
        for mesh in building_meshes:
            building_models.append(ModelFromMesh(scene, mesh, shader=PhongShader()))         
            building_models[-1].M.translate([col * self.col_width, 0, row * self.row_width])
    
        CompModel.__init__(self, scene, building_models)

class Towers(ModelFromObjInstanced):

    def __init__(self, scene, file, num_instances=10):
        self.shader = PhongShaderInstanced()
        self.offsets = []
        ModelFromObjInstanced.__init__(self, scene, file, shader=self.shader, num_instances=num_instances)

    def add_tower(self, offset_x, offset_z):
        self.shader.add_offset(np.array([offset_x * 20, 0, offset_z * 10], 'f'))

if __name__ == "__main__":
    sandbox = City()

    sandbox.run()