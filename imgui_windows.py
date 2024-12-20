import imgui
import glm
import OpenGL.GL as gl
import numpy as np
import glfw

from skybox import SkyBox
from light import LightSource, SpotLight
from environment_map import EnvironmentShader, EnvironmentShaderRefractive
from coordinate_system import CoordinateSystem
from light import DirectionalLight
from model import CompModel
from model import ModelFromObj, ModelFromMesh
from mesh import SphereMesh, CubeMesh

# global variables for the model settings
trans = [0, 0, 0]
rot_axis = [0, 0, 0]
rot_angle = 0
scale = [1, 1, 1]

#== Window header booleans ==#
dir_light_settings_open = False
skybox_settings_open = False

player_spotlight_settings_open = False
player_spotlight_enabled = False

police_car_settings_open = False
police_car_settings_red_light_open = False
police_car_settings_blue_light_open = False
camera_settings_open = False

environment_map_settings_open = False
selected_env_map_option = 2
selected_model_option = 0

goto_settings_open = False
open_gl_settings_open = False

scene_metrics_open = False
traffic_lights_settings_open = False
traffic_lights_enabled = False
traffic_light_lights_enabled = False

#== Traffic light controls ==#
red_offset = glm.vec3(0, 2.8, 0.31)
green_offset = glm.vec3(0, 1.8, 0.31)
traffic_light_offset = green_offset

