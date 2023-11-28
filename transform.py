import glm

class TransformMatrix():
    """
    Represents a transformation matrix used for translating, rotating, and scaling objects in 3D space.
    """

    def __init__(self):
        """
        Initializes a new instance of the TransformMatrix class.
        """
        self.matrix = glm.mat4(1.0)  # Initialize with an identity matrix

    def translate(self, translation):
        """
        Translates the matrix by the specified translation vector.

        Args:
            translation: A 3D vector representing the translation in each axis.

        Returns:
            None
        """
        translation_matrix = glm.translate(glm.mat4(1.0), translation)
        self.matrix = translation_matrix * self.matrix

    def rotate(self, rotation):
        """
        Rotates the matrix by the specified rotation quaternion.

        Args:
            rotation: A quaternion representing the rotation.

        Returns:
            None
        """
        rotation_matrix = glm.mat4_cast(rotation)
        self.matrix = rotation_matrix * self.matrix

    def rotate(self, axis, angle):
        """
        Rotates the matrix by the specified axis and angle.

        Args:
            axis: A 3D vector representing the rotation axis.
            angle: The rotation angle in radians.

        Returns:
            None
        """
        if axis == [0.0, 0.0, 0.0]:
            return

        if angle == 0.0:
            return

        rotation_matrix = glm.rotate(glm.mat4(1.0), angle, axis)
        self.matrix = rotation_matrix * self.matrix

    def scale(self, scale):
        """
        Scales the matrix by the specified scale vector.

        Args:
            scale: A 3D vector representing the scale in each axis.

        Returns:
            None
        """
        scale_matrix = glm.scale(glm.mat4(1.0), scale)
        self.matrix = scale_matrix * self.matrix

    def get_position(self):
        """
        Gets the position vector from the matrix.

        Returns:
            A 3D vector representing the position.
        """
        return glm.vec3(self.matrix[3][0], self.matrix[3][1], self.matrix[3][2])

    def get_rotation(self):
        """
        Gets the rotation quaternion from the matrix.

        Returns:
            A quaternion representing the rotation.
        """
        return glm.quat(glm.mat3(self.matrix))

    def get_scale(self):
        """
        Gets the scale vector from the matrix.

        Returns:
            A 3D vector representing the scale.
        """
        return glm.vec3(self.matrix[0][0], self.matrix[1][1], self.matrix[2][2])

    def reset(self):
        """
        Resets the matrix to an identity matrix.

        Returns:
            None
        """
        self.matrix = glm.mat4(1.0)

    def set_position(self, position):
        """
        Sets the position vector of the matrix.

        Args:
            position: A 3D vector representing the new position.

        Returns:
            None
        """
        self.matrix[3][0] = position[0]
        self.matrix[3][1] = position[1]
        self.matrix[3][2] = position[2]

    def set_rotation(self, rotation):
        """
        Sets the rotation quaternion of the matrix.

        Args:
            rotation: A quaternion representing the new rotation.

        Returns:
            None
        """
        self.matrix = glm.mat4_cast(rotation)

    def set_rotation(self, axis, angle):
        """
        Sets the rotation of the matrix by the specified axis and angle.

        Args:
            axis: A 3D vector representing the rotation axis.
            angle: The rotation angle in radians.

        Returns:
            None
        """
        if axis == [0.0, 0.0, 0.0]:
            return

        if angle == 0.0:
            return

        self.matrix = glm.rotate(glm.mat4(1.0), angle, axis)

    def set_scale(self, scale):
        """
        Sets the scale vector of the matrix.

        Args:
            scale: A 3D vector representing the new scale.

        Returns:
            None
        """
        self.matrix[0][0] = scale[0]
        self.matrix[1][1] = scale[1]
        self.matrix[2][2] = scale[2]

    def get_transform(self):
        """
        Gets the transformation matrix.

        Returns:
            The transformation matrix.
        """
        return self.matrix