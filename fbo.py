import OpenGL.GL as gl

from texture import Texture

class Framebuffer():
    """
    A class representing a framebuffer object in computer graphics.

    Args:
        width (int): The width of the framebuffer.
        height (int): The height of the framebuffer.
        attachments (list, optional): The list of attachments to be used with the framebuffer. Defaults to [gl.GL_COLOR_ATTACHMENT0].
        textures (list, optional): The list of textures to be used with the framebuffer. Defaults to None.

    Attributes:
        attachments (list): The list of attachments used with the framebuffer.
        fbo (int): The framebuffer object ID.
        width (int): The width of the framebuffer.
        height (int): The height of the framebuffer.
        depthbuffer (int, optional): The depth buffer ID. Defaults to None.
        stencilbuffer (int, optional): The stencil buffer ID. Defaults to None.
        depthstencilbuffer (int, optional): The depth-stencil buffer ID. Defaults to None.
        prev_viewport (list): The previous viewport size.

    """

    def __init__(self, width, height, attachments=[gl.GL_COLOR_ATTACHMENT0], textures=None):
        """
        Initializes a Framebuffer object.

        Args:
            width (int): The width of the framebuffer.
            height (int): The height of the framebuffer.
            attachments (list, optional): The list of attachments to be used with the framebuffer. Defaults to [gl.GL_COLOR_ATTACHMENT0].
            textures (list, optional): The list of textures to be used with the framebuffer. Defaults to None.
        """

        self.attachments = attachments
        self.fbo = gl.glGenFramebuffers(1)
        self.width = width
        self.height = height

        self.depthbuffer = None
        self.stencilbuffer = None
        self.depthstencilbuffer = None

        if textures is not None:
            self.prepare(textures)

    def __del__(self):
        """
        Deletes the Framebuffer object and its associated resources.
        """

        gl.glDeleteFramebuffers(1, [self.fbo])
        if self.depthbuffer is not None:
            gl.glDeleteRenderbuffers(1, [self.depthbuffer])
        if self.stencilbuffer is not None:
            gl.glDeleteRenderbuffers(1, [self.stencilbuffer])
        if self.depthstencilbuffer is not None:
            gl.glDeleteRenderbuffers(1, [self.depthstencilbuffer])

    def bind(self):
        """
        Binds the framebuffer object.
        """

        # deal with double binding
        if gl.glGetIntegerv(gl.GL_FRAMEBUFFER_BINDING) == self.fbo:
            return

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fbo)
        # store prev framebuffer size to reset when unbind
        self.prev_viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
        if list(self.prev_viewport) != [0, 0, int(self.width), int(self.height)]:
            gl.glViewport(0, 0, int(self.width), int(self.height))

    def unbind(self):
        """
        Unbinds the framebuffer object.
        """

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        # reset old framebuffer viewport
        if list(gl.glGetIntegerv(gl.GL_VIEWPORT)) != list(self.prev_viewport):
            gl.glViewport(self.prev_viewport[0], self.prev_viewport[1], self.prev_viewport[2], self.prev_viewport[3])

    def status(self):
        """
        Checks the status of the framebuffer object.

        Returns:
            int: The status of the framebuffer object.
        """

        self.bind()
        stat = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        self.unbind()
        return stat

    def good(self):
        """
        Checks if the framebuffer object is complete.

        Returns:
            bool: True if the framebuffer object is complete, False otherwise.
        """

        return self.status() == gl.GL_FRAMEBUFFER_COMPLETE

    def prepare(self, textures, targets=None, level=0):
        """
        Prepares the framebuffer object with the given textures.

        Args:
            textures (list): The list of textures to be used with the framebuffer.
            targets (list, optional): The list of targets for each texture. Defaults to None.
            level (int, optional): The mipmap level. Defaults to 0.

        Raises:
            AssertionError: If the number of textures and attachments do not match.
        """

        assert len(textures) == len(self.attachments)

        if targets is None:
            targets = [texture.target for texture in textures]

        self.bind()

        for i, texture in enumerate(textures):
            gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, self.attachments[i], targets[i], texture.textureid, level)

        self.unbind()

    def attach_renderbuffer_depth(self):
        """
        Attaches a depth renderbuffer to the framebuffer object.
        """

        self.bind()

        depthbuffer = gl.glGenRenderbuffers(1)
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, depthbuffer)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT, self.width, self.height)
        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, gl.GL_RENDERBUFFER, depthbuffer)

        self.unbind()

    def attach_renderbuffer_stencil(self):
        """
        Attaches a stencil renderbuffer to the framebuffer object.
        """

        self.bind()

        stencilbuffer = gl.glGenRenderbuffers(1)
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, stencilbuffer)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_STENCIL_INDEX, self.width, self.height)
        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_STENCIL_ATTACHMENT, gl.GL_RENDERBUFFER, stencilbuffer)

        self.unbind()

    def attach_renderbuffer_depthstencil(self):
        """
        Attaches a depth-stencil renderbuffer to the framebuffer object.
        """

        self.bind()

        depthstencilbuffer = gl.glGenRenderbuffers(1)
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, depthstencilbuffer)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH24_STENCIL8, self.width, self.height)
        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_STENCIL_ATTACHMENT, gl.GL_RENDERBUFFER, depthstencilbuffer)

        self.unbind()

    def no_colorbuffer(self):
        """
        Disables the color buffer for the framebuffer object.
        """

        self.bind()

        gl.glDrawBuffer(gl.GL_NONE)
        gl.glReadBuffer(gl.GL_NONE)

        self.unbind()


class FramebufferTexture(Texture):
    """
    Represents a texture used in a framebuffer object.

    Args:
        width (int): The width of the texture.
        height (int): The height of the texture.
        uniform (str): The uniform name used to bind the texture in shaders.
        format (int, optional): The format of the texture. Defaults to gl.GL_RGBA.
        type (int, optional): The data type of the texture. Defaults to gl.GL_UNSIGNED_BYTE.

    Attributes:
        name (str): The name of the texture.
        uniform (str): The uniform name used to bind the texture in shaders.
        type (int): The data type of the texture.
        format (int): The format of the texture.
        wrap (int): The texture wrap mode.
        sample (int): The texture sample mode.
        target (int): The texture target.
        textureid (int): The ID of the texture.
        width (int): The width of the texture.
        height (int): The height of the texture.
    """

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