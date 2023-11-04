import OpenGL.GL as gl

class IndexBuffer:

    def __init__(self, data=None, buffer_size=None):
        """ Create an index buffer with the given data """
        self._count = len(data)
        self._buffer = gl.glGenBuffers(1)

        if data is not None:
            buffer_size = len(data) * 4
        else:
            if buffer_size is None:
                raise Exception("Index buffer requires either data or buffer size")

        self.bind()
        
        if data is None:
            gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, buffer_size,
                        None, gl.GL_DYNAMIC_DRAW)
        else:
            gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, data.flatten(), gl.GL_STATIC_DRAW)

    def __del__(self):
        """ Delete the index buffer """
        if self._buffer:
            gl.glDeleteBuffers(1, [self._buffer])
            self._buffer = None

    def bind(self):
        """ Bind the index buffer """
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._buffer)

    def unbind(self):
        """ Unbind the index buffer """
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

    def update(self, data):
        """ Update the index buffer with the given data """
        if data is None:
            return

        self._count = len(data)

        self.bind()
        gl.glBufferSubData(gl.GL_ELEMENT_ARRAY_BUFFER, 0, len(data) * 4, data.flatten())
        self.unbind()

    def get_count(self):
        """ Return the count of the index buffer """
        return self._count