def show_lighting_settings(scene):
    """
    Displays the lighting settings window in ImGui.

    Parameters:
    - scene: The scene object containing the lighting settings.

    Returns:
    None
    """
    imgui.begin("Lighting Settings")
    
    global dir_light_settings_open
    dir_light_settings_open, _ = imgui.collapsing_header("Directional Light")

    if dir_light_settings_open:
        imgui.push_id("dir_light_settings")
        imgui.text("Presets")

        if imgui.button("Default"):
            scene.directional_light = DirectionalLight()

        imgui.same_line()

        if imgui.button("Dusk"):
            scene.directional_light.direction = (0.8, 0.4, 0.1)
            scene.directional_light.Ia = (0.7, 0.3, 0.1)
            scene.directional_light.Id = (0.8, 0.5, 0.2)
            scene.directional_light.Is = (0.9, 0.6, 0.3)

        imgui.same_line()

        if imgui.button("Daytime warm"):
            # bright with a slight yellow tint
            scene.directional_light.direction = (1.0, 1.0, 0.8)
            scene.directional_light.Ia = (0.8, 0.8, 0.6)
            scene.directional_light.Id = (1.0, 1.0, 0.9)
            scene.directional_light.Is = (1.0, 1.0, 1.0)

        if imgui.button("Darkness"):
            scene.directional_light.direction = (0.1, 0.1, 0.1)
            scene.directional_light.Ia = (0.05, 0.05, 0.05)
            scene.directional_light.Id = (0.1, 0.1, 0.1)
            scene.directional_light.Is = (0.0, 0.0, 0.0)

        imgui.same_line()

        if imgui.button("Daytime cool"):
            scene.directional_light.direction = (0.8, 0.9, 1.0)
            scene.directional_light.Ia = (0.6, 0.7, 0.8)
            scene.directional_light.Id = (0.9, 0.95, 1.0)
            scene.directional_light.Is = (1.0, 1.0, 1.0)
        
        imgui.same_line()

        if imgui.button("Midnight"):
            scene.directional_light.direction = (0.05, 0.05, 0.1)
            scene.directional_light.Ia = (0.03, 0.03, 0.05)
            scene.directional_light.Id = (0.1, 0.1, 0.2)
            scene.directional_light.Is = (0.0, 0.0, 0.1)


        if imgui.button("Sunrise"):
            scene.directional_light.direction = (1.0, 0.7, 0.4)
            scene.directional_light.Ia = (0.9, 0.6, 0.3)
            scene.directional_light.Id = (1.0, 0.8, 0.6)
            scene.directional_light.Is = (1.0, 0.9, 0.7)


        imgui.same_line()

        if imgui.button("Sunset"):
            scene.directional_light.direction = (0.9, 0.5, 0.2)
            scene.directional_light.Ia = (0.8, 0.4, 0.1)
            scene.directional_light.Id = (0.9, 0.6, 0.3)
            scene.directional_light.Is = (1.0, 0.8, 0.5)

        imgui.same_line()

        if imgui.button("Gloomy"):
            scene.directional_light.direction = (0.5, 0.5, 0.5)
            scene.directional_light.Ia = (0.4, 0.4, 0.4)
            scene.directional_light.Id = (0.5, 0.5, 0.5)
            scene.directional_light.Is = (0.4, 0.4, 0.4)


        if imgui.button("Cloudy"):
            scene.directional_light.direction = (0.7, 0.7, 0.7)
            scene.directional_light.Ia = (0.6, 0.6, 0.6)
            scene.directional_light.Id = (0.7, 0.7, 0.7)
            scene.directional_light.Is = (0.8, 0.8, 0.8)

        imgui.same_line()

        if imgui.button("Stormy"):
            scene.directional_light.direction = (0.4, 0.4, 0.4)
            scene.directional_light.Ia = (0.3, 0.3, 0.3)
            scene.directional_light.Id = (0.4, 0.4, 0.4)
            scene.directional_light.Is = (0.5, 0.5, 0.5)

        imgui.same_line()

        if imgui.button("Overcast"):
            scene.directional_light.direction = (0.6, 0.6, 0.6)
            scene.directional_light.Ia = (0.5, 0.5, 0.5)
            scene.directional_light.Id = (0.6, 0.6, 0.6)
            scene.directional_light.Is = (0.7, 0.7, 0.7)

        if imgui.button("Twilight"):
            scene.directional_light.direction = (0.7, 0.6, 0.8)
            scene.directional_light.Ia = (0.6, 0.5, 0.7)
            scene.directional_light.Id = (0.7, 0.6, 0.8)
            scene.directional_light.Is = (0.8, 0.7, 0.9)

        imgui.same_line()

        if imgui.button("Snowy"):
            scene.directional_light.direction = (0.8, 0.9, 1.0)
            scene.directional_light.Ia = (0.7, 0.8, 0.9)
            scene.directional_light.Id = (0.8, 0.9, 1.0)
            scene.directional_light.Is = (0.9, 1.0, 1.0)

        imgui.same_line()

        if imgui.button("Rainy"):
            scene.directional_light.direction = (0.5, 0.6, 0.7)
            scene.directional_light.Ia = (0.4, 0.5, 0.6)
            scene.directional_light.Id = (0.5, 0.6, 0.7)
            scene.directional_light.Is = (0.6, 0.7, 0.8)

        if imgui.button("Moonlight"):
            scene.directional_light.direction = (0.7, 0.7, 1.0)
            scene.directional_light.Ia = (0.6, 0.6, 0.8)
            scene.directional_light.Id = (0.7, 0.7, 1.0)
            scene.directional_light.Is = (0.8, 0.8, 1.0)

        imgui.separator()

        imgui.text("Manual")
        _light_settings(scene.directional_light)
        imgui.pop_id()

    global skybox_settings_open
    skybox_settings_open, _ = imgui.collapsing_header("Skybox")
    
    if skybox_settings_open:
        if imgui.button("Blue clouds"):
            scene.skybox = SkyBox(scene, "skybox/blue_clouds", extension="jpg")
        imgui.same_line()
        
        if imgui.button("Yellow clouds"):
            scene.skybox = SkyBox(scene, "skybox/yellow_clouds", extension="jpg")
        imgui.same_line()

        if imgui.button("Mountains"):
            scene.skybox = SkyBox(scene, "skybox/ame_ash", extension="bmp")

        if imgui.button("Frozen Dusk"):
            scene.skybox = SkyBox(scene, "skybox/sb_frozendusk", extension="jpg")

        imgui.same_line()

        if imgui.button("Night Sky"):
            scene.skybox = SkyBox(scene, "skybox/night_sky", extension="png")

    global player_spotlight_settings_open
    player_spotlight_settings_open, _ = imgui.collapsing_header("Player Spotlight")

    if player_spotlight_settings_open:
        imgui.push_id("player_spotlight_settings")
        global player_spotlight_enabled
        changed, player_spotlight_enabled = imgui.checkbox("enabled", player_spotlight_enabled)

        if changed:
            if player_spotlight_enabled:
                # range of approx 100m
                scene.player_spotlight = SpotLight(constant=1, linear=0.045, quadratic=0.0075)
                scene.spot_lights.append(scene.player_spotlight)
            else:
                scene.spot_lights.remove(scene.player_spotlight)
                scene.player_spotlight = None

        if player_spotlight_enabled:
            _light_settings(scene.player_spotlight)
        imgui.pop_id()

    imgui.end()

