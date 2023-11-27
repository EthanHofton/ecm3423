import glm
import glfw

class Camera3d:

    def __init__(self, aspect_ratio, fov = 45 ,z_near = 0.1, z_far = 100.0):
        self._view = glm.mat4(1.0)

        self._pos = glm.vec3(0.0, 0.0, 0.0)
        self._world_up = glm.vec3(0.0, 1.0, 0.0)
        self._move_speed = 0.08
        self._turn_speed = .04
        self._yaw = -90.0
        self._pitch = 0.0
        self._constrain_pitch = True

        self._front = glm.vec3(0.0, 0.0, -1.0)
        self._right = glm.vec3(1.0, 0.0, 0.0)
        self._up = glm.vec3(0.0, 1.0, 0.0)

        self._aspect_ratio = aspect_ratio
        self._fov = fov
        self._z_near = z_near
        self._z_far = z_far
        self._projection = glm.perspective(glm.radians(fov), aspect_ratio, z_near, z_far)

        self._active = True
        self._camera_dirty = True
        self._first_mouse = True

        self._mouse_last_x = 0.0
        self._mouse_last_y = 0.0

        self.move_speed = 100
        self.scroll_speed = 100

        self._update_vectors()

    def _update_vectors(self):
        front = glm.vec3(0.0, 0.0, 0.0)
        front.x = glm.cos(glm.radians(self._yaw)) * glm.cos(glm.radians(self._pitch))
        front.y = glm.sin(glm.radians(self._pitch))
        front.z = glm.sin(glm.radians(self._yaw)) * glm.cos(glm.radians(self._pitch))
        self._front = glm.normalize(front)
        self._right = glm.normalize(glm.cross(self._front, self._world_up))
        self._up = glm.normalize(glm.cross(self._right, self._front))

        self._view = glm.lookAt(self._pos, self._pos + self._front, self._up)
        self._camera_dirty = False

    def translate(self, direction, delta_time=1.0):
        if self._active:
            velocity = self._move_speed * delta_time
            self._pos += self._front * direction.z * velocity
            self._pos += self._right * direction.x * velocity
            self._pos += self._up * direction.y * velocity
            self._camera_dirty = True

    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE  and action == glfw.PRESS:
            if self._active:
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            else:
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

            self._active = not self._active
            self._first_mouse = True
        
    def mouse_callback(self, window, x, y):
        if not self._active:
            return        

        dx = x - self._mouse_last_x
        dy = self._mouse_last_y - y

        if not self._first_mouse:
            if dx != 0.0 or dy != 0.0:
                self._yaw += dx * self._turn_speed
                self._pitch += dy * self._turn_speed

                if self._constrain_pitch:
                    if self._pitch > 89.0:
                        self._pitch = 89.0
                    if self._pitch < -89.0:
                        self._pitch = -89.0

                self._camera_dirty = True
        else:
            self._first_mouse = False

        self._mouse_last_x = x
        self._mouse_last_y = y

    def position(self):
        return self._pos

    def key_input(self, window, dt):
        if not self._active:
            return

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.translate(glm.vec3(0.0, 0.0, 1.0 * self.move_speed * dt))
        
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.translate(glm.vec3(0.0, 0.0, -1.0 * self.move_speed * dt))

        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.translate(glm.vec3(-1.0 * self.move_speed * dt, 0.0, 0.0))

        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.translate(glm.vec3(1.0 * self.move_speed * dt, 0.0, 0.0))

        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            self.translate(glm.vec3(0.0, 1.0 * self.move_speed * dt, 0.0))

        if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            self.translate(glm.vec3(0.0, -1.0 * self.move_speed * dt, 0.0))

        if glfw.get_key(window, glfw.KEY_MINUS) == glfw.PRESS:
            self._fov -= 1. * self.scroll_speed * dt
            self._update_projection()

        if glfw.get_key(window, glfw.KEY_EQUAL) == glfw.PRESS:
            self._fov += 1. * self.scroll_speed * dt
            self._update_projection()


    # maybe do zoom out with out scroll call back ??

    def _update_projection(self):
        self._projection = glm.perspective(glm.radians(self._fov), self._aspect_ratio, self._z_near, self._z_far)

    def front(self):
        if self._camera_dirty:
            self._update_vectors()
        return self._front

    def view(self):
        if self._camera_dirty:
            self._update_vectors()
        return self._view
    
    def projection(self):
        return self._projection