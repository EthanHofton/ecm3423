import glm

class TransformMatrix():

    def __init__(self):
        self.matrix = glm.mat4(1.0)  # Initialize with an identity matrix

    def translate(self, translation):
        translation_matrix = glm.translate(glm.mat4(1.0), translation)
        self.matrix = translation_matrix * self.matrix

    def rotate(self, rotation):
        rotation_matrix = glm.mat4_cast(rotation)
        self.matrix = rotation_matrix * self.matrix

    def rotate(self, axis, angle):
        if axis == [0.0, 0.0, 0.0]:
            return

        if angle == 0.0:
            return

        rotation_matrix = glm.rotate(glm.mat4(1.0), angle, axis)
        self.matrix = rotation_matrix * self.matrix

    def scale(self, scale):
        scale_matrix = glm.scale(glm.mat4(1.0), scale)
        self.matrix = scale_matrix * self.matrix

    def get_position(self):
        return glm.vec3(self.matrix[3][0], self.matrix[3][1], self.matrix[3][2])

    def get_rotation(self):
        return glm.quat(glm.mat3(self.matrix))

    def get_scale(self):
        return glm.vec3(self.matrix[0][0], self.matrix[1][1], self.matrix[2][2])

    def reset(self):
        self.matrix = glm.mat4(1.0)

    def set_position(self, position):
        self.matrix[3][0] = position[0]
        self.matrix[3][1] = position[1]
        self.matrix[3][2] = position[2]

    def set_rotation(self, rotation):
        self.matrix = glm.mat4_cast(rotation)

    def set_rotation(self, axis, angle):
        if axis == [0.0, 0.0, 0.0]:
            return

        if angle == 0.0:
            return

        self.matrix = glm.rotate(glm.mat4(1.0), angle, axis)

    def set_scale(self, scale):
        self.matrix[0][0] = scale[0]
        self.matrix[1][1] = scale[1]
        self.matrix[2][2] = scale[2]

    def get_transform(self):
        return self.matrix