def show_scene_settings(scene):
    """
    Displays the scene settings window using ImGui.

    Parameters:
    - scene: The scene object containing the settings to be displayed.

    Returns:
    None
    """
    imgui.begin("Scene Settings")
    
    global police_car_settings_open
    police_car_settings_open, _ = imgui.collapsing_header("Police car")

    if police_car_settings_open:
        pass
        changed, scene.POLICE_LIGHT_TIME = imgui.drag_float("light time", scene.POLICE_LIGHT_TIME, 0.01)

    global camera_settings_open
    camera_settings_open, _ = imgui.collapsing_header("Camera")

    if camera_settings_open:
        changed, scene.camera.move_speed = imgui.drag_float("move speed", scene.camera.move_speed, 1)
        changed, scene.camera._turn_speed = imgui.drag_float("turn speed", scene.camera._turn_speed, 1)

        # camera position
        front = scene.camera.front()
        changed, scene.camera._pos = imgui.drag_float3("position", *scene.camera._pos)
        changed, scene.camera._yaw = imgui.drag_float("yaw", scene.camera._yaw, 0.01)
        changed, scene.camera._pitch = imgui.drag_float("pitch", scene.camera._pitch, 0.01)
        imgui.label_text("front", f"[{front.x:.3f}, {front.y:.3f}, {front.z:.3f}]")

        # projection stuff
        changed, scene.camera._fov = imgui.drag_float("fov", scene.camera._fov, 0.01)
        changed, scene.camera._z_near = imgui.drag_float("near", scene.camera._z_near, 0.01)
        changed, scene.camera._z_far = imgui.drag_float("far", scene.camera._z_far, 0.01)
        changed, scene.camera._aspect_ratio = imgui.drag_float("aspect ratio", scene.camera._aspect_ratio, 0.01)

        if imgui.button("Update camera"):
            scene.camera._update_vectors()
        
        imgui.same_line()

        if imgui.button("Update projection"):
            scene.camera._update_projection()

    global environment_map_settings_open
    environment_map_settings_open, _ = imgui.collapsing_header("Environment Map")
    global selected_env_map_option, selected_model_option

    def update_tank_shader(scene, shader):
        if isinstance(scene.tank, CompModel):
            for model in scene.tank.components:
                model.bind_shader(shader)
        else:
            scene.tank.bind_shader(shader)

    if environment_map_settings_open:

        options = ["Dynamic Reflective", "Dynamic Refractive", "Static Reflective", "Static Refractive"]
        changed, selected_env_map_option= imgui.combo("type", selected_env_map_option, options)
        
        if changed:
            if selected_env_map_option == 0:
                scene.tank_shader = EnvironmentShader(map=scene.tank_env_map)
                update_tank_shader(scene, scene.tank_shader)
                scene.update_tank_env_map = True
            elif selected_env_map_option == 1:
                scene.tank_shader = EnvironmentShaderRefractive(map=scene.tank_env_map)
                update_tank_shader(scene, scene.tank_shader)
                scene.update_tank_env_map = True
            elif selected_env_map_option == 2:
                scene.tank_shader = EnvironmentShader(map=scene.skybox.cube_map)
                update_tank_shader(scene, scene.tank_shader)
                scene.update_tank_env_map = False
            elif selected_env_map_option == 3:
                scene.tank_shader = EnvironmentShaderRefractive(map=scene.skybox.cube_map)
                update_tank_shader(scene, scene.tank_shader)
                scene.update_tank_env_map = False


        if selected_env_map_option == 0:
            imgui.text("This is a dynamic environment map. It is updated every frame. Each frame the camera is moved to the position of the tanks and the scene is rendered in all 6 directions of a cube map. The cube map is then sampled in the direction of the light ray, reflected along the model normal. This method is very computationally expensive.")
        elif selected_env_map_option == 1:
            imgui.text("This is a dynamic environment map. It is updated every frame. Each frame the camera is moved to the position of the tanks and the scene is rendered in all 6 directions of a cube map. The cube map is then sampled in the direction of the light ray, refracted along the model normal. This method is very computationally expensive.")
        elif selected_env_map_option == 2:
            imgui.text("This mode maps the skybox texture to the model by sampling the skybox along the reflected light ray. This is a static environment map, it is not updated every frame.")
        elif selected_env_map_option == 3:
            imgui.text("This mode maps the skybox texture to the model by sampling the skybox along the refracted light ray. This is a static environment map, it is not updated every frame.")

        if selected_env_map_option == 1 or selected_env_map_option == 3:
            _, scene.tank_shader.refractive_index_from = imgui.slider_float("refractive index from", scene.tank_shader.refractive_index_from, 0.01, 3)
            _, scene.tank_shader.refractive_index_to = imgui.slider_float("refractive index to", scene.tank_shader.refractive_index_to, 0.01, 3)

        options = ["Tank", "Taxi", "Car", "Dinosaur", "Sphere", "Cube"]
        changed, selected_model_option = imgui.combo("model", selected_model_option, options)

        def move_model(model):
            model.M.translate(np.array([0, CoordinateSystem.ROAD_OFFSET, 0], 'f'))
            model.M.translate(CoordinateSystem.get_world_pos(-2, -4))

        if changed:
            if selected_model_option == 0:
                scene.models.remove(scene.tank)
                scene.tank = ModelFromObj(scene, 'tank/tank.obj', shader=scene.tank_shader)
                scene.models.append(scene.tank)
            if selected_model_option == 1:
                scene.models.remove(scene.tank)
                scene.tank = ModelFromObj(scene, 'taxi/taxi.obj', shader=scene.tank_shader)
                scene.models.append(scene.tank)
            if selected_model_option == 2:
                scene.models.remove(scene.tank)
                scene.tank = ModelFromObj(scene, 'car_red/car_red.obj', shader=scene.tank_shader)
                scene.models.append(scene.tank)
            if selected_model_option == 3:
                scene.models.remove(scene.tank)
                scene.tank = ModelFromObj(scene, 'dyno/dyno.obj', shader=scene.tank_shader)
                scene.models.append(scene.tank)
            if selected_model_option == 4:
                scene.models.remove(scene.tank)
                scene.tank = ModelFromMesh(scene, SphereMesh(), shader=scene.tank_shader)
                scene.models.append(scene.tank)
            if selected_model_option == 5:
                scene.models.remove(scene.tank)
                scene.tank = ModelFromMesh(scene, CubeMesh(), shader=scene.tank_shader)
                scene.models.append(scene.tank)

            move_model(scene.tank)

        if imgui.button("Move Model Up"):
            scene.tank.M.translate(np.array([0, 0.5, 0], 'f'))
            
    global goto_settings_open
    goto_settings_open, _ = imgui.collapsing_header("Goto")

    if goto_settings_open:
        if imgui.button("Goto Environment Map"):
            scene.camera._pos = scene.tank.M.get_position() + glm.vec3([0, 2, 0])
            scene.camera._update_vectors()

        if imgui.button("Goto police car"):
            pos = scene.police_car.shader.matricies[np.random.randint(0, len(scene.police_car.shader.matricies))].get_position()
            scene.camera._pos = glm.vec3(pos + [-0.5, 2, 0])
            scene.camera._update_vectors()

        if imgui.button("Goto racing cars"):
            pos = scene.car_offsets[np.random.randint(0, len(scene.car_offsets))]
            scene.camera._pos = glm.vec3(CoordinateSystem.get_world_pos(pos[0], pos[1]) + [-0.5, 2, 0])
            scene.camera._update_vectors()

        if imgui.button("Dino Swarm"):
            pos = scene.dyno_positions[np.random.randint(0, len(scene.dyno_positions))]
            scene.camera._pos = glm.vec3(CoordinateSystem.get_world_pos(pos[0], pos[1]) + [-0.5, 2, 0])
            scene.camera._update_vectors()

    global open_gl_settings_open
    open_gl_settings_open, _ = imgui.collapsing_header("OpenGL")

    if open_gl_settings_open:
        # wireframe
        if imgui.button("Wireframe"):
            scene.wireframe = not scene.wireframe
            if scene.wireframe:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            else:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

        imgui.separator()

        if imgui.button("Cull back faces CCW"):
            scene.enable_face_culling(gl.GL_BACK, gl.GL_CCW)

        imgui.same_line()

        if imgui.button("Cull back faces CW"):
            scene.enable_face_culling(gl.GL_BACK, gl.GL_CW)

        imgui.separator()

        if imgui.button("Cull front faces CCW"):
            scene.enable_face_culling(gl.GL_FRONT, gl.GL_CCW)

        imgui.same_line()

        if imgui.button("Cull front faces CW"):
            scene.enable_face_culling(gl.GL_FRONT, gl.GL_CW)

        imgui.separator()

        if imgui.button("Disable face culling"):
            scene.disable_face_culling()

        imgui.separator()

        # enable/disable depth testing
        if imgui.button("Enable depth testing"):
            gl.glEnable(gl.GL_DEPTH_TEST)

        imgui.same_line()

        if imgui.button("Disable depth testing"):
            gl.glDisable(gl.GL_DEPTH_TEST)

        imgui.separator()

        # enable/disable blending
        if imgui.button("Enable blending"):
            gl.glEnable(gl.GL_BLEND)

        imgui.same_line()

        if imgui.button("Disable blending"):
            gl.glDisable(gl.GL_BLEND)

        imgui.separator()

        # FPS
        changed, scene.FPS = imgui.drag_float("FPS", scene.FPS, 1)

        if imgui.button("Disable VSync"):
            glfw.swap_interval(0)

        imgui.same_line()

        if imgui.button("Enable VSync"):
            glfw.swap_interval(1)

    global scene_metrics_open
    scene_metrics_open, _ = imgui.collapsing_header("Scene Metrics")

    if scene_metrics_open:
        imgui.label_text("FPS", f"{(1/scene.delta_time):.2f}")
        imgui.label_text("delta time", f"{scene.delta_time:.2f}")
        imgui.label_text("models", f"{len(scene.models)}")
        imgui.label_text("point lights", f"{len(scene.lights)}")
        imgui.label_text("spot lights", f"{len(scene.spot_lights)}")

    global traffic_lights_settings_open
    traffic_lights_settings_open, _ = imgui.collapsing_header("Traffic Lights")

    if traffic_lights_settings_open:
        global traffic_lights_enabled
        changed, traffic_lights_enabled = imgui.checkbox("enabled", traffic_lights_enabled)

        if changed:
            if traffic_lights_enabled:
                scene.models.append(scene.traffic_light)
            else:
                scene.models.remove(scene.traffic_light)

        if traffic_lights_enabled:
            global traffic_light_lights_enabled
            changed, traffic_light_lights_enabled = imgui.checkbox("lights enabled", traffic_light_lights_enabled)

            if changed:
                if traffic_light_lights_enabled:
                    scene.lights.extend(scene.traffic_light_lights)
                else:
                    scene.lights = [light for light in scene.lights if light not in scene.traffic_light_lights]

            if traffic_light_lights_enabled:
                global traffic_light_offset

                if imgui.button("Red"):
                    for index, light in enumerate(scene.traffic_light_lights):
                        traffic_light_offset = red_offset
                        light.Id = (1, 0, 0)
                        light.Is = (1, 0, 0)
                        light.Ia = (1, 0, 0)
                
                imgui.same_line()

                if imgui.button("Green"):
                    for light in scene.traffic_light_lights:
                        traffic_light_offset = green_offset
                        light.Id = (0, 1, 0)
                        light.Is = (0, 1, 0)
                        light.Ia = (0, 1, 0)

                for index, light in enumerate(scene.traffic_light_lights):
                    tf_pos = scene.traffic_light_shader.offsets[index]
                    light.position = glm.vec3(tf_pos[0], tf_pos[1], tf_pos[2]) + traffic_light_offset

                changed, traffic_light_offset = imgui.drag_float3("offset", *traffic_light_offset)

    imgui.end()

