# -*- coding: utf-8 -*-

"""
Constants used in Sphere_IOT project.

These constants include camera properties for the OpenGL shaders. Dictionary with shader data and lists with textures
and resources data.

"""
SPHERE_SMALL_RADIUS = 0.01
SPHERE_RADIUS = 1
COLLISION_NODE_DISC_RADIUS = 0.075
COLLISION_SOCKET_RADIUS = 0.01
HOVER_MIN_DISTANCE = 3

WIDTH, HEIGHT = 720, 720

# camera props for shader
FOV = 45.0
NEAR_VAL = 0.1
FAR_VAL = 100

# camera props
CAMERA_UP = 0
ROTATION = 90
MAX_YAW_UP = 70
MIN_YAW_DOWN = -70

# The camera should not get closer to the sphere_base
MIN_RADIUS = 2.0
# CAM_MOVEMENT_STEPS = 30
CAM_MOVEMENT_STEPS = 4

MESH_DIR = "..//sphere_base/model/resources/meshes/"
TEXTURE_DIR = "..//sphere_base/model/resources/"
SHADER_DIR = "..//sphere_base/model/resources/shaders/"
SKYBOX_IMG_DIR = "..//sphere_base/model/resources/textures/skybox/"

MODELS = {
    "sphere_base": {"model_id": 1, "model_file_name": "sphere1.obj", "shader": "SphereShader",
               "vertex_shader": "vert_sphere.glsl",
               "fragment_shader": "frag_sphere.glsl", "geometry_shader": "none"},
    "holo_sphere": {"model_id": 2, "model_file_name": "sphere1.obj", "shader": "HoloSphereShader",
                    "vertex_shader": "vert_holo_sphere.glsl", "fragment_shader": "frag_holo_sphere.glsl",
                    "geometry_shader": "none"},
    "sphere_small": {"model_id": 3, "model_file_name": "sphere_small.obj", "shader": "SphereSmallShader",
                     "vertex_shader": "vert_sphere_small.glsl", "fragment_shader": "frag_sphere_small.glsl",
                     "geometry_shader": "none"},
    "skybox": {"model_id": 4, "model_file_name": "skybox.obj", "shader": "SkyboxShader",
               "vertex_shader": "vert_skybox.glsl",
               "fragment_shader": "frag_skybox.glsl", "geometry_shader": "none"},
    "node": {"model_id": 5, "model_file_name": "node_disc1.obj", "shader": "NodeShader",
             "vertex_shader": "vert_node.glsl",
             "fragment_shader": "frag_node.glsl", "geometry_shader": "none"},
    "socket": {"model_id": 6, "model_file_name": "node_disc1.obj", "shader": "SocketShader",
               "vertex_shader": "vert_socket.glsl",
               "fragment_shader": "frag_socket.glsl", "geometry_shader": "none"},
    "rubber_band": {"model_id": 7, "model_file_name": "square1x1.obj", "shader": "FlatShader",
                    "vertex_shader": "vert_2d.glsl",
                    "fragment_shader": "frag_2d.glsl", "geometry_shader": "none"},
    "circle": {"model_id": 8, "model_file_name": "vertex1.obj", "shader": "CircleShader",
               "vertex_shader": "vert_circle.glsl",
               "fragment_shader": "frag_circle.glsl", "geometry_shader": "geom_circle.glsl"},
    "square": {"model_id": 9, "model_file_name": "vertex1.obj", "shader": "SquareShader",
               "vertex_shader": "vert_square.glsl",
               "fragment_shader": "frag_square.glsl", "geometry_shader": "geom_square.glsl"},
    "edge": {"model_id": 10, "model_file_name": "line_1x1.obj", "shader": "SphereEdgeShader",
             "vertex_shader": "vert_sphere_edge.glsl",
             "fragment_shader": "frag_sphere_edge.glsl", "geometry_shader": "none"},
    "cross_hair1": {"model_id": 11, "model_file_name": "vertex1.obj", "shader": "CrossShader",
                    "vertex_shader": "vert_circle.glsl",
                    "fragment_shader": "frag_circle.glsl", "geometry_shader": "geom_cross.glsl"},
    "cube": {"model_id": 12, "model_file_name": "vertex1.obj", "shader": "SphereShader",
             "vertex_shader": "vert_sphere.glsl",
             "fragment_shader": "frag_sphere.glsl", "geometry_shader": "none"},

}


SHADER_SWITCH = {"node": 0, "sphere_base": 1, "square1x1": 2, "rubber_band": 2, "sphere_small": 1, "socket": 2, "cube": 1}

SKYBOX_SETS = ([None, "space1", "space2", "space3", "space4", "space5", "space6", "red1", "red2", "red3",
                "blue1", "blue2"])

SKYBOX_SET = "space2"
SKYBOX_RANDOM_SET = True

EDGE_TYPE_DIRECT = 1

