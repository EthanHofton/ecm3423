from material import Material
import numpy as np

from texture import Texture
from matutils import sort_faces_by_winding_order
import numpy as np


class Mesh:
    '''
    Hold mesh data: vertices, faces, normals, bitangents, tangnets, texture coordinates, and material.
    '''
    def __init__(self, vertices=None, faces=None, normals=None, textureCoords=None, material=None, tangents=None, bitangents=None):
        '''
        Initialises a mesh object.
        :param vertices: A numpy array of shape (N, 3) containing the vertices of the mesh.
        :param faces: A numpy array of shape (N, 3) containing the faces of the mesh.
        :param normals: A numpy array of shape (N, 3) containing the normals of the mesh.
        :param textureCoords: A numpy array of shape (N, 2) containing the texture coordinates of the mesh.
        :param material: A material object containing the material properties of the mesh.
        :param tangents (optional): A numpy array of shape (N, 3) containing the tangents of the mesh.
        :param bitangents (optional): A numpy array of shape (N, 3) containing the bitangents of the mesh.
        '''
        self.name = 'Unknown'
        self.vertices = vertices
        self.faces = faces
        self.material = material if material is not None else Material()
        self.colors = None
        self.textureCoords = textureCoords
        self.textures = []
        self.tangents = tangents
        self.bitangents = bitangents

        if vertices is not None:
            print('Creating mesh')
            print('- {} vertices, ({})'.format(self.vertices.shape[0], self.vertices.shape))
            if faces is not None:
                print('- {} faces, ({})'.format(self.faces.shape[0], self.faces.shape))
            if textureCoords is not None: 
                print('- {} texture coordinates, ({})'.format(self.textureCoords.shape[0], self.textureCoords.shape))
        

        if normals is None:
            if faces is None:
                print('(W) Warning: the current code only calculates normals using the face vector of indices, which was not provided here.')
            else:
                self.calculate_normals()
        else:
            self.normals = normals

    def calculate_normals(self):
        '''
        method to calculate normals from the mesh faces.
        '''

        # Calculate triangle edges and deltas for vertices and texture coordinates
        delta_pos1 = self.vertices[self.faces[:, 1]] - self.vertices[self.faces[:, 0]]
        delta_pos2 = self.vertices[self.faces[:, 2]] - self.vertices[self.faces[:, 0]]
        delta_uv1 = self.textureCoords[self.faces[:, 1]] - self.textureCoords[self.faces[:, 0]]
        delta_uv2 = self.textureCoords[self.faces[:, 2]] - self.textureCoords[self.faces[:, 0]]

        # Calculate tangent and bitangent vectors
        self.face_tangents = np.zeros((len(self.faces), 3))
        self.face_bitangents = np.zeros((len(self.faces), 3))

        r = 1.0 / (delta_uv1[:, 0] * delta_uv2[:, 1] - delta_uv1[:, 1] * delta_uv2[:, 0])

        self.face_tangents[:, 0] = (delta_pos1[:, 0] * delta_uv2[:, 1] - delta_pos2[:, 0] * delta_uv1[:, 1]) * r
        self.face_tangents[:, 1] = (delta_pos1[:, 1] * delta_uv2[:, 1] - delta_pos2[:, 1] * delta_uv1[:, 1]) * r
        self.face_tangents[:, 2] = (delta_pos1[:, 2] * delta_uv2[:, 1] - delta_pos2[:, 2] * delta_uv1[:, 1]) * r

        self.face_bitangents[:, 0] = (delta_pos2[:, 0] * delta_uv1[:, 0] + delta_pos1[:, 0] * -delta_uv2[:, 0]) * r
        self.face_bitangents[:, 1] = (delta_pos2[:, 1] * delta_uv1[:, 0] + delta_pos1[:, 1] * -delta_uv2[:, 0]) * r
        self.face_bitangents[:, 2] = (delta_pos2[:, 2] * delta_uv1[:, 0] + delta_pos1[:, 2] * -delta_uv2[:, 0]) * r

        # Calculate normals for each face
        self.face_normals = np.cross(delta_pos1, delta_pos2)

        # Calculate normals for each vertex
        self.normals = np.zeros((len(self.vertices), 3))
        self.tangents = np.zeros((len(self.vertices), 3))
        self.bitangents = np.zeros((len(self.vertices), 3))

        for i in range(len(self.faces)):
            for j in range(3):
                self.normals[self.faces[i, j]] += self.face_normals[i]
                self.tangents[self.faces[i, j]] += self.face_tangents[i]
                self.bitangents[self.faces[i, j]] += self.face_bitangents[i]

        self.normals /= np.linalg.norm(self.normals, axis=1)[:, np.newaxis]
        self.tangents /= np.linalg.norm(self.tangents, axis=1)[:, np.newaxis]
        self.bitangents /= np.linalg.norm(self.bitangents, axis=1)[:, np.newaxis] 

        # convert to float32
        self.normals= self.normals.astype('f')
        self.tangents = self.tangents.astype('f')
        self.bitangents = self.bitangents.astype('f')

