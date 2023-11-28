class Material:
    """
    Represents a material used in computer graphics.

    Attributes:
        name (str): The name of the material.
        Ka (list): The ambient color of the material as a list of RGB values.
        Kd (list): The diffuse color of the material as a list of RGB values.
        Ks (list): The specular color of the material as a list of RGB values.
        Ns (float): The shininess of the material.
        map_Kd (str): The file path to the diffuse texture map.
        map_Ks (str): The file path to the specular texture map.
        map_bump (str): The file path to the bump texture map.
        map_Ns (str): The file path to the shininess texture map.
        alpha (float): The alpha (transparency) value of the material.
    """

    def __init__(self, name=None, Ka=[1.,1.,1.], Kd=[1.,1.,1.], Ks=[1.,1.,1.], Ns=10.0, map_Kd=None, map_Ks=None, map_bump=None, map_Ns=None):
        self.name = name
        self.Ka = Ka
        self.Kd = Kd
        self.Ks = Ks
        self.Ns = Ns
        self.map_Kd = map_Kd
        self.map_Ks = map_Ks
        self.map_bump = map_bump
        self.map_Ns = map_Ns
        self.alpha = 1.0