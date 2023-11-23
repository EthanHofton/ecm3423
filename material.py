class Material:
    def __init__(self, name=None, Ka=[1.,1.,1.], Kd=[1.,1.,1.], Ks=[1.,1.,1.], Ns=10.0, map_Kd=None, map_Ks=None, map_bump=None):
        self.name = name
        self.Ka = Ka
        self.Kd = Kd
        self.Ks = Ks
        self.Ns = Ns
        self.map_Kd = map_Kd
        self.map_Ks = map_Ks
        self.map_bump = map_bump
        self.alpha = 1.0

class MaterialLibrary:
    def __init__(self):
        self.materials = []
        self.names = {}

    def add_material(self, material):
        self.names[material.name] = len(self.materials)
        self.materials.append(material)