class SquareMesh(Mesh):

    def __init__(self, texture=None, inside=True, material=None):
        vertices = np.array([
            [-1.0, -1.0, 0.0],  # 0
            [+1.0, -1.0, 0.0],  # 1
            [-1.0, +1.0, 0.0],  # 2
            [+1.0, +1.0, 0.0],  # 3
        ], dtype='f')

        faces = np.array([
            [0, 1, 2],
            [1, 3, 2],
        ], dtype=np.uint32)

        textureCoords = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0]
        ], dtype='f')

        if not inside:
            # Reverse the winding order for backface culling
            faces = faces[:, np.argsort([0, 2, 1])]

        Mesh.__init__(self, vertices=vertices, faces=faces, textureCoords=textureCoords, material=material)

        if texture is not None:
            self.textures.append(texture)

class CubeMesh(Mesh):
    def __init__(self, texture=None, inside=False, material=None):
        
        # vertices, normals, texture coords
        vertices = np.array([
            [-1.0, -1.0, -1.0,  0.0,  0.0, -1.0, 0.0, 0.0,],
            [ 1.0,  1.0, -1.0,  0.0,  0.0, -1.0, 1.0, 1.0,],
            [ 1.0, -1.0, -1.0,  0.0,  0.0, -1.0, 1.0, 0.0,],
            [ 1.0,  1.0, -1.0,  0.0,  0.0, -1.0, 1.0, 1.0,],
            [-1.0, -1.0, -1.0,  0.0,  0.0, -1.0, 0.0, 0.0,],
            [-1.0,  1.0, -1.0,  0.0,  0.0, -1.0, 0.0, 1.0,],
            [-1.0, -1.0,  1.0,  0.0,  0.0,  1.0, 0.0, 0.0,],
            [ 1.0, -1.0,  1.0,  0.0,  0.0,  1.0, 1.0, 0.0,],
            [ 1.0,  1.0,  1.0,  0.0,  0.0,  1.0, 1.0, 1.0,],
            [ 1.0,  1.0,  1.0,  0.0,  0.0,  1.0, 1.0, 1.0,],
            [-1.0,  1.0,  1.0,  0.0,  0.0,  1.0, 0.0, 1.0,],
            [-1.0, -1.0,  1.0,  0.0,  0.0,  1.0, 0.0, 0.0,],
            [-1.0,  1.0,  1.0, -1.0,  0.0,  0.0, 1.0, 0.0,],
            [-1.0,  1.0, -1.0, -1.0,  0.0,  0.0, 1.0, 1.0,],
            [-1.0, -1.0, -1.0, -1.0,  0.0,  0.0, 0.0, 1.0,],
            [-1.0, -1.0, -1.0, -1.0,  0.0,  0.0, 0.0, 1.0,],
            [-1.0, -1.0,  1.0, -1.0,  0.0,  0.0, 0.0, 0.0,],
            [-1.0,  1.0,  1.0, -1.0,  0.0,  0.0, 1.0, 0.0,],
            [ 1.0,  1.0,  1.0,  1.0,  0.0,  0.0, 1.0, 0.0,],
            [ 1.0, -1.0, -1.0,  1.0,  0.0,  0.0, 0.0, 1.0,],
            [ 1.0,  1.0, -1.0,  1.0,  0.0,  0.0, 1.0, 1.0,],
            [ 1.0, -1.0, -1.0,  1.0,  0.0,  0.0, 0.0, 1.0,],
            [ 1.0,  1.0,  1.0,  1.0,  0.0,  0.0, 1.0, 0.0,],
            [ 1.0, -1.0,  1.0,  1.0,  0.0,  0.0, 0.0, 0.0,],
            [-1.0, -1.0, -1.0,  0.0, -1.0,  0.0, 0.0, 1.0,],
            [ 1.0, -1.0, -1.0,  0.0, -1.0,  0.0, 1.0, 1.0,],
            [ 1.0, -1.0,  1.0,  0.0, -1.0,  0.0, 1.0, 0.0,],
            [ 1.0, -1.0,  1.0,  0.0, -1.0,  0.0, 1.0, 0.0,],
            [-1.0, -1.0,  1.0,  0.0, -1.0,  0.0, 0.0, 0.0,],
            [-1.0, -1.0, -1.0,  0.0, -1.0,  0.0, 0.0, 1.0,],
            [-1.0,  1.0, -1.0,  0.0,  1.0,  0.0, 0.0, 1.0,],
            [ 1.0,  1.0 , 1.0,  0.0,  1.0,  0.0, 1.0, 0.0,],
            [ 1.0,  1.0, -1.0,  0.0,  1.0,  0.0, 1.0, 1.0,],
            [ 1.0,  1.0,  1.0,  0.0,  1.0,  0.0, 1.0, 0.0,],
            [-1.0,  1.0, -1.0,  0.0,  1.0,  0.0, 0.0, 1.0,],
            [-1.0,  1.0,  1.0,  0.0,  1.0,  0.0, 0.0, 0.0 ],
        ], dtype='f')

        pos = vertices[:, :3].reshape((36, 3))
        normals = vertices[:, 3:6].reshape((36, 3))
        textureCoords = vertices[:, 6:].reshape((36, 2))

        Mesh.__init__(self, vertices=pos, textureCoords=textureCoords, normals=normals, material=material)

        if texture is not None:
            self.textures = [
                texture
            ]


