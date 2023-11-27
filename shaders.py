import OpenGL.GL as gl
import OpenGL.GL.shaders as shaders
import numpy as np
from matutils import homog, unhomog

class Uniform:
    '''
    We create a simple class to handle uniforms, this is not necessary,
    but allow to put all relevant code in one place
    '''
    def __init__(self, name, value=None):
        '''
        Initialise the uniform parameter
        :param name: the name of the uniform, as stated in the GLSL code
        '''
        self.name = name
        self.value = value
        self.location = -1

    def link(self, program):
        '''
        This function needs to be called after compiling the GLSL program to fetch the location of the uniform
        in the program from its name
        :param program: the GLSL program where the uniform is used
        '''
        self.location = gl.glGetUniformLocation(program=program, name=self.name)

        # if self.location == -1:
        #     print('(E) Warning, no uniform {}'.format(self.name))

    def bind_matrix(self, M=None, number=1, transpose=True):
        '''
        Call this before rendering to bind the Python matrix to the GLSL uniform mat4.
        You will need different methods for different types of uniform, but for now this will
        do for the PVM matrix
        :param number: the number of matrices sent, leave that to 1 for now
        :param transpose: Whether the matrix should be transposed
        '''
        if M is not None:
            self.value = M
        if self.value.shape[0] == 4 and self.value.shape[1] == 4:
            gl.glUniformMatrix4fv(self.location, number, transpose, self.value)
        elif self.value.shape[0] == 3 and self.value.shape[1] == 3:
            gl.glUniformMatrix3fv(self.location, number, transpose, self.value)
        else:
            print('(E) Error: Trying to bind as uniform a matrix of shape {}'.format(self.value.shape))

    def bind(self,value):
        if value is not None:
            self.value = value

        if isinstance(self.value, int):
            self.bind_int()
        elif isinstance(self.value, float):
            self.bind_float()
        elif isinstance(self.value, np.ndarray):
            if self.value.ndim==1:
                self.bind_vector()
            elif self.value.ndim==2:
                self.bind_matrix()
        else:
            print('Wrong value bound: {} for {}'.format(type(self.value), self.name))

    def bind_int(self, value=None):
        if value is not None:
            self.value = value
        gl.glUniform1i(self.location, self.value)

    def bind_float(self, value=None):
        if value is not None:
            self.value = value
        gl.glUniform1f(self.location, self.value)

    def bind_vector(self, value=None):
        if value is not None:
            self.value = value
        if value.shape[0] == 2:
            gl.glUniform2fv(self.location, 1, value)
        elif value.shape[0] == 3:
            gl.glUniform3fv(self.location, 1, value)
        elif value.shape[0] == 4:
            gl.glUniform4fv(self.location, 1, value)
        else:
            print('(E) Error in Uniform.bind_vector(): Vector should be of dimension 2,3 or 4, found {}'.format(value.shape[0]))

    def set(self, value):
        '''
        function to set the uniform value (could also access it directly, of course)
        '''
        self.value = value