# sphere_base colors
LIGHT_GREEN = [0.07, 0.46, 0.24, 0.5]
GREEN = [0.37, 0.56, 0.32, 0.5]
BRIGHT_GREEN = [0.35, 0.8, 0.16, 0.5]
LIGHT_GREY = [0.93, 0.87, 0.89, 0.5]
GREY = [0.25, 0.26, 0.18, 0.5]
BRIGHT_GREY = [0.64, 0.59, 0.63, 0.5]
LIGHT_YELLOW = [0.81, 0.7, 0.46, 0.5]
YELLOW = [0.88, 0.7, 0.13, 0.5]
BRIGHT_YELLOW = [0.75, 0.95, 0.21, 0.5]
LIGHT_ORANGE = [0.94, 0.44, 0.54, 0.5]
ORANGE = [0.97, 0.44, 0.05, 0.5]
BRIGHT_ORANGE = [0.94, 0.51, 0.07, 0.5]
LIGHT_RED = [0.35, 0.13, 0.23, 0.5]
RED = [0.6, 0.08, 0.08, 0.5]
BRIGHT_RED = [0.99, 0.05, 0.38, 0.5]
LIGHT_BLUE = [0.10, 0.40, 1.00, 0.5]
BLUE = [0.10, 0.10, 1.00, 0.5]
BRIGHT_BLUE = [0.30, 0.65, 1.00, 0.5]

RELEVANCE_COLORS = {1: GREY, 2: BRIGHT_BLUE, 3: BRIGHT_GREEN, 4: LIGHT_YELLOW, 5: BRIGHT_RED, 6: LIGHT_GREEN}
# RELEVANCE_COLORS = {1: LIGHT_GREEN, 2: GREEN, 3: BRIGHT_GREEN, 4: LIGHT_GREY, 5: GREY, 6: BRIGHT_GREY,
#                     7: LIGHT_YELLOW, 8: YELLOW, 9: BRIGHT_YELLOW, 10: LIGHT_ORANGE, 11: ORANGE, 12: BRIGHT_ORANGE,
#                     13: LIGHT_RED, 14: RED, 15: BRIGHT_RED}

RELEVANCE_TEXTURE = {1: 29, 2: 4, 3: 6, 4: 3}

TRANSPARENCY_SMALL_SPHERES = 0.8
TRANSPARENCY_DETAIL_SPHERE = 0.5

TEXTURES = (
    [0, "not_used", "texture_diffuseN", "textures/grid1.jpg"],
    [1, "grid", "texture_diffuseN", "textures/grid1.jpg"],
    [2, "color_grid", "texture_diffuseN", "textures/color_grid.png"],
    [3, "red1", "texture_diffuseN", "textures/red1.jpg"],
    [4, "green1", "texture_diffuseN", "textures/green1.jpg"],
    [5, "blue1", "texture_diffuseN", "textures/blue1.jpg"],
    [6, "yellow1", "texture_diffuseN", "textures/yellow1.jpg"],
    [7, "white1", "texture_diffuseN", "textures/white1.jpg"],
    [8, "circle_black", "texture_diffuseN", "textures/circle_black.jpg"],
    [9, "circle_blue", "texture_diffuseN", "textures/circle_hover.jpg"],
    [10, "circle_red", "texture_diffuseN", "textures/circle_selected.jpg"],
    [11, "question_mark_icon", "texture_diffuseN", "icons/icon_question_mark.png"],
    [12, "man_icon", "texture_diffuseN", "icons/icon_man.png"],
    [13, "woman_icon", "texture_diffuseN", "icons/icon_woman.png"],
    [14, "lgbt_icon", "texture_diffuseN", "icons/icon_lgbt.png"],
    [15, "laptop_icon", "texture_diffuseN", "icons/icon_laptop.png"],
    [16, "mobile_icon", "texture_diffuseN", "icons/icon_mobile.png"],
    [17, "passport_icon", "texture_diffuseN", "icons/icon_passport.png"],
    [18, "pc_icon", "texture_diffuseN", "icons/icon_pc.png"],
    [19, "rfid_tag_icon", "texture_diffuseN", "icons/icon_rfid.png"],
    [20, "smart_card_icon", "texture_diffuseN", "icons/icon_smart_card.png"],
    [21, "smart_tv_icon", "texture_diffuseN", "icons/icon_smart_tv.png"],
    [22, "smart_phone_icon", "texture_diffuseN", "icons/icon_smart_phone.png"],
    [23, "smart_watch_icon", "texture_diffuseN", "icons/icon_smart_watch.png"],
    [24, "tablet_icon", "texture_diffuseN", "icons/icon_tablet.png"],
    [25, "webcam_icon", "texture_diffuseN", "icons/icon_webcam.png"],
    [26, "wifi_icon", "texture_diffuseN", "icons/icon_wifi.png"],
    [27, "item_icon", "texture_diffuseN", "icons/icon_item.png"],
    [28, "landline_icon", "texture_diffuseN", "icons/icon_landline.png"],
    [29, "light_grey", "texture_diffuseN", "textures/light_grey.jpg"],
    [30, "man_billboard", "texture_diffuseN", "textures/man.jpg"],
    [31, "woman_billboard", "texture_diffuseN", "textures/woman.jpg"],
)