from texture import Texture
from shaders import BaseShaderProgram
from fbo import Framebuffer, FramebufferTexture
import OpenGL.GL as gl

class ShadowMappingShader(BaseShaderProgram):
    pass


class ShadowMap(FramebufferTexture):
    
    def __init__(self, width=1024, height=1024, uniform='shadowMap', name='shadow_map'):
        FramebufferTexture.__init__(self, width, height, uniform, format=gl.GL_DEPTH_COMPONENT, type=gl.GL_FLOAT)

        self.fbo = Framebuffer(width, height, [gl.GL_DEPTH_ATTACHMENT], textures=[self])
        self.fbo.no_colorbuffer()

    def update(self, scene):
        self.bind()
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        scene.draw(Framebuffer=True)

        self.unbind()