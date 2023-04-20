# -*- coding: utf-8 -*-

"""
Constants used in Sphere_IOT project.

These constants include camera properties for the OpenGL shaders. Dictionary with shader data and lists with textures
and resources data.

"""
SPHERE_SMALL_RADIUS = 0.01
SPHERE_RADIUS = 3
NODE_DISC_RADIUS = 0.075
SOCKET_RADIUS = 0.015
HOVER_MIN_DISTANCE = 10

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
    "edge": {"model_id": 10, "model_file_name": "line_1x1.obj", "shader": "EdgeShader",
              "vertex_shader": "vert_sphere_edge.glsl",
              "fragment_shader": "frag_sphere_edge.glsl", "geometry_shader": "none"},
    "cross_hair1": {"model_id": 11, "model_file_name": "vertex1.obj", "shader": "CrossShader",
                    "vertex_shader": "vert_circle.glsl",
                    "fragment_shader": "frag_circle.glsl", "geometry_shader": "geom_cross.glsl"},
    "cube": {"model_id": 12, "model_file_name": "vertex1.obj", "shader": "SphereShader",
             "vertex_shader": "vert_sphere.glsl",
             "fragment_shader": "frag_sphere.glsl", "geometry_shader": "none"},
    "cube_sphere": {"model_id": 13, "model_file_name": "cubesphere.obj", "shader": "SphereShader",
                    "vertex_shader": "vert_sphere.glsl",
                    "fragment_shader": "frag_sphere.glsl", "geometry_shader": "none"},
    "drag_edge": {"model_id": 10, "model_file_name": "sphere1.obj", "shader": "DragEdgeShader",
                  "vertex_shader": "vert_sphere.glsl",
                  "fragment_shader": "frag_sphere.glsl", "geometry_shader": "none"},
    "sphere_lines": {"model_id": 10, "model_file_name": "line_1x1.obj", "shader": "EdgeShader",
                     "vertex_shader": "vert_sphere_edge.glsl",
                     "fragment_shader": "frag_sphere_edge.glsl", "geometry_shader": "none"},
}

SHADER_SWITCH = {"node": 0, "sphere_base": 1, "square1x1": 2, "rubber_band": 2, "sphere_small":
                 1, "socket": 2, "cube": 1, "cube_sphere": 1}

EDGE_TYPE_DIRECT = 1
TRANSPARENCY_SMALL_SPHERES = 0.8
TRANSPARENCY_DETAIL_SPHERE = 0.5
