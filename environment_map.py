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

class EnvironmentShaderRefrection(EnvironmentShader):

    def __init__(self, name='environment_refract', map=None):
        EnvironmentShader.__init__(self, name=name, map=map)

        self.refractive_index_from = 1.0
        self.refractive_index_to = 1.0
        self.add_uniform('refraction_ratio')

    def bind(self, model, M):
        EnvironmentShader.bind(self, model, M)

        self.uniforms['refraction_ratio'].bind_float(self.refractive_index_from / self.refractive_index_to)

class EnvironmentMap(CubeMap):

    def __init__(self, uniform="textureObject", width=50, height=50):
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
        self._last_pos = None

        self._bind()
        for (face, fbo) in self.fbos.items():
            gl.glTexImage2D(face, 0, self.format, width, height, 0, self.format, self.type, None)
            fbo.prepare([self], [face])

            # attach the depth buffer
            fbo.attach_renderbuffer_depth()
        self.unbind()

    def update(self, scene, model):
        # if self._views is not None and self._last_pos is not None:
        #     if self._last_pos != model.M.get_position():
        #         self.calculate_camera_views(model.M.get_position())

        # else:
        #     self.calculate_camera_views(model.M.get_position())
        self.calculate_camera_views(model.M.get_position())
        
        Pscene = scene.camera._projection
        scene.camera._projection = self.P

        for (face, fbo) in self.fbos.items():
            fbo.bind()
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            
            scene.camera._view = self._views[face]
            scene.camera._camera_dirty = False

            scene.draw_reflections()

            fbo.unbind()


        scene.camera._projection = Pscene
        scene.camera._update_vectors()

        self._last_pos = model.M.get_position()

    def calculate_camera_views(self, object_position):
        # Define the transformations for each face according to the OpenGL convention
        views = {
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X: glm.lookAt(object_position, object_position + glm.vec3(1, 0, 0), glm.vec3(0, -1, 0)),
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X: glm.lookAt(object_position, object_position + glm.vec3(-1, 0, 0), glm.vec3(0, -1, 0)),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y: glm.lookAt(object_position, object_position + glm.vec3(0, 1, 0), glm.vec3(0, 0, 1)),
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: glm.lookAt(object_position, object_position + glm.vec3(0, -1, 0), glm.vec3(0, 0, -1)),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z: glm.lookAt(object_position, object_position + glm.vec3(0, 0, 1), glm.vec3(0, -1, 0)),
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: glm.lookAt(object_position, object_position + glm.vec3(0, 0, -1), glm.vec3(0, -1, 0)),
        }
        self._views = views
        self._last_pos = object_position
