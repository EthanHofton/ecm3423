from model import ModelFromObjInstanced
from shaders import PhongShaderInstanced
from coordinate_system import CoordinateSystem

class Towers(ModelFromObjInstanced):

    def __init__(self, scene, file, num_instances=10):
        self.shader = PhongShaderInstanced('phong_instanced_normal_map')
        self.offsets = []
        ModelFromObjInstanced.__init__(self, scene, file, shader=self.shader, num_instances=num_instances)

    def add_tower(self, offset_x, offset_z):
        self.shader.add_offset(CoordinateSystem.get_world_pos(offset_x, offset_z))