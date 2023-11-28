import imgui
import glm

from skybox import SkyBox
from light import LightSource, SpotLight
from environment_map import EnvironmentMap, EnvironmentShader, EnvironmentShaderRefractive
from coordinate_system import CoordinateSystem
from light import DirectionalLight
from model import CompModel

trans = [0, 0, 0]
rot_axis = [0, 0, 0]
rot_angle = 0
scale = [1, 1, 1]

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

goto_settings_open = False

def show_lighting_settings(scene):
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
                scene.player_spotlight = SpotLight()
                scene.spot_lights.append(scene.player_spotlight)
            else:
                scene.spot_lights.remove(scene.player_spotlight)
                scene.player_spotlight = None

        if player_spotlight_enabled:
            _light_settings(scene.player_spotlight)
        imgui.pop_id()

    imgui.end()

def show_scene_settings(scene):
    imgui.begin("Scene Settings")
    
    global police_car_settings_open
    police_car_settings_open, _ = imgui.collapsing_header("Police car")

    if police_car_settings_open:
        changed, scene.POLICE_LIGHT_TIME = imgui.drag_float("light time", scene.POLICE_LIGHT_TIME, 0.01)

        global police_car_settings_red_light_open
        police_car_settings_red_light_open, _ = imgui.collapsing_header("Red light settings")
        if police_car_settings_red_light_open:
            _light_settings(scene.police_red_light)

        global police_car_settings_blue_light_open
        police_car_settings_blue_light_open, _ = imgui.collapsing_header("Blue light settings")
        if police_car_settings_blue_light_open:
            _light_settings(scene.police_blue_light)

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
    global selected_env_map_option

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
            
    global goto_settings_open
    goto_settings_open, _ = imgui.collapsing_header("Goto")

    if goto_settings_open:
        if imgui.button("Goto Environment Map"):
            scene.camera._pos = glm.vec3(CoordinateSystem.get_world_pos(-2, -4) + [-0.5, 2, 0])
            scene.camera._update_vectors()

        if imgui.button("Goto police car"):
            scene.camera._pos = glm.vec3(CoordinateSystem.get_world_pos(-2, -2) + [-0.5, 2, 0])
            scene.camera._update_vectors()

        if imgui.button("Goto racing police cars"):
            scene.camera._pos = glm.vec3(CoordinateSystem.get_world_pos(1, 1) + [-0.5, 2, 0])
            scene.camera._update_vectors()

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