class BaseShaderProgram:
    '''
    This is the base class for loading and compiling the GLSL shaders.
    '''

    def __init__(self, name=None, vertex_shader=None, fragment_shader=None):
        '''
        Initialises the shaders
        :param vertex_shader: the name of the file containing the vertex shader GLSL code
        :param fragment_shader: the name of the file containing the fragment shader GLSL code
        '''

        self.name = name
        print('Creating shader program: {}'.format(name) )

        if name is not None:
            vertex_shader = 'shaders/{}/vertex.glsl'.format(name)
            fragment_shader = 'shaders/{}/fragment.glsl'.format(name)

        # load the vertex shader GLSL code
        if vertex_shader is None:
            self.vertex_shader_source = '''
                #version 330

                in vec3 position;   // vertex position
                uniform mat4 PVM; // the Perspective-View-Model matrix is received as a Uniform

                // main function of the shader
                void main() {
                    gl_Position = PVM * vec4(position, 1.0f);  // first we transform the position using PVM matrix
                }
            '''
        else:
            print('Load vertex shader from file: {}'.format(vertex_shader))
            with open(vertex_shader, 'r') as file:
                self.vertex_shader_source = file.read()
                
            self.vertex_shader_source = self.preprocess_vertex(self.vertex_shader_source)

        # load the fragment shader GLSL code
        if fragment_shader is None:
            self.fragment_shader_source = '''
                #version 330
                void main() {                   
                      gl_FragColor = vec4(1.0f);      // for now, we just apply the colour uniformly
                }
            '''
        else:
            print('Load fragment shader from file: {}'.format(fragment_shader))
            with open(fragment_shader, 'r') as file:
                self.fragment_shader_source = file.read()

            self.fragment_shader_source = self.preprocess_fragment(self.fragment_shader_source)

        # in order to simplify extension of the class in the future, we start storing uniforms in a dictionary.
        self.uniforms = {
            'PVM': Uniform('PVM'),  # project view model matrix
        }

        self.compiled = False

    def preprocess_vertex(self, source):
        source = self.read("utils/version.glsl") + source
        return source

    def preprocess_fragment(self, source):
        source = self.read("utils/version.glsl") + source
        return source

    def read(self, filename):
        with open(f"shaders/{filename}", 'r') as file:
            return file.read()

    def add_uniform(self, name):
        self.uniforms[name] = Uniform(name)

    def compile(self, attributes):
        '''
        Call this function to compile the GLSL codes for both shaders.
        :return:
        '''
        if self.compiled:
            # print('(W) Warning: Trying to compile already compiled shader program {}'.format(self.name))
            return

        print('Compiling GLSL shaders [{}]...'.format(self.name))
        try:
            self.program = gl.glCreateProgram()
            gl.glAttachShader(self.program, shaders.compileShader(self.vertex_shader_source, shaders.GL_VERTEX_SHADER))
            gl.glAttachShader(self.program, shaders.compileShader(self.fragment_shader_source, shaders.GL_FRAGMENT_SHADER))
        except RuntimeError as error:
            print('(E) An error occured while compiling {} shader:\n {}\n... forwarding exception...'.format(self.name, error)),
            raise error

        self.bindAttributes(attributes)

        gl.glLinkProgram(self.program)

        # tell OpenGL to use this shader program for rendering
        gl.glUseProgram(self.program)

        print('... done compiling GLSL shaders [{}, program: {}]'.format(self.name, self.program))

        # link all uniforms
        for uniform in self.uniforms:
            self.uniforms[uniform].link(self.program)

        self.compiled = True

    def bindAttributes(self, attributes):
        # bind all shader attributes to the correct locations in the VAO
        for name, location in attributes.items():
            gl.glBindAttribLocation(self.program, location, name)
            print('Binding attribute {} to location {}'.format(name, location))

    def bind(self, model, M):
        '''
        Call this function to enable this GLSL Program (you can have multiple GLSL programs used during rendering!)
        '''

        # tell OpenGL to use this shader program for rendering
        gl.glUseProgram(self.program)

        P = model.scene.camera.projection()
        V = model.scene.camera.view()

        # set the PVM matrix uniform
        self.uniforms['PVM'].bind(np.matmul(P, np.matmul(V, M)))

        self.bind_textures(model)

    def bind_textures(self, model):
        for unit, texture in enumerate(model.mesh.textures):
            texture.bind(unit)

            if texture.uniform not in self.uniforms.keys():
                self.add_uniform(texture.uniform)
                self.uniforms[texture.uniform].link(self.program)

            self.uniforms[texture.uniform].bind(unit)

        texture_unit = len(model.mesh.textures)

        texture_unit = self.bind_material_texture(model.mesh.material.map_Kd, 'material.map_Kd', 'material.use_map_Kd', texture_unit)
        texture_unit = self.bind_material_texture(model.mesh.material.map_Ks, 'material.map_Ks', 'material.use_map_Ks', texture_unit)
        texture_unit = self.bind_material_texture(model.mesh.material.map_bump, 'material.map_bump', 'material.use_map_bump', texture_unit)
        texture_unit = self.bind_material_texture(model.mesh.material.map_Ns, 'material.map_Ns', 'material.use_map_Ns', texture_unit)

        return texture_unit

    def bind_material_texture(self, texture, texture_name, has_texture_name, texture_unit):
        if has_texture_name not in self.uniforms.keys():
            self.add_uniform(has_texture_name)
            self.uniforms[has_texture_name].link(self.program)

        if texture is not None:
            if texture_name not in self.uniforms.keys():
                self.add_uniform(texture_name)
                self.uniforms[texture_name].link(self.program)

            texture.bind(texture_unit)
            self.uniforms[texture_name].bind(texture_unit)
            self.uniforms[has_texture_name].bind(1)
            return texture_unit + 1
        else:
            self.uniforms[has_texture_name].bind(0)

        return texture_unit

