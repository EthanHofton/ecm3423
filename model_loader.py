import pyassimp as assimp
import numpy as np

from mesh import Mesh
from material import Material

class ModelLoader:

    def load_model(self, path, generate_normals=True, flip_uvs=True, flip_winding=False, optimize_meshes=True, generate_tangents=True):
        meshes = []
        processing = assimp.postprocess.aiProcess_Triangulate | assimp.postprocess.aiProcess_JoinIdenticalVertices
        if flip_uvs:
            processing = processing | assimp.postprocess.aiProcess_FlipUVs
        if flip_winding:
            processing = processing | assimp.postprocess.aiProcess_FlipWindingOrder
        if generate_normals:
            processing = processing | assimp.postprocess.aiProcess_GenSmoothNormals
        if generate_tangents:
            processing = processing | assimp.postprocess.aiProcess_CalcTangentSpace

        if optimize_meshes:
            processing = processing | assimp.postprocess.aiProcess_OptimizeMeshes

        with assimp.load(f"models/{path}", processing=processing) as scene:
            for mesh in scene.meshes:
                faces = mesh.faces
                texCoords = mesh.texturecoords if mesh.texturecoords.any() else None
                vertices = mesh.vertices
                normals = mesh.normals if mesh.normals.any() else None
                m = mesh.material

                tangents = mesh.tangents if mesh.tangents.any() else None
                bitangents = mesh.bitangents if mesh.bitangents.any() else None

                if texCoords is not None:
                    texCoords = texCoords[0][:, :2]

                # print(m.properties)

                # load map_Kd
                map_Kd = m.properties.get(('file', 1), None)
                # load map_Ks
                map_Ks = m.properties.get(('file', 2), None)
                map_Ns = m.properties.get(('file', 7), None)
                map_bump = m.properties.get(('file', 5), None)

                material = Material(
                    Ka=np.array(m.properties['ambient'], dtype=np.float32),
                    Kd=np.array(m.properties['diffuse'], dtype=np.float32),
                    Ks=np.array(m.properties['specular'], dtype=np.float32),
                    Ns=np.array(m.properties['shininess'], dtype=np.float32),
                    map_Kd=map_Kd,
                    map_Ks=map_Ks,
                    map_Ns=map_Ns,
                    map_bump=map_bump,
                )

                # create model
                m = Mesh(
                    vertices=vertices,
                    normals=normals,
                    textureCoords=texCoords,
                    faces=faces,
                    material=material,
                    tangents=tangents,
                    bitangents=bitangents
                )
                meshes.append(m)

        return meshes