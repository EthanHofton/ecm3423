import OpenGL.GL as gl
import numpy as np
import glm

from cube_map import CubeMap
from fbo import Framebuffer, FramebufferTexture
from shaders import BaseShaderProgram
import matutils as mu

class EnvironmentShader(BaseShaderProgram):

    def __init__(self, name='environment', map=None):
        BaseShaderProgram.__init__(self, name=name)

        self.add_uniform('VM')
        self.add_uniform('VMiT')
        self.add_uniform('VT')
        self.add_uniform('env_map')

        self.map = map

    def bind(self, model, M):
        gl.glUseProgram(self.program)

        P = model.scene.camera.projection()  # get projection matrix from the scene
        V = model.scene.camera.view()  # get view matrix from the camera

        self.uniforms['PVM'].bind(np.matmul(P, np.matmul(V, M)))

        # set the PVM matrix uniform
        self.uniforms['VM'].bind(np.matmul(V, M))

        # set the PVM matrix uniform
        self.uniforms['VMiT'].bind(np.linalg.inv(np.matmul(V, M))[:3, :3].transpose())

        V = np.array(V)
        V.reshape(4,4)
        self.uniforms['VT'].bind(V.transpose()[:3, :3])

        num_textures = self.bind_textures(model)
        if self.map is not None:
            self.map.bind(num_textures)
            self.uniforms['env_map'].bind(num_textures)

class EnvironmentMap(CubeMap):

    def __init__(self, uniform="textureObject", width=50, height=50):
        CubeMap.__init__(self, uniform)

        self.width = width
        self.height = height

        self.fbos = {
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X: Framebuffer(width, height, [gl.GL_COLOR_ATTACHMENT0, gl.GL_COLOR_ATTACHMENT0]),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X: Framebuffer(width, height, [gl.GL_COLOR_ATTACHMENT0, gl.GL_COLOR_ATTACHMENT0]),
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: Framebuffer(width, height, [gl.GL_COLOR_ATTACHMENT0, gl.GL_COLOR_ATTACHMENT0]),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y: Framebuffer(width, height, [gl.GL_COLOR_ATTACHMENT0, gl.GL_COLOR_ATTACHMENT0]),
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: Framebuffer(width, height, [gl.GL_COLOR_ATTACHMENT0, gl.GL_COLOR_ATTACHMENT0]),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z: Framebuffer(width, height, [gl.GL_COLOR_ATTACHMENT0, gl.GL_COLOR_ATTACHMENT0])
        }
        self.P = np.array(glm.frustum(-1, +1, -1, +1, 1, 20))
        self.views = self.calculate_camera_views()

        self.textures = []

        self._bind()
        for (face, fbo) in self.fbos.items():
            gl.glTexImage2D(face, 0, self.format, width, height, 0, self.format, self.type, None)
            self.textures.append(FramebufferTexture(width, height, str(face)))
            fbo.prepare([self, self.textures[-1]], [face, self.textures[-1].target])
        self.unbind()

    def update(self, scene):
        Pscene = scene.camera._projection
        scene.camera._projection = self.P

        for (face, fbo) in self.fbos.items():
            fbo.bind()
            
            scene.camera._view = self.views[face]

            scene.draw_reflections()

            fbo.unbind()


        scene.camera._projection = Pscene
        scene.camera._update_vectors()

    def calculate_camera_views(self):
        t = 0
        return {
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X: np.matmul(mu.translationMatrix([0, 0, t]), mu.rotationMatrixY(+np.pi/2.0)),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X: np.matmul(mu.translationMatrix([0, 0, t]), mu.rotationMatrixY(-np.pi/2.0)),
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: np.matmul(mu.translationMatrix([0, 0, t]), mu.rotationMatrixX(-np.pi/2.0)),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y: np.matmul(mu.translationMatrix([0, 0, t]), mu.rotationMatrixX(+np.pi/2.0)),
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: np.matmul(mu.translationMatrix([0, 0, t]), mu.rotationMatrixY(+np.pi)),
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z: mu.translationMatrix([0, 0, t]),
        }