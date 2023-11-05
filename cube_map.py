import OpenGL.GL as gl
from texture import Texture, ImageWrapper

class CubeMap(Texture):

    def __init__(self, uniform="textureObject", name=None, files=None, wrap=gl.GL_CLAMP_TO_EDGE, sample=gl.GL_LINEAR, format=gl.GL_RGBA, type=gl.GL_UNSIGNED_BYTE, extension='jpg'):
        self.name = name
        self.format = format
        self.type = type
        self.wrap = wrap
        self.sample = sample
        self.target = gl.GL_TEXTURE_CUBE_MAP # we set the texture target as a cube map
        self.uniform = uniform

        # generate the texture.
        self.textureid = gl.glGenTextures(1)

        self.files = {
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X: f'left.{extension}',
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z: f'back.{extension}',
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X: f'right.{extension}',
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: f'front.{extension}',
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: f'bottom.{extension}',
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y: f'top.{extension}',
        }

        # bind the texture
        self._bind()

        # if name is provided, load cube faces from images on disk
        if name is not None:
            self.set(name, files)

        # set what happens for texture coordinates outside [0,1]
        gl.glTexParameteri(self.target, gl.GL_TEXTURE_WRAP_S, wrap)
        gl.glTexParameteri(self.target, gl.GL_TEXTURE_WRAP_T, wrap)

        # set how sampling from the texture is done.
        gl.glTexParameteri(self.target, gl.GL_TEXTURE_MAG_FILTER, sample)
        gl.glTexParameteri(self.target, gl.GL_TEXTURE_MIN_FILTER, sample)

        # unbind the texture
        self.unbind()

    def set(self, name, files=None):
        if files is not None:
            self.files = files

        self.name = name
        
        self._bind()
        
        for (key, value) in self.files.items():
            print('Loading texture: texture/{}/{}'.format(name, value))
            img = ImageWrapper('{}/{}'.format(name, value))

            # convert the python image object to a plain byte array for passsing to OpenGL
            gl.glTexImage2D(key, 0, self.format, img.width(), img.height(), 0, self.format, self.type, img.data(self.format))

    def update(self, scene):
        pass