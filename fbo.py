import OpenGL.GL as gl

from texture import Texture

class Framebuffer():

    def __init__(self, width, height, attachments = [gl.GL_COLOR_ATTACHMENT0], textures=None):
        self.attachments = attachments
        self.fbo = gl.glGenFramebuffers(1)
        self.width = width
        self.height = height

        if textures is not None:
            self.prepare(textures)

    def __del__(self):
        gl.glDeleteFramebuffers(1, [self.fbo])

    def bind(self):
        # deal with double binding
        if gl.glGetIntegerv(gl.GL_FRAMEBUFFER_BINDING) == self.fbo:
            return

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fbo)
        # store prev framebuffer size to reset when unbind
        self.prev_viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)        
        if list(self.prev_viewport) != [0, 0, int(self.width), int(self.height)]:
            gl.glViewport(0, 0, int(self.width), int(self.height))

    def unbind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        # reset old framebuffer viewport        
        if list(gl.glGetIntegerv(gl.GL_VIEWPORT)) != list(self.prev_viewport):
            gl.glViewport(self.prev_viewport[0], self.prev_viewport[1], self.prev_viewport[2], self.prev_viewport[3])

    def status(self):
        self.bind()
        stat = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        self.unbind()
        return stat

    def good(self):
        return self.status() == gl.GL_FRAMEBUFFER_COMPLETE

    def prepare(self, textures, targets=None, level=0):
        assert len(textures) == len(self.attachments)

        if targets is None:
            targets = [texture.target for texture in textures]

        self.bind()

        for i, texture in enumerate(textures):
            gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, self.attachments[i], targets[i], texture.textureid, level)

        self.unbind()


class FramebufferTexture(Texture):

    def __init__(self, width, height, uniform, format=gl.GL_RGBA, type=gl.GL_UNSIGNED_BYTE):
        self.name = None
        self.uniform = uniform
        self.type = type
        self.format = format
        self.wrap = gl.GL_CLAMP_TO_EDGE
        self.sample = gl.GL_LINEAR
        self.target = gl.GL_TEXTURE_2D
        self.textureid = gl.glGenTextures(1)

        self.width = width
        self.height = height

        self._bind()

        # create the texture

        gl.glTexImage2D(self.target, 0, self.format, width, height, 0, self.format, self.type, None)

        gl.glTexParameteri(self.target, gl.GL_TEXTURE_WRAP_S, self.wrap)
        gl.glTexParameteri(self.target, gl.GL_TEXTURE_WRAP_T, self.wrap)
        gl.glTexParameteri(self.target, gl.GL_TEXTURE_WRAP_R, self.wrap)

        gl.glTexParameteri(self.target, gl.GL_TEXTURE_MAG_FILTER, self.sample)
        gl.glTexParameteri(self.target, gl.GL_TEXTURE_MIN_FILTER, self.sample)

        self.unbind()