class SphereMesh(Mesh):

    def __init__(self, nvert=50, nhoriz=100, material=Material(Ka=[0.5,0.5,0.5], Kd=[0.6,0.6,0.9], Ks=[1.,1.,0.9], Ns=15.0), texture=None):
        n = (nvert-1)*nhoriz+2
        vertices = np.zeros((n, 3), 'f')
        vertex_colors = np.zeros((n, 3), 'f')

        vslice = np.pi/nvert
        hslice = 2.*np.pi/nhoriz
        vertices[0,:] = [0., 1., 0.]
        vertices[-1, :] = [0., -1., 0.]

        # texture coordinates
        textureCoords = np.zeros((n, 2), 'f')

        # start by creating vertices
        for i in range(nvert-1):
            y = np.cos((i+1) * vslice)
            r = np.sin((i+1) * vslice)
            for j in range(nhoriz):
                v = 1+i*nhoriz+j
                vertices[v, 0] = r * np.cos(j*hslice)
                vertices[v, 1] = y
                vertices[v, 2] = r * np.sin(j*hslice)
                vertex_colors[v, 0] = float(i) / float(nvert)
                vertex_colors[v, 1] = float(j) / float(nhoriz)
                textureCoords[v, 1] = float(i) / float(nvert)
                textureCoords[v, 0] = float(j) / float(nhoriz)

        nfaces = nhoriz*2 + (nvert-2)*(nhoriz)*2
        indices = np.zeros((nfaces, 3), dtype=np.uint32)
        k = 0

        for i in range(nhoriz-1):

            # top
            indices[k, 0] = 0
            indices[k, 2] = i + 1
            indices[k, 1] = i + 2
            k+=1

            # bottom
            lastrow = n - nhoriz - 2
            indices[k, 0] = lastrow + i + 2
            indices[k, 2] = lastrow + i + 1
            indices[k, 1] = n-1
            k+=1

        # last triangle at the top
        indices[k, :] = [0, 1, nhoriz]

        # last triangle at the bottom
        indices[k + 1, :] = [lastrow + 1, n - 1, n-2]
        k+=2

        for j in range(1, nvert-1):
            for i in range(nhoriz-1):
                lastrow = nhoriz*(j-1)+1
                row = nhoriz*j+1
                indices[k, 0] = row + i
                indices[k, 2] = row + i + 1
                indices[k, 1] = lastrow + i
                k += 1

                indices[k, 0] = row + i + 1
                indices[k, 2] = lastrow + i + 1
                indices[k, 1] = lastrow + i
                k += 1

            # last two triangles on this row
            indices[k, :] = [row + nhoriz - 1, lastrow + nhoriz - 1, row]
            k += 1
            indices[k, :] = [row, lastrow + nhoriz - 1, lastrow]
            k += 1

        Mesh.__init__(self,
                      vertices=vertices,
                      faces=indices,
                      textureCoords=textureCoords,
                      material=material
                      )

        if texture is not None:
            self.textures = [
                texture
            ]