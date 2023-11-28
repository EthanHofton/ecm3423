import numpy as np

import numpy as np

class CoordinateSystem:
    """
    Represents a coordinate system.
    """

    # X_SEP = 17
    # Y_SEP = 17
    X_SEP = 19
    Y_SEP = 19
    # road translation + road height
    ROAD_OFFSET = 0.1
    ROAD_HEIGHT = 0.225
    TOP_ROAD_HEIGHT = ROAD_OFFSET + ROAD_HEIGHT

    @staticmethod
    def get_world_pos(x, y):
        """
        Converts the given x and y coordinates to world position.

        Args:
            x (float): The x coordinate.
            y (float): The y coordinate.

        Returns:
            numpy.ndarray: The world position as a numpy array.
        """
        return np.array([x * CoordinateSystem.X_SEP, 0, y * CoordinateSystem.Y_SEP], 'f')