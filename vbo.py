import OpenGL.GL as gl
from enum import Enum

class BufferType(Enum):
    FLOAT_1 = 0
    FLOAT_2 = 1
    FLOAT_3 = 2
    FLOAT_4 = 3
    INT_1 = 4
    INT_2 = 5
    INT_3 = 6
    INT_4 = 7
    BOOL_1 = 8
    MATF_3 = 9
    MATF_4 = 10

class BufferElement:

    def __init__(self,
                 type: BufferType,
                 normalized=False,
                 vertex_divisor=0):
        """ Create a buffer element with the given type """
        self._type = type
        self._normalized = normalized
        self._vertex_divisor = vertex_divisor
        self._offset = 0

        if type == BufferType.FLOAT_1:
            self._count = 1
            self._size = 4
        elif type == BufferType.FLOAT_2:
            self._count = 2
            self._size = 4 * 2
        elif type == BufferType.FLOAT_3:
            self._count = 3
            self._size = 4 * 3
        elif type == BufferType.FLOAT_4:
            self._count = 4
            self._size = 4 * 4
        elif type == BufferType.INT_1:
            self._count = 1
            self._size = 4
        elif type == BufferType.INT_2:
            self._count = 2
            self._size = 4 * 2
        elif type == BufferType.INT_3:
            self._count = 3
            self._size = 4 * 3
        elif type == BufferType.INT_4:
            self._count = 4
            self._size = 4 * 4
        elif type == BufferType.BOOL_1:
            self._count = 1
            self._size = 1
        elif type == BufferType.MATF_3:
            self._count = 1
            self._size = 36
        elif type == BufferType.MATF_4:
            self._count = 1
            self._size = 64

    def get_type(self):
        """ Return the type of the buffer element """
        return self._type

    def get_count(self):
        """ Return the count of the buffer element """
        return self._count

    def get_normalized(self):
        """ Return whether the buffer element is normalized """
        return self._normalized

    def get_vertex_divisor(self):
        """ Return the vertex divisor of the buffer element """
        return self._vertex_divisor

    def get_size(self):
        """ Return the size of the buffer element """
        return self._size

    def set_offset(self, offset):
        """ Set the offset of the buffer element """
        self._offset = offset

    def get_offset(self):
        """ Return the offset of the buffer element """
        return self._offset


class BufferLayout:

    def __init__(self, elements: list):
        """ Create a buffer layout with the given elements """
        self._elements = elements
        self._stride = 0
        offset = 0
        for element in elements:
            self._stride += element.get_size()
            element.set_offset(offset)
            offset += element.get_size()

    def get_elements(self):
        """ Return the elements of the buffer layout """
        return self._elements

    def get_stride(self):
        """ Return the stride of the buffer layout """
        return self._stride


class VertexBuffer:

    def __init__(self, data=None, buffer_size=10000):
        """ Create a vertex buffer with the given data """
        self._VBO = gl.glGenBuffers(1)

        self.bind()
        if data is not None:
            gl.glBufferData(gl.GL_ARRAY_BUFFER, data, gl.GL_STATIC_DRAW)
            self._data_size = len(data)
        else:
            gl.glBufferData(gl.GL_ARRAY_BUFFER, buffer_size,
                        None, gl.GL_DYNAMIC_DRAW)
            self.update(data)

    def __del__(self):
        """ Delete the vertex buffer """
        gl.glDeleteBuffers(1, [self._VBO])

    def set_layout(self, layout):
        """ Set the layout of the vertex buffer """
        self._layout = layout

        total_count = 0
        for elem in layout.get_elements():
            total_count += elem.get_count()

        self._layout_count = total_count

    def get_layout(self):
        """ Return the layout of the vertex buffer """
        return self._layout

    def update(self, data):
        """ Update the vertex buffer with the given data """
        self._data_size = 0        

        if data is None:
            return

        self._data_size = len(data)

        self.bind()
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, len(data) * 4,
                           data.flatten())
        self.unbind()

    def bind(self):
        """ Bind the vertex buffer """
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._VBO)

    def unbind(self):
        """ Unbind the vertex buffer """
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def get_vertex_count(self):
        """ Return the vertex count of the vertex buffer """
        return self._data_size // self._layout_count
