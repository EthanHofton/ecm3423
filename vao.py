import OpenGL.GL as gl
import ctypes
import numpy as np

class VertexArray:

    def __init__(self):
        """ Create a vertex array """
        self._VAO = gl.glGenVertexArrays(1)
        self._VBOs = []
        self._IBO = None
        self._index_count = 0

    def add_vertex_buffer(self, buffer):
        """ Add a vertex buffer to the vertex array """
        self.bind()
        buffer.bind()

        layout = buffer.get_layout()
        for element in layout.get_elements():
            gl.glEnableVertexAttribArray(self._index_count)
            gl.glVertexAttribPointer(self._index_count,
                                     element.get_count(),
                                     gl.GL_FLOAT,
                                     gl.GL_TRUE if element.get_normalized()
                                     else gl.GL_FALSE,
                                     layout.get_stride(),
                                     ctypes.c_void_p(element.get_offset()))
            gl.glVertexAttribDivisor(self._index_count,
                                     element.get_vertex_divisor())
            self._index_count += 1
        self._VBOs.append(buffer)

    def set_index_buffer(self, buffer):
        """ Set the index buffer of the vertex array """
        self.bind()
        buffer.bind()
        self._IBO = buffer

    def get_index_buffer(self):
        """ Return the index buffer of the vertex array """
        return self._IBO

    def get_vertex_buffers(self):
        """ Return the vertex buffers of the vertex array """
        return self._VBOs

    def get_vertex_buffer(self, index):
        """ Return the vertex buffer at the given index """
        return self._VBOs[index]

    def bind(self):
        """ Bind the vertex array """
        gl.glBindVertexArray(self._VAO)

    def unbind(self):
        """ Unbind the vertex array """
        gl.glBindVertexArray(0)

    def __del__(self):
        """ Delete the vertex array """
        gl.glDeleteVertexArrays(1, [self._VAO])

    def get_vertex_count(self):
        """ Return the vertex count of the vertex array """
        count = np.inf
        for vbo in self._VBOs:
            count = min(count, vbo.get_vertex_count())
        return count
