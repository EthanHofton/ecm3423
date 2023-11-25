import numpy as np
from model import ModelFromObj, ModelFromObjInstanced
from shaders import PhongShader, PhongShaderNormalMapInstancedMatrices
from coordinate_system import CoordinateSystem
from transform import TransformMatrix

class Car(ModelFromObj):

    def __init__(self, scene, file, grid_positions, shader=PhongShader('phong_normal_map'), animation_time=2):
        ModelFromObj.__init__(self, scene, file, shader=shader)
        self.grid_positions = grid_positions
        self.current_grid_pos = 0
        self.t = 0
        self.animation_time = animation_time

    def update(self, dt):
        # lerp between current and next grid position
        self.t += dt
        if self.t > self.animation_time:
            self.t = 0
            self.current_grid_pos += 1
            if self.current_grid_pos >= len(self.grid_positions):
                self.current_grid_pos = 0

        a = CoordinateSystem.get_world_pos(self.grid_positions[self.current_grid_pos][0], self.grid_positions[self.current_grid_pos][1])
        b = CoordinateSystem.get_world_pos(self.grid_positions[(self.current_grid_pos + 1) % len(self.grid_positions)][0], self.grid_positions[(self.current_grid_pos + 1) % len(self.grid_positions)][1])
        d_pos = a + (b - a) * (self.t / self.animation_time)

        # rotate to face next grid position
        d = b - a
        angle = np.arctan2(d[0], d[2])  # calculate rotation angle based on direction vector

        # reset the matrix to that rotation
        if angle == 0:
            self.M.reset()
        else:
            self.M.set_rotation([0, 1, 0], angle)
        # move back to position
        self.M.translate(d_pos)


class CarInstanced(ModelFromObjInstanced):

    def __init__(self, scene, file, num_instance=5, animation_time=2):
        self.shader = PhongShaderNormalMapInstancedMatrices()
        ModelFromObjInstanced.__init__(self, scene, file, shader=self.shader, num_instances=num_instance)
        self.positions = []
        self.current_grid_positions = []
        self.t = 0
        self.animation_time = animation_time
        self.current_cars = 0


    def add_car(self, positions):
        self.positions.append(positions)
        self.shader.add_matrix(TransformMatrix())
        self.current_grid_positions.append(0)
        self.current_cars += 1

    def lerp(self, index):
        a_pos = [self.positions[index][self.current_grid_positions[index]][0], self.positions[index][self.current_grid_positions[index]][1]]
        b_pos = [self.positions[index][(self.current_grid_positions[index] + 1) % len(self.positions[index])][0], self.positions[index][(self.current_grid_positions[index] + 1) % len(self.positions[index])][1]]

        a = CoordinateSystem.get_world_pos(a_pos[0], a_pos[1])
        b = CoordinateSystem.get_world_pos(b_pos[0], b_pos[1])

        d_pos = a + (b - a) * (self.t / self.animation_time)
        d = b - a
        angle = np.arctan2(d[0], d[2])
        if angle == 0:
            self.shader.matricies[index].reset()
        else:
            self.shader.matricies[index].set_rotation([0, 1, 0], angle)
        self.shader.matricies[index].translate(d_pos)

    def update(self, dt):
        self.t += dt
        if self.t > self.animation_time:
            self.t = 0
            for i in range(self.current_cars):
                self.current_grid_positions[i] += 1
                if self.current_grid_positions[i] >= len(self.positions[i]):
                    self.current_grid_positions[i] = 0

        for i in range(self.current_cars):
            self.lerp(i)