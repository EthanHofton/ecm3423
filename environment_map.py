import OpenGL.GL as gl
import numpy as np
import glm

from cube_map import CubeMap
from fbo import Framebuffer, FramebufferTexture
from shaders import BaseShaderProgram
import matutils as mu

class EnvironmentShader(BaseShaderProgram):

    def __init__(self, name='environment_reflect', map=None):
        BaseShaderProgram.__init__(self, name=name)

        self.add_uniform('env_map')
        self.add_uniform('M')
        self.add_uniform('viewPos')

        self.map = map

    def bind(self, model, M):
        BaseShaderProgram.bind(self, model, M)

        self.uniforms['M'].bind_matrix(np.array(M, dtype=np.float32))
        self.uniforms['viewPos'].bind_vector(np.array(model.scene.camera.position(), dtype=np.float32))

        num_textures = self.bind_textures(model)
        if self.map is not None:
            self.map.bind(num_textures)
            self.uniforms['env_map'].bind(num_textures)

class EnvironmentShaderRefractive(EnvironmentShader):

    def __init__(self, name='environment_refract', map=None):
        EnvironmentShader.__init__(self, name=name, map=map)

        self.refractive_index_from = 1.0
        self.refractive_index_to = 1.0
        self.add_uniform('refraction_ratio')

    def bind(self, model, M):
        EnvironmentShader.bind(self, model, M)

        self.uniforms['refraction_ratio'].bind_float(self.refractive_index_from / self.refractive_index_to)

class EnvironmentMap(CubeMap):
    """
    A class representing an environment map.

    Attributes:
        width (int): The width of the environment map.
        height (int): The height of the environment map.
        fbos (dict): A dictionary mapping each face of the cube map to its corresponding framebuffer object.
        P (numpy.ndarray): The perspective projection matrix.
        _views (dict): A dictionary mapping each face of the cube map to its corresponding camera view matrix.

    Args:
        uniform (str): The uniform name for the environment map texture.
        width (int): The width of the environment map. Default is 50.
        height (int): The height of the environment map. Default is 50.
    """

    def __init__(self, uniform="textureObject", width=50, height=50):
        """
        Initializes the EnvironmentMap object.

        Args:
            uniform (str): The uniform name for the environment map texture.
            width (int): The width of the environment map. Default is 50.
            height (int): The height of the environment map. Default is 50.
        """
        CubeMap.__init__(self, uniform)

        self.width = width
        self.height = height

        self.fbos = {
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X: Framebuffer(width, height),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z: Framebuffer(width, height),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X: Framebuffer(width, height),
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: Framebuffer(width, height),
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: Framebuffer(width, height),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y: Framebuffer(width, height)
        }
        # Define frustum parameters
        left = -1.0
        right = 1.0
        bottom = -1.0
        top = 1.0
        near = 1
        far = 100.0

        # Create the perspective projection matrix using glm.frustum
        self.P = np.array(glm.frustum(left, right, bottom, top, near, far))
        self._views = None

        self._bind()
        for (face, fbo) in self.fbos.items():
            gl.glTexImage2D(face, 0, self.format, width, height, 0, self.format, self.type, None)
            fbo.prepare([self], [face])

            # attach the depth buffer
            fbo.attach_renderbuffer_depth()
        self.unbind()

    def update(self, scene, model):
        """
        Updates the environment map based on the scene and model.

        Args:
            scene (Scene): The scene object.
            model (Model): The model object.
        """
        # calculate the camera views based on the object position
        self.calculate_camera_views(model.M.get_position())
        
        # store the old scene projection
        Pscene = scene.camera._projection
        # reset the scenes projection matrix to the environment maps frustum projection
        scene.camera._projection = self.P

        # loop though each face of the cube map
        for (face, fbo) in self.fbos.items():
            # bind the fbo for the current face (sets the viewport)
            fbo.bind()
            # clear the color and depth buffer
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            
            # set the camera view to the current face
            scene.camera._view = self._views[face]
            scene.camera._camera_dirty = False

            # draw the reflections of the scene
            scene.draw_reflections()

            # unbind the fbo (restores the viewport)
            fbo.unbind()

        # restore the scenes projection matrix
        scene.camera._projection = Pscene
        
        # reset the camera view to the original view
        scene.camera._camera_dirty = True
        scene.camera._update_vectors()

    def calculate_camera_views(self, object_position):
        """
        Calculates the camera views for each face of the cube map.

        Args:
            object_position (glm.vec3): The position of the object.
        """
        # Define the camera views for each face of the cube map
        # Use GLM look at function to face the camera in each direction of the cube map
        views = {
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X: glm.lookAt(object_position, object_position + glm.vec3(1, 0, 0), glm.vec3(0, -1, 0)),
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X: glm.lookAt(object_position, object_position + glm.vec3(-1, 0, 0), glm.vec3(0, -1, 0)),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y: glm.lookAt(object_position, object_position + glm.vec3(0, 1, 0), glm.vec3(0, 0, 1)),
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: glm.lookAt(object_position, object_position + glm.vec3(0, -1, 0), glm.vec3(0, 0, -1)),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z: glm.lookAt(object_position, object_position + glm.vec3(0, 0, 1), glm.vec3(0, -1, 0)),
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: glm.lookAt(object_position, object_position + glm.vec3(0, 0, -1), glm.vec3(0, -1, 0)),
        }
        self._views = views
