# -*- coding: utf-8 -*-

"""
Constants used in Sphere_IOT project.

These constants include camera properties for the OpenGL shaders. Dictionary with shader data and lists with textures
and resources data.

"""
SPHERE_SMALL_RADIUS = 0.01
SPHERE_RADIUS = 1
NODE_DISC_RADIUS = 0.075
SOCKET_RADIUS = 0.01
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
TEXTURES_DIR = "..//sphere_base/model/resources/textures/"
ICONS_DIR = "..//sphere_base/model/resources/icons/"
SPHERE_TEXTURE_DIR = "..//sphere_base/model/resources/sphere_textures/"
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
    "edge1": {"model_id": 10, "model_file_name": "line_1x1.obj", "shader": "DynamicShader",
             "vertex_shader": "vert_sphere_edge.glsl",
             "fragment_shader": "frag_sphere_edge.glsl", "geometry_shader": "none"},
    "cross_hair1": {"model_id": 11, "model_file_name": "vertex1.obj", "shader": "CrossShader",
                    "vertex_shader": "vert_circle.glsl",
                    "fragment_shader": "frag_circle.glsl", "geometry_shader": "geom_cross.glsl"},
    "cube": {"model_id": 12, "model_file_name": "vertex1.obj", "shader": "SphereShader",
             "vertex_shader": "vert_sphere.glsl",
             "fragment_shader": "frag_sphere.glsl", "geometry_shader": "none"},
}

SHADER_SWITCH = {"node": 0, "sphere_base": 1, "square1x1": 2, "rubber_band": 2, "sphere_small":
                 1, "socket": 2, "cube": 1}

EDGE_TYPE_DIRECT = 1
#
# # sphere_base colors
# LIGHT_GREEN = [0.07, 0.46, 0.24, 0.5]
# GREEN = [0.37, 0.56, 0.32, 0.5]
# BRIGHT_GREEN = [0.35, 0.8, 0.16, 0.5]
# LIGHT_GREY = [0.93, 0.87, 0.89, 0.5]
# GREY = [0.25, 0.26, 0.18, 0.5]
# BRIGHT_GREY = [0.64, 0.59, 0.63, 0.5]
# LIGHT_YELLOW = [0.81, 0.7, 0.46, 0.5]
# YELLOW = [0.88, 0.7, 0.13, 0.5]
# BRIGHT_YELLOW = [0.75, 0.95, 0.21, 0.5]
# LIGHT_ORANGE = [0.94, 0.44, 0.54, 0.5]
# ORANGE = [0.97, 0.44, 0.05, 0.5]
# BRIGHT_ORANGE = [0.94, 0.51, 0.07, 0.5]
# LIGHT_RED = [0.35, 0.13, 0.23, 0.5]
# RED = [0.6, 0.08, 0.08, 0.5]
# BRIGHT_RED = [0.99, 0.05, 0.38, 0.5]
# LIGHT_BLUE = [0.10, 0.40, 1.00, 0.5]
# BLUE = [0.10, 0.10, 1.00, 0.5]
# BRIGHT_BLUE = [0.30, 0.65, 1.00, 0.5]
#
# RELEVANCE_COLORS = {1: GREY, 2: BRIGHT_BLUE, 3: BRIGHT_GREEN, 4: LIGHT_YELLOW, 5: BRIGHT_RED, 6: LIGHT_GREEN}
# # RELEVANCE_COLORS = {1: LIGHT_GREEN, 2: GREEN, 3: BRIGHT_GREEN, 4: LIGHT_GREY, 5: GREY, 6: BRIGHT_GREY,
# #                     7: LIGHT_YELLOW, 8: YELLOW, 9: BRIGHT_YELLOW, 10: LIGHT_ORANGE, 11: ORANGE, 12: BRIGHT_ORANGE,
# #                     13: LIGHT_RED, 14: RED, 15: BRIGHT_RED}
#
# RELEVANCE_TEXTURE = {1: 29, 2: 4, 3: 6, 4: 3}

TRANSPARENCY_SMALL_SPHERES = 0.8
TRANSPARENCY_DETAIL_SPHERE = 0.5
