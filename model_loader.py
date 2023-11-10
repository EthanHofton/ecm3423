import pyassimp as assimp
import numpy as np

from mesh import Mesh
from material import Material

class ModelLoader:

    def load_model(self, path, generate_normals=True):
        meshes = []
        processing = assimp.postprocess.aiProcess_Triangulate | assimp.postprocess.aiProcess_JoinIdenticalVertices
        if generate_normals:
            processing = processing | assimp.postprocess.aiProcess_GenSmoothNormals

        with assimp.load(f"models/{path}", processing=processing) as scene:
            for mesh in scene.meshes:
                faces = mesh.faces
                texCoords = mesh.texturecoords if mesh.texturecoords.any() else None
                vertices = mesh.vertices
                normals = mesh.normals if mesh.normals.any() else None
                m = mesh.material

                # texName = m.properties['file', 1]
                texName = None

                material = Material(
                    Ka=np.array(m.properties['ambient'], dtype=np.float32),
                    Kd=np.array(m.properties['diffuse'], dtype=np.float32),
                    Ks=np.array(m.properties['specular'], dtype=np.float32),
                    Ns=np.array(m.properties['shininess'], dtype=np.float32),
                    texture=texName
                )

                # create model
                m = Mesh(
                    vertices=vertices,
                    normals=normals,
                    textureCoords=texCoords,
                    faces=faces,
                    material=material
                )
                meshes.append(m)

        return meshes