import numpy as np

from model import ModelFromObjInstanced
from shaders import PhongShaderInstanced

class Towers(ModelFromObjInstanced):

    def __init__(self, scene, file, num_instances=10):
        self.shader = PhongShaderInstanced()
        self.offsets = []
        ModelFromObjInstanced.__init__(self, scene, file, shader=self.shader, num_instances=num_instances)

    def add_tower(self, offset_x, offset_z):
        self.shader.add_offset(np.array([offset_x * 20, 0, offset_z * 20], 'f'))