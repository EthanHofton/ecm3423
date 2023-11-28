import numpy as np

class CoordinateSystem:

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
        return np.array([x * CoordinateSystem.X_SEP, 0, y * CoordinateSystem.Y_SEP], 'f')