def show_light_settings(light, name):
    imgui.begin(f"Light Source {name}")

    _light_settings(light)

    imgui.end()

def _light_settings(light):
    # create a slider for the light position
    if hasattr(light, 'position'):
        changed, light.position = imgui.drag_float3("position", *light.position)
    if hasattr(light, 'direction'):
        changed, light.direction = imgui.drag_float3("direction", *light.direction)

    changed, light.Ia = imgui.color_edit3("Ia", *light.Ia)
    changed, light.Id = imgui.color_edit3("Id", *light.Id)
    changed, light.Is = imgui.color_edit3("Is", *light.Is)

    if isinstance(light, LightSource) or isinstance(light, SpotLight):
        changed, light.constant = imgui.drag_float("constant", light.constant, 0.01)
        changed, light.linear = imgui.drag_float("linear", light.linear, 0.01)
        changed, light.quadratic = imgui.drag_float("quadratic", light.quadratic, 0.01)
        changed, light.intensity = imgui.drag_float("intensity", light.intensity, 0.01)

    if isinstance(light, SpotLight):
        changed, light.cutoff = imgui.drag_float("inner cutoff", light.cutoff, 0.01)
        changed, light.outer_cutoff = imgui.drag_float("outer cutoff", light.outer_cutoff, 0.01)

