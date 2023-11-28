import random
import os
import numpy as np

from towers import Towers
from model import ModelFromObjInstanced
from shaders import PhongShaderInstanced
from coordinate_system import CoordinateSystem

class CityMap:
    def __init__(self, b_n, building_type):
        self.b_n = b_n
        self.n = (self.b_n * 3) + 1
        self.map = [[0] * self.n for _ in range(self.n)]

        # positions of the roads, intersections and buildings
        self.road_positions = []
        self.intersection_positions = []
        self.building_positions = []

        self.building_type = building_type
        self.index_to_building = {}
        self.fill_buildings()

    def fill_buildings(self):
        block_size = self.n // self.b_n
        road_width = 1
        self.buildings_count = self.b_n * self.b_n * self.building_type
        self.building_counts = [0] * self.building_type

        for i in range(self.b_n):
            for j in range(self.b_n):
                for x in range(i * block_size, (i + 1) * block_size):
                    for y in range(j * block_size, (j + 1) * block_size):
                        if x % block_size < road_width or y % block_size < road_width:
                            self.map[x][y] = 0
                        else:
                            if self.building_type == 1:
                                self.map[x][y] = 1  # Building type 1
                                self.building_counts[0] += 1
                            else:
                                # Randomize the building type while maintaining the count
                                while True:
                                    random_building_type = random.randint(1, self.building_type)
                                    if self.building_counts[random_building_type - 1] < self.buildings_count:
                                        self.map[x][y] = random_building_type
                                        self.building_counts[random_building_type - 1] += 1
                                        break

        map_copy = self.map.copy()
        for i in range(len(map_copy)):
            for j in range(len(map_copy) - 1):
                if map_copy[i][j] == 0 and map_copy[i][j + 1] != 0:
                    self.map[i][j] = -1
                if j == len(map_copy[i]) - 2 and map_copy[i][j] != 0:
                    self.map[i][j + 1] = -1

    def print_map(self):
        for row in self.map:
            print(row)

    def generate_city(self, building_pack, road_model_file, road_model_horez_file, scene):
        towers = self._get_buildings(building_pack, scene)

        vertical_road_shader = PhongShaderInstanced('phong_instanced_normal_map')
        vertical_road_count = np.count_nonzero(np.array(self.map) == 0)
        vertical_roads = ModelFromObjInstanced(scene, road_model_file, shader=vertical_road_shader, num_instances=vertical_road_count)
        vertical_roads.M.translate([0, CoordinateSystem.ROAD_OFFSET, 0])
        vertical_roads.M.scale([CoordinateSystem.X_SEP + 2, 1, CoordinateSystem.Y_SEP])

        horizontal_road_shader = PhongShaderInstanced('phong_instanced_normal_map')
        horizontal_road_count = np.count_nonzero(np.array(self.map) == -1)
        horizontal_roads = ModelFromObjInstanced(scene, road_model_horez_file, shader=horizontal_road_shader, num_instances=horizontal_road_count)
        # add a small offset to the horizontal roads to avoid z-fighting/ gap between intersecting roads
        horizontal_roads.M.translate([0, CoordinateSystem.ROAD_OFFSET , 0])
        horizontal_roads.M.scale([CoordinateSystem.X_SEP, 1, CoordinateSystem.Y_SEP])

        print("========= Generating city... =========")
        print("Vertical Road count:", vertical_road_count)
        print("Horizontal Road count:", horizontal_road_count)
        print("Building count:", self.buildings_count)
        print("Building type count:", self.building_type)
        print("City map:")
        self.print_map()

        print("========= Adding roads and buildings... =========")
        def check_intersection(i, j):
            if i % 3 == 0 and j % 3 == 0:
                return True
            return False

        for i in range(self.n):
            road_positions = []
            intersection_positions = []
            building_positions = []

            for j in range(self.n):
                # remap i and j to -n/2 to n/2
                i_remapped = i - self.n // 2
                j_remapped = j - self.n // 2
                if self.map[i][j] != 0:
                    if self.map[i][j] == -1:
                        road_positions.append((i_remapped, j_remapped))
                        if check_intersection(i, j):
                            intersection_positions.append((i_remapped, j_remapped))

                        horizontal_road_shader.add_offset(CoordinateSystem.get_world_pos(i_remapped, j_remapped))
                    else:
                        building_positions.append((i_remapped, j_remapped))
                        towers[self.map[i][j] - 1].add_tower(i_remapped, j_remapped)
                else:
                    road_positions.append((i_remapped, j_remapped))
                    if check_intersection(i, j):
                        intersection_positions.append((i_remapped, j_remapped))
                    
                    vertical_road_shader.add_offset(CoordinateSystem.get_world_pos(i_remapped, j_remapped)) 
                
            self.road_positions.append(road_positions)
            self.intersection_positions.append(intersection_positions)
            self.building_positions.append(building_positions)

        print("========= Done =========")

        return towers, vertical_roads, horizontal_roads

    def get_random_intersection(self, blacklist=[], depth=0):
        if depth > 900:
            return None

        if len(self.intersection_positions) == 0:
            return None

        random_x = random.randint(0, len(self.intersection_positions) - 1)

        # dont allow edge intersections
        if random_x == len(self.intersection_positions) - 1:
            return self.get_random_intersection(blacklist=blacklist, depth=depth + 1)
        
        if len(self.intersection_positions[random_x]) == 0:
            return self.get_random_intersection(blacklist=blacklist, depth=depth + 1)

        random_y = random.randint(0, len(self.intersection_positions[random_x]) - 1)

        if len(self.intersection_positions[random_x][random_y]) == 0:
            return self.get_random_intersection(blacklist=blacklist, depth=depth + 1)
        
        # dont allow edge intersections
        if random_y == len(self.intersection_positions[random_x]) - 1:
            return self.get_random_intersection(blacklist=blacklist, depth=depth + 1)

        if self.intersection_positions[random_x][random_y] in blacklist:
            return self.get_random_intersection(blacklist=blacklist, depth=depth + 1)

        return self.intersection_positions[random_x][random_y]

    def _get_buildings(self, building_pack, scene):
        objs = []
        for file in os.listdir(f"models/{building_pack}/"):
            if file.endswith(".obj"):
                objs.append(f"{building_pack}/{file}")
                if len(objs) == self.building_type:
                    break

        towers = []

        for index, obj in enumerate(objs):
            tower = Towers(scene, obj, num_instances=self.building_counts[index])
            self.index_to_building[index] = tower
            towers.append(tower)

        return towers


if __name__ == "__main__":
    # Example usage
    city = CityMap(3, 5)
    city.print_map()