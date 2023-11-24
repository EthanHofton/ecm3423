import random
import os
import numpy as np

from towers import Towers
from model import ModelFromObjInstanced
from shaders import PhongShaderInstanced

class CityMap:
    def __init__(self, b_n, building_type):
        self.b_n = b_n
        self.n = (self.b_n * 3) + 1
        self.map = [[0] * self.n for _ in range(self.n)]
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
                            self.map[x][y] = 0  # Road
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

    def print_map(self):
        for row in self.map:
            print(row)

    def generate_city(self, building_pack, road_model_file, scene):
        towers = self._get_buildings(building_pack, scene)
        road_count = np.count_nonzero(np.array(self.map) == 0)
        road_shader = PhongShaderInstanced()
        roads = ModelFromObjInstanced(scene, road_model_file, shader=road_shader, num_instances=road_count)
        print("========= Generating city... =========")
        print("Road count:", road_count)
        print("Building count:", self.buildings_count)
        print("Building type count:", self.building_type)
        print("City map:")
        self.print_map()

        print("========= Adding roads and buildings... =========")

        for i in range(self.n):
            for j in range(self.n):
                if self.map[i][j] != 0:
                    print(f"Adding tower at {i}, {j} with type {self.map[i][j]}")
                    towers[self.map[i][j] - 1].add_tower(i, j)
                else:
                    print(f"Adding road at {i}, {j}")
                    road_shader.add_offset(np.array([i * 20, 0, j * 20]))

        return towers, roads

    def _get_buildings(self, building_pack, scene):
        objs = []
        for file in os.listdir(f"models/{building_pack}/"):
            if file.endswith(".obj"):
                objs.append(f"{building_pack}/{file}")

        towers = []

        for index, obj in enumerate(objs):
            tower = Towers(scene, obj, num_instances=self.building_counts[index])
            self.index_to_building[index] = tower
            towers.append(tower)

        return towers


if __name__ == "__main__":
    # Example usage
    city = CityMap(3, 1)
    city.print_map()