def imgui_model_settings(model, name):
    imgui.begin(f"Model {name}")
    imgui.push_id(str(name))

    imgui.text("transformation")

    imgui.separator()    

    global trans, rot_axis, rot_angle, scale

    changed, trans = imgui.drag_float3("translation", *trans)
    changed, rot_axis = imgui.drag_float3("rotation axis", *rot_axis)
    changed, rot_angle = imgui.drag_float("rotation angle", rot_angle)
    changed, scale = imgui.drag_float3("scale", *scale)

    if imgui.button("apply"):
        model.M.translate(trans)
        model.M.rotate(rot_axis, glm.radians(rot_angle))
        model.M.scale(scale)

    if imgui.button("reset"):
        trans = [0, 0, 0]
        rot_axis = [0, 0, 0]
        rot_angle = 0
        scale = [1, 1, 1]

    if hasattr(model, 'mesh'):
        imgui.text("material")
        imgui.separator()    

        changed, model.mesh.material.Ka = imgui.color_edit3("Ka", *model.mesh.material.Ka)
        changed, model.mesh.material.Kd = imgui.color_edit3("Kd", *model.mesh.material.Kd)
        changed, model.mesh.material.Ks = imgui.color_edit3("Ks", *model.mesh.material.Ks)
        changed, model.mesh.material.Ns = imgui.slider_float("Ns", model.mesh.material.Ns, 0, 100)
        changed, model.mesh.material.alpha = imgui.slider_float("alpha", model.mesh.material.alpha, 0, 1)

    imgui.pop_id()
    imgui.end()
