import glfw
import OpenGL.GL as gl
import glm
from imgui.integrations.glfw import GlfwRenderer
import imgui
from camera3d import Camera3d

class Scene():

    def __del__(self):
        imgui.shutdown()
        glfw.terminate()

    def __init__(self, width=800, height=600, title="untitled"):
        self.window_size = (width, height)
        self.width = width
        self.height = height
        self.wireframe = False
        self.title = title

        # initialize glfw and create window
        imgui.create_context()
        if not glfw.init():
            raise Exception("Failed to initialize GLFW")

        # set the window hints
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        # create the window
        self._window = glfw.create_window(width, height, title, None, None)

        # check if window was created
        if not self._window:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")

        # create the opengl context
        glfw.make_context_current(self._window)

        # create the imgui renderer
        self.impl = GlfwRenderer(self._window)

        # opengl options
        # Here we start initialising the window from the OpenGL side
        print(self.get_window_framebuffer_size())
        gl.glViewport(0, 0, int(self.get_window_framebuffer_size()[0]), int(self.get_window_framebuffer_size()[1]))

        # this selects the background color
        gl.glClearColor(0.7, 0.7, 1.0, 1.0)

        # enable back face culling (see lecture on clipping and visibility
        # gl.glEnable(gl.GL_CULL_FACE)
        # depending on your model, or your projection matrix, the winding order may be inverted,
        # Typically, you see the far side of the model instead of the front one
        # uncommenting the following line should provide an easy fix.
        # gl.glCullFace(gl.GL_FRONT)

        # enable depth test for clean output (see lecture on clipping & visibility for an explanation
        gl.glEnable(gl.GL_DEPTH_TEST)

        # set the window callbacks
        glfw.set_key_callback(self._window, self.key_callback)
        glfw.set_mouse_button_callback(self._window, self.mouse_button_callback)
        glfw.set_cursor_pos_callback(self._window, self.mouse_callback)
        glfw.set_scroll_callback(self._window, self.scroll_callback)

        # class variables
        self.models = []
        self.lights = []
        self.camera = Camera3d(width/height)

    def key_callback(self, window, key, scancode, action, mods):
        # give imgui callbacks a chance to process the event
        self.impl.keyboard_callback(window, key, scancode, action, mods)

        if key == glfw.KEY_Q and action == glfw.PRESS:
            # close the window
            glfw.set_window_should_close(window, True)

        if key == glfw.KEY_0 and action == glfw.PRESS:
            self.wireframe = not self.wireframe
            if self.wireframe:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            else:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

        if self.camera is not None:
            self.camera.key_callback(window, key, scancode, action, mods)

    def mouse_button_callback(self, window, button, action, mods):
        pass

    def mouse_callback(self, window, xpos, ypos):
        if self.camera is not None:
            self.camera.mouse_callback(window, xpos, ypos)

    def scroll_callback(self, window, xoffset, yoffset):
        self.impl.scroll_callback(window, xoffset, yoffset)

    def draw(self, framebuffer=False):
        if not framebuffer:
            # clear the screen
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            # update the camera

        for model in self.models:
            model.draw()

    def run(self):
        while not glfw.window_should_close(self._window):
            # poll events
            glfw.poll_events()
            self.impl.process_inputs()
            if self.camera is not None:
                self.camera.key_input(self._window)
            # start the imgui frame
            imgui.new_frame()

            # call the draw function
            self.draw()

            # render imgui data
            imgui.render()
            # draw imgui data
            self.impl.render(imgui.get_draw_data())
            # swap the buffers
            glfw.swap_buffers(self._window)


    def get_window_framebuffer_size(self):
        return glfw.get_framebuffer_size(self._window)