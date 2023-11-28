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
        self.cube_map = CubeMap("skybox_sampler", name=name, files=files, extension=extension)
        ModelFromMesh.__init__(self, 
                               scene,
                               CubeMesh(texture=self.cube_map),
                               name='skybox',
                               shader=SkyBoxShader()
                               )

        self.M.scale([10, 10, 10])

    def draw(self):
        # backface culling will not work as they must be viewed from inside
        # store the current state of backface culling
        culling_enabled = gl.glIsEnabled(gl.GL_CULL_FACE)

        if culling_enabled:
            gl.glDisable(gl.GL_CULL_FACE)

        gl.glDepthMask(gl.GL_FALSE)
        ModelFromMesh.draw(self)
        gl.glDepthMask(gl.GL_TRUE)

        if culling_enabled:
            gl.glEnable(gl.GL_CULL_FACE)
