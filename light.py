import numpy as np

class LightSource:
    '''
    Base class for maintaining a light source in the scene. Inheriting from Sphere allows to visualize the light
    source position easily.
    '''
    def __init__(self, position=[2.,2.,0.], Ia=[0.2,0.2,0.2], Id=[0.9,0.9,0.9], Is=[1.0,1.0,1.0], constant=1.0, linear=0.7, quadratic=1.8, intensity=1.0):
        self.position = np.array(position, 'f')
        self.Ia = Ia
        self.Id = Id
        self.Is = Is
        self.constant = constant
        self.linear = linear
        self.quadratic = quadratic
        self.intensity = intensity

class DirectionalLight():
    '''
    A directional light source. It is assumed that the light source is at infinity.
    '''
    def __init__(self, direction=[-1.,-1.,0.], Ia=[0.2,0.2,0.2], Id=[0.9,0.9,0.9], Is=[0.5,0.5,0.5]):
        '''
        :param direction: The direction of the light source
        :param Ia: The ambiant illumination it provides (may not be dependent on the light source itself)
        :param Id: The diffuse illumination
        :param Is: The specular illumination
        :param visible: Whether the light should be represented as a sphere in the scene (default: False)
        '''
        self.direction = np.array(direction, 'f')
        self.Ia = Ia
        self.Id = Id
        self.Is = Is

class SpotLight:
    pass