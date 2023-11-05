import OpenGL.GL as gl
import numpy as np

from cube_map import CubeMap
from model import ModelFromMesh
from mesh import CubeMesh
from shaders import BaseShaderProgram

class SkyBoxShader(BaseShaderProgram):

    def __init__(self):
        BaseShaderProgram.__init__(self, 'skybox')

    def bind(self, model, M):
        BaseShaderProgram.bind(self, model, M)
        P = model.scene.camera.projection()  # get projection matrix from the scene
        V = np.array(model.scene.camera.view())  # get view matrix from the camera
        V = V.reshape((4,4))
        Vr = np.identity(4)
        Vr[:3, :3] = V[:3, :3]

        self.uniforms['PVM'].bind(np.matmul(P, np.matmul(Vr, M)))

class SkyBox(ModelFromMesh):

    def __init__(self, scene, name, files=None, extension='jpg'):
        ModelFromMesh.__init__(self, 
                               scene,
                               CubeMesh(texture=CubeMap("skybox_sampler", name=name, files=files, extension=extension)),
                               name='skybox',
                               shader=SkyBoxShader()
                               )

        self.M.scale([10, 10, 10])

    def draw(self):
        gl.glDepthMask(gl.GL_FALSE)
        ModelFromMesh.draw(self)
        gl.glDepthMask(gl.GL_TRUE)