class PhongShader(BaseShaderProgram):
    '''
    This is the base class for loading and compiling the GLSL shaders. Handles the lighting and material unifroms.
    '''
    def __init__(self, name='phong'):
        '''
        Initialises the shaders
        '''

        BaseShaderProgram.__init__(self, name=name)

        self.uniforms = {}
        self.max_lights = 6
        self.max_spot_lights = 3

        # MVP
        self.add_uniform('PVM')
        self.add_uniform('ViT')
        self.add_uniform('viewPos')
        self.add_uniform('M')

        # material
        self.add_uniform('material.alpha')
        self.add_uniform('material.Ka')
        self.add_uniform('material.Kd')
        self.add_uniform('material.Ks')
        self.add_uniform('material.Ns')

        # directional light
        self.add_uniform('dir_light.dir')
        self.add_uniform('dir_light.Ia')
        self.add_uniform('dir_light.Id')
        self.add_uniform('dir_light.Is')

        # point light
        self.add_uniform('light_count')
        for i in range(self.max_lights):
            self.add_uniform('lights[{}].position'.format(i))
            self.add_uniform('lights[{}].Ia'.format(i))
            self.add_uniform('lights[{}].Id'.format(i))
            self.add_uniform('lights[{}].Is'.format(i))
            self.add_uniform('lights[{}].constant'.format(i))
            self.add_uniform('lights[{}].linear'.format(i))
            self.add_uniform('lights[{}].quadratic'.format(i))
            self.add_uniform('lights[{}].intensity'.format(i))

        # spot lights
        self.add_uniform('spot_light_count')
        for i in range(self.max_spot_lights):
            self.add_uniform('spot_lights[{}].position'.format(i))
            self.add_uniform('spot_lights[{}].direction'.format(i))
            self.add_uniform('spot_lights[{}].Ia'.format(i))
            self.add_uniform('spot_lights[{}].Id'.format(i))
            self.add_uniform('spot_lights[{}].Is'.format(i))

            self.add_uniform('spot_lights[{}].constant'.format(i))
            self.add_uniform('spot_lights[{}].linear'.format(i))
            self.add_uniform('spot_lights[{}].quadratic'.format(i))
            self.add_uniform('spot_lights[{}].intensity'.format(i))

            self.add_uniform('spot_lights[{}].cutoff'.format(i))
            self.add_uniform('spot_lights[{}].outer_cutoff'.format(i))

    def preprocess_fragment(self, source):
        preprocessed = self.read("utils/version.glsl")
        preprocessed += self.read("utils/material.glsl")
        preprocessed += self.read("utils/lights.glsl")
        preprocessed += self.read("utils/phong_lighting.glsl")
        preprocessed += source
        return preprocessed
    
    def preprocess_vertex(self, source):
        return super().preprocess_vertex(source)


    def bind(self, model, M):
        '''
        Call this function to enable this GLSL Program (you can have multiple GLSL programs used during rendering!)
        '''

        P = model.scene.camera.projection()
        V = model.scene.camera.view()

        # tell OpenGL to use this shader program for rendering
        gl.glUseProgram(self.program)

        # set the PVM matrix uniform
        self.uniforms['PVM'].bind(np.matmul(P, np.matmul(V, M)))

        self.uniforms['M'].bind(M)

        # set the Vit matrix uniform
        self.uniforms['ViT'].bind(np.linalg.inv(M)[:3, :3].transpose())

        # set the view position in view space
        self.uniforms['viewPos'].bind_vector(np.array(model.scene.camera.position(), 'f'))

        # bind the textures
        self.bind_textures(model)

        # bind material properties
        self.bind_material_uniforms(model.mesh.material)

        # bind the light properties
        self.bind_light_uniforms(model.scene.directional_light, model.scene.lights, model.scene.spot_lights, V)

    def bind_light_uniforms(self, dir_light, point_lights, spot_lights, V):
        # bind directional light
        self.uniforms['dir_light.dir'].bind_vector(np.array(dir_light.direction, 'f'))
        self.uniforms['dir_light.Ia'].bind_vector(np.array(dir_light.Ia, 'f'))
        self.uniforms['dir_light.Id'].bind_vector(np.array(dir_light.Id, 'f'))
        self.uniforms['dir_light.Is'].bind_vector(np.array(dir_light.Is, 'f'))

        # check if we have too many lights
        if len(point_lights) > self.max_lights:
            print(f'(E) Warning: Max light count of {self.max_lights} exceeded')

        # bind point lights
        for index, light in enumerate(point_lights):
            self.uniforms[f'lights[{index}].position'].bind_vector(np.array(light.position, 'f'))
            self.uniforms[f'lights[{index}].Ia'].bind_vector(np.array(light.Ia, 'f'))
            self.uniforms[f'lights[{index}].Id'].bind_vector(np.array(light.Id, 'f'))
            self.uniforms[f'lights[{index}].Is'].bind_vector(np.array(light.Is, 'f'))
            self.uniforms[f'lights[{index}].constant'].bind_float(light.constant)
            self.uniforms[f'lights[{index}].linear'].bind_float(light.linear)
            self.uniforms[f'lights[{index}].quadratic'].bind_float(light.quadratic)
            self.uniforms[f'lights[{index}].intensity'].bind_float(light.intensity)

        # bind light count
        self.uniforms['light_count'].bind_int(len(point_lights))

        # bind spot lights
        for index, light in enumerate(spot_lights):
            self.uniforms[f'spot_lights[{index}].position'].bind_vector(np.array(light.position, 'f'))
            self.uniforms[f'spot_lights[{index}].direction'].bind_vector(np.array(light.direction, 'f'))
            self.uniforms[f'spot_lights[{index}].Ia'].bind_vector(np.array(light.Ia, 'f'))
            self.uniforms[f'spot_lights[{index}].Id'].bind_vector(np.array(light.Id, 'f'))
            self.uniforms[f'spot_lights[{index}].Is'].bind_vector(np.array(light.Is, 'f'))
            self.uniforms[f'spot_lights[{index}].constant'].bind_float(light.constant)
            self.uniforms[f'spot_lights[{index}].linear'].bind_float(light.linear)
            self.uniforms[f'spot_lights[{index}].quadratic'].bind_float(light.quadratic)
            self.uniforms[f'spot_lights[{index}].intensity'].bind_float(light.intensity)
            self.uniforms[f'spot_lights[{index}].cutoff'].bind_float(np.cos(np.radians(light.cutoff)))
            self.uniforms[f'spot_lights[{index}].outer_cutoff'].bind_float(np.cos(np.radians(light.outer_cutoff)))

        # bind light count
        self.uniforms['spot_light_count'].bind_int(len(spot_lights))

    def bind_material_uniforms(self, material):
        self.uniforms['material.Ka'].bind_vector(np.array(material.Ka, 'f'))
        self.uniforms['material.Kd'].bind_vector(np.array(material.Kd, 'f'))
        self.uniforms['material.Ks'].bind_vector(np.array(material.Ks, 'f'))
        self.uniforms['material.Ns'].bind_float(material.Ns)
        self.uniforms['material.alpha'].bind(material.alpha)

    def add_uniform(self, name):
        if name in self.uniforms:
            print('(W) Warning re-defining already existing uniform %s' % name)
        self.uniforms[name] = Uniform(name)

    def unbind(self):
        gl.glUseProgram(0)

