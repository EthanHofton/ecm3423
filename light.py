import numpy as np

class LightSource:
    '''
    A point light source.
    '''
    def __init__(self, position=[2.,2.,0.], Ia=[0.2,0.2,0.2], Id=[0.9,0.9,0.9], Is=[1.0,1.0,1.0], constant=1.0, 
                linear=0.7, quadratic=1.8, intensity=1.0):
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
    '''
    A spot light source
    '''

    def __init__(self, position=[0., 0., 0.], direction=[0., 0., 0.], Ia=[0.2, 0.2, 0.2], Id=[0.9, 0.9, 0.9],
                 Is=[0.5, 0.5, 0.5], constant=1.0, linear=0.045, quadratic=0.007, intensity=1.0, cutoff=12.5, outer_cutoff=17.5):
        '''
        :param position: The position of the light source
        :param direction: The spot direction of the light source
        :param Ia: The ambiant illumination it provides (may not be dependent on the light source itself)
        :param Id: The diffuse illumination
        :param Is: The specular illumination

        :param constant: The constant attenuation factor
        :param linear: The linear attenuation factor
        :param quadratic: The quadratic attenuation factor
        :param intensity: The intensity of the light source

        :param cutoff: The cutoff angle of the light source
        :param outer_cutoff:  The outer cutoff angle, used to create a soft edge
        angles in radians
        '''
        self.position = np.array(position, 'f')
        self.direction = np.array(direction, 'f')
        self.Ia = Ia
        self.Id = Id
        self.Is = Is

        self.constant = constant
        self.linear = linear
        self.quadratic = quadratic
        self.intensity = intensity

        self.cutoff = cutoff
        self.outer_cutoff = outer_cutoff