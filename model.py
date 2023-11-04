import OpenGL.GL as gl
from transform import TransformMatrix
from vao import VertexArray
from vbo import VertexBuffer, BufferLayout, BufferElement, BufferType
from ibo import IndexBuffer
from texture import Texture
from shaders import PhongShader
import numpy as np

class BaseModel():

    def __init__(self, scene, mesh=None,primative=gl.GL_TRIANGLES,visable=True):

        self.visable = visable

        self.scene = scene

        self.primative = primative

        self.shader = None

        self.mesh = mesh
        self.name = self.mesh.name

        self.M = TransformMatrix()

        self.vao = VertexArray()
        self.ibo = None

        self.vbos = {}
        self.attributes = {}

    def bind_shader(self, shader):
        if self.shader is None or self.shader.name is not shader:
            if isinstance(shader, str):
                self.shader = PhongShader(shader)
            else:
                self.shader = shader

            # bind all attributes and compile the shader
            self.shader.compile(self.attributes)

    def bind(self):
        self.vao.bind()

        if self.mesh is None:
            print('Warning - binding model with no mesh')

        if self.mesh.vertices is None:
            print("Warning - binding mesh with no vertices")

        self.init_vbo('position', self.mesh.vertices)
        self.init_vbo('normal', self.mesh.normals)
        self.init_vbo('color', self.mesh.colors)
        self.init_vbo('texCoord', self.mesh.textureCoords)
        self.init_vbo('tangent', self.mesh.tangents)
        self.init_vbo('binormal', self.mesh.binormals)

        if self.mesh.material.texture is not None:
            if isinstance(self.mesh.material.texture, str):
                self.mesh.material.texture = Texture(self.mesh.material.texture)

        if self.mesh.faces is not None:
            self.ibo = IndexBuffer(self.mesh.faces)
            self.vao.set_index_buffer(self.ibo)

        self.vao.unbind()

    def init_vbo(self, name, data):

        if data is None:
            return

        if data.shape[1] == 1:
            buffer_type = BufferType.FLOAT_1
        elif data.shape[1] == 2:
            buffer_type = BufferType.FLOAT_2
        elif data.shape[1] == 3:
            buffer_type = BufferType.FLOAT_3
        elif data.shape[1] == 4:
            buffer_type = BufferType.FLOAT_4
        else:
            buffer_type = BufferType.FLOAT_3

        self.vbos[name] = VertexBuffer(data)
        self.vbos[name].set_layout(BufferLayout([
            BufferElement(buffer_type)
        ]))

        self.attributes[name] = self.vao._index_count
        self.vao.add_vertex_buffer(self.vbos[name])

    def draw(self, M=TransformMatrix()):
        if self.visable:

            self.vao.bind()

            self.shader.bind(
                model=self,
                M=np.matmul(np.array(M.get_transform()), np.array(self.M.get_transform()))
            )

            if self.ibo is None:
                gl.glDrawArrays(self.primative, 0, self.mesh.vertices.shape[0])
            else:
                gl.glDrawElements(self.primative, self.mesh.faces.flatten().shape[0], gl.GL_UNSIGNED_INT, None)

            self.vao.unbind()


class ModelFromMesh(BaseModel):

    def __init__(self, scene, mesh, name=None, shader=None, visable=True):
        BaseModel.__init__(self, scene=scene, mesh=mesh, visable=visable)

        if name is not None:
            self.name = name

        if self.mesh.faces.shape[1] == 3:
            self.primative = gl.GL_TRIANGLES

        elif self.mesh.faces.shape[1] == 4:
            self.primative = gl.GL_QUADS

        self.bind()

        if shader is not None:
            self.bind_shader(shader)