class FlatShader(PhongShader):
    def __init__(self):
        PhongShader.__init__(self, name='flat')


class GouraudShader(PhongShader):
    def __init__(self):
        PhongShader.__init__(self, name='gouraud')


class BlinnShader(PhongShader):
    def __init__(self):
        PhongShader.__init__(self, name='blinn')


class TextureShader(PhongShader):
    def __init__(self):
        PhongShader.__init__(self, name='texture')

class PhongShaderNormalMap(PhongShader):
    def __init__(self):
        PhongShader.__init__(self, name='phong_normal_map')

class PhongShaderInstanced(PhongShader):
    def __init__(self, name='phong_instanced'):
        PhongShader.__init__(self, name=name)
        self.add_uniform("M")
        self.add_uniform("PV")
        self.add_uniform("V")
        self.offsets = []

    def add_offset(self, offset):
        self.add_uniform(f'offsets[{len(self.offsets)}]')
        self.uniforms[f'offsets[{len(self.offsets)}]'].link(self.program)
        self.offsets.append(offset)
        
    def bind(self, model, M):
        PhongShader.bind(self, model, M)

        self.uniforms["M"].bind(M)
        self.uniforms["V"].bind(np.array(model.scene.camera.view(), 'f'))
        self.uniforms["PV"].bind(np.matmul(model.scene.camera.projection(), model.scene.camera.view()))

        for index, offset in enumerate(self.offsets):
            self.uniforms[f'offsets[{index}]'].bind_vector(offset)


class PhongShaderNormalMapInstancedMatrices(PhongShader):
    def __init__(self, name='phong_instanced_normal_map_matricies'):
        PhongShader.__init__(self, name=name)
        self.add_uniform("M")
        self.add_uniform("PV")
        self.add_uniform("V")
        self.matricies = []

    def add_matrix(self, M):
        self.add_uniform(f'matricies[{len(self.matricies)}]')
        self.uniforms[f'matricies[{len(self.matricies)}]'].link(self.program)
        self.matricies.append(M)

    def bind(self, model, M):
        PhongShader.bind(self, model, M)

        self.uniforms["M"].bind(M)
        self.uniforms["V"].bind(np.array(model.scene.camera.view(), 'f'))
        self.uniforms["PV"].bind(np.matmul(model.scene.camera.projection(), model.scene.camera.view()))

        for index, M in enumerate(self.matricies):
            self.uniforms[f'matricies[{index}]'].bind(np.array(M.matrix, 'f'))