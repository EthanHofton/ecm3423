import numpy as np
from model import ModelFromObj, ModelFromObjInstanced
from shaders import PhongShader, PhongShaderNormalMapInstancedMatrices
from coordinate_system import CoordinateSystem
from transform import TransformMatrix

class Car(ModelFromObj):
    """
    A class representing a car in a computer graphics scene.

    Attributes:
        scene (Scene): The scene the car belongs to.
        file (str): The file path of the car model.
        grid_positions (list): A list of grid positions the car will move between.
        shader (Shader, optional): The shader to use for rendering the car. Defaults to PhongShader('phong_normal_map').
        animation_time (float, optional): The time it takes for the car to move between grid positions. Defaults to 2.
        current_grid_pos (int): The index of the current grid position.
        t (float): The current time in the animation.
        M (Matrix4): The transformation matrix of the car.
    """

    def __init__(self, scene, file, grid_positions, shader=PhongShader('phong_normal_map'), animation_time=2):
        """
        Initializes a Car object.

        Args:
            scene (Scene): The scene the car belongs to.
            file (str): The file path of the car model.
            grid_positions (list): A list of grid positions the car will move between.
            shader (Shader, optional): The shader to use for rendering the car. Defaults to PhongShader('phong_normal_map').
            animation_time (float, optional): The time it takes for the car to move between grid positions. Defaults to 2.
        """
        ModelFromObj.__init__(self, scene, file, shader=shader)
        self.grid_positions = grid_positions
        self.current_grid_pos = 0
        self.t = 0
        self.animation_time = animation_time

    def update(self, dt):
        """
        Updates the car's position and rotation based on the elapsed time.

        Args:
            dt (float): The elapsed time since the last update.
        """
        self.t += dt
        if self.t > self.animation_time:
            self.t = 0
            self.current_grid_pos += 1
            if self.current_grid_pos >= len(self.grid_positions):
                self.current_grid_pos = 0

        a = CoordinateSystem.get_world_pos(self.grid_positions[self.current_grid_pos][0], self.grid_positions[self.current_grid_pos][1])
        b = CoordinateSystem.get_world_pos(self.grid_positions[(self.current_grid_pos + 1) % len(self.grid_positions)][0], self.grid_positions[(self.current_grid_pos + 1) % len(self.grid_positions)][1])
        d_pos = a + (b - a) * (self.t / self.animation_time)

        d = b - a
        angle = np.arctan2(d[0], d[2])

        if angle == 0:
            self.M.reset()
        else:
            self.M.set_rotation([0, 1, 0], angle)
        self.M.translate(d_pos)


class CarInstanced(ModelFromObjInstanced):
    """
    Represents an instanced car model in a scene.

    Args:
        scene (Scene): The scene to add the car model to.
        file (str): The file path of the car model.
        num_instance (int, optional): The number of instances of the car model to create. Defaults to 5.
        animation_time (float, optional): The time it takes for the car to complete one animation cycle. Defaults to 2.

    Attributes:
        shader (PhongShaderNormalMapInstancedMatrices): The shader used for rendering the car model.
        positions (list): The list of positions for each car instance.
        current_grid_positions (list): The current grid positions of each car instance.
        t (float): The current time of the animation.
        animation_time (float): The time it takes for the car to complete one animation cycle.
        current_cars (int): The number of current car instances.

    """

    def __init__(self, scene, file, num_instance=5, animation_time=2):
        self.shader = PhongShaderNormalMapInstancedMatrices()
        ModelFromObjInstanced.__init__(self, scene, file, shader=self.shader, num_instances=num_instance)
        self.positions = []
        self.current_grid_positions = []
        self.t = 0
        self.animation_time = animation_time
        self.current_cars = 0


    def add_car(self, positions):
        """
        Adds a car instance to the scene.

        Args:
            positions (list): The positions of the car instance in the grid.

        """
        self.positions.append(positions)
        self.shader.add_matrix(TransformMatrix())
        self.current_grid_positions.append(0)
        self.current_cars += 1

    def lerp(self, index):
        """
        Performs linear interpolation between two grid positions of a car instance.

        Args:
            index (int): The index of the car instance.

        """
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
        """
        Updates the car instances and performs the animation.

        Args:
            dt (float): The time elapsed since the last update.

        """
        self.t += dt
        if self.t > self.animation_time:
            self.t = 0
            for i in range(self.current_cars):
                self.current_grid_positions[i] += 1
                if self.current_grid_positions[i] >= len(self.positions[i]):
                    self.current_grid_positions[i] = 0

        for i in range(self.current_cars):
            self.lerp(i)