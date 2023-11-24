import OpenGL.GL as gl
from transform import TransformMatrix
from vao import VertexArray
from vbo import VertexBuffer, BufferLayout, BufferElement, BufferType
from ibo import IndexBuffer
from texture import Texture
from shaders import PhongShader
from model_loader import ModelLoader
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

        if self.mesh.material.map_Kd is not None:
            if isinstance(self.mesh.material.map_Kd, str):
                self.mesh.material.map_Kd = Texture(self.mesh.material.map_Kd)
        
        if self.mesh.material.map_Ks is not None:
            if isinstance(self.mesh.material.map_Ks, str):
                self.mesh.material.map_Ks = Texture(self.mesh.material.map_Ks)

        if self.mesh.material.map_bump is not None:
            if isinstance(self.mesh.material.map_bump, str):
                self.mesh.material.map_bump = Texture(self.mesh.material.map_bump)

        if self.mesh.material.map_Ns is not None:
            if isinstance(self.mesh.material.map_Ns, str):
                self.mesh.material.map_Ns = Texture(self.mesh.material.map_Ns)

        if self.mesh.textures is not None:
            for texture in self.mesh.textures:
                if isinstance(texture, str):
                    texture = Texture(texture)

        if self.mesh.faces is not None:
            self.ibo = IndexBuffer(self.mesh.faces)
            self.vao.set_index_buffer(self.ibo)

        self.vao.unbind()

    def update(self):
        self.vao.bind()

        self.update_vbo('position', self.mesh.vertices)
        self.update_vbo('normal', self.mesh.normals)
        self.update_vbo('color', self.mesh.colors)
        self.update_vbo('texCoord', self.mesh.textureCoords)
        self.update_vbo('tangent', self.mesh.tangents)
        self.update_vbo('binormal', self.mesh.binormals)


    def update_vbo(self, name, data):
        if name in self.vbos:
            self.vbos[name].update(data)
        else:
            self.init_vbo(name, data)

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

            if M == TransformMatrix():
                self.shader.bind(
                    model=self,
                    M=np.array(self.M.get_transform())
                )
            else:
                self.shader.bind(
                    model=self,
                    M=np.matmul(np.array(M.get_transform()), np.array(self.M.get_transform()))
                )

            if self.ibo is None:
                gl.glDrawArrays(self.primative, 0, self.mesh.vertices.shape[0])
            else:
                gl.glDrawElements(self.primative, self.mesh.faces.flatten().shape[0], gl.GL_UNSIGNED_INT, None)

            self.vao.unbind()

class InstancedModel(BaseModel):

    def __init__(self, scene, num_instances, mesh=None, primative=gl.GL_TRIANGLES, visable=True):
        self.num_instances = num_instances
        BaseModel.__init__(self, scene=scene, mesh=mesh, primative=primative, visable=visable)

    def draw(self, M=TransformMatrix()):
        if self.visable:
            self.vao.bind()
            if M == TransformMatrix():
                self.shader.bind(
                    model=self,
                    M=np.array(self.M.get_transform())
                )
            else:
                self.shader.bind(
                    model=self,
                    M=np.matmul(np.array(M.get_transform()), np.array(self.M.get_transform()))
                )

            if self.ibo is None:
                gl.glDrawArraysInstanced(self.primative, 0, self.mesh.vertices.shape[0], self.num_instances)
            else:
                gl.glDrawElementsInstanced(self.primative, self.mesh.faces.flatten().shape[0], gl.GL_UNSIGNED_INT, None, self.num_instances)

            self.vao.unbind()

class ModelFromMesh(BaseModel):

    def __init__(self, scene, mesh, name=None, shader=None, visable=True):
        BaseModel.__init__(self, scene=scene, mesh=mesh, visable=visable)

        if name is not None:
            self.name = name

        if self.mesh.faces is not None:
            if self.mesh.faces.shape[1] == 3:
                self.primative = gl.GL_TRIANGLES

            elif self.mesh.faces.shape[1] == 4:
                self.primative = gl.GL_QUADS
        else:
            self.primative = gl.GL_TRIANGLES

        self.bind()

        if shader is not None:
            self.bind_shader(shader)

class ModelFromMeshInstanced(InstancedModel):

    def __init__(self, scene, mesh, name=None, shader=None, visable=True, num_instances=100):
        InstancedModel.__init__(self, scene=scene, mesh=mesh, visable=visable, num_instances=num_instances)

        if name is not None:
            self.name = name

        if self.mesh.faces is not None:
            if self.mesh.faces.shape[1] == 3:
                self.primative = gl.GL_TRIANGLES

            elif self.mesh.faces.shape[1] == 4:
                self.primative = gl.GL_QUADS
        else:
            self.primative = gl.GL_TRIANGLES

        self.bind()

        if shader is not None:
            self.bind_shader(shader)


class CompModel(BaseModel):

    def __init__(self, scene, models=[],visable=True):
        self.components = models
        self.visable = visable
        self.scene = scene
        self.M = TransformMatrix()

    def draw(self, M=TransformMatrix()):
        if self.visable:
            for component in self.components:
                transform = TransformMatrix()
                if M==TransformMatrix():
                    transform.matrix =self.M.get_transform()
                else:
                    transform.matrix = np.matmul(np.array(M.get_transform()), np.array(self.M.get_transform()))

                component.draw(
                    M=transform
                )

    def update(self):
        for component in self.components:
            component.update()


class ModelFromObj(CompModel):

    def __init__(self, scene, obj, shader=None, visable=True, generate_normals=True, flip_uvs=True, flip_winding=False, optimize_meshes=True):
        model_loader = ModelLoader()
        meshes = model_loader.load_model(obj, generate_normals=generate_normals, flip_uvs=flip_uvs, flip_winding=flip_winding, optimize_meshes=optimize_meshes)

        models = []
        for mesh in meshes:
            models.append(ModelFromMesh(scene, mesh, visable=visable, shader=shader))

        CompModel.__init__(self, scene, models, visable=visable)


class ModelFromObjInstanced(CompModel):

    def __init__(self, scene, obj, shader=None, visable=True, generate_normals=True, flip_uvs=True, flip_winding=False, optimize_meshes=True, num_instances=100):
        model_loader = ModelLoader()
        meshes = model_loader.load_model(obj, generate_normals=generate_normals, flip_uvs=flip_uvs, flip_winding=flip_winding, optimize_meshes=optimize_meshes)

        models = []
        for mesh in meshes:
            models.append(ModelFromMeshInstanced(scene, mesh, visable=visable, shader=shader, num_instances=num_instances))

        CompModel.__init__(self, scene, models, visable=visable)