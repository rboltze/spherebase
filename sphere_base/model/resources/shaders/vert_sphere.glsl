#version 330 core

// Input vertex data, different for all executions of this shader.
layout(location = 0) in vec3 vertexPosition_model_space;
layout(location = 1) in vec2 vertexUV;
layout(location = 2) in vec3 vertexNormal_model_space;
// layout(location = 3) in vec3 a_color;

// Output data ; will be interpolated for each fragment.
out vec2 UV;
out vec3 Position_world_space;
out vec3 Normal_camera_space;
out vec3 EyeDirection_camera_space;
out vec3 LightDirection_camera_space;
out vec4 v_color;

// Values that stay constant for the whole mesh.
uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;
uniform mat4 transform;
uniform vec4 a_color;
uniform vec3 LightPosition_world_space;
uniform int switcher;

void main()
{
    if (switcher == 3) {
        gl_Position = projection * view * vec4(vertexPosition_model_space, 1.0);

        vec3 vertexPosition_camera_space = ( view * model * vec4(vertexPosition_model_space,1)).xyz;
        EyeDirection_camera_space = vec3(0, 0, 0) - vertexPosition_camera_space;

        vec3 LightPosition_camera_space = ( view * vec4(LightPosition_world_space,1)).xyz;
        LightDirection_camera_space = LightPosition_camera_space + EyeDirection_camera_space;

        Normal_camera_space = ( view * model * transform * vec4(vertexNormal_model_space, 0)).xyz;
        UV = vertexUV;
        v_color = vec4(a_color);
    }
    else {

        // Output position of the vertex, in clip space : MVP * position
        gl_Position = projection * view * model * transform * vec4(vertexPosition_model_space, 1.0);

        Position_world_space = (model * vec4(vertexPosition_model_space,1)).xyz;

        // Vector that goes from the vertex to the camera, in camera space.
        // In camera space, the camera is at the origin (0,0,0).
        vec3 vertexPosition_camera_space = ( view * model * vec4(vertexPosition_model_space,1)).xyz;
        EyeDirection_camera_space = vec3(0,0,0) - vertexPosition_camera_space;

        // Vector that goes from the vertex to the light, in camera space.
        vec3 LightPosition_camera_space = ( view * vec4(LightPosition_world_space,1)).xyz;
        LightDirection_camera_space = LightPosition_camera_space + EyeDirection_camera_space;

        // Normal of the the vertex, in camera space
        // Only correct if ModelMatrix does not scale the model ! Use its inverse transpose if not.
        Normal_camera_space = ( view * model * transform * vec4(vertexNormal_model_space, 0)).xyz;

        // UV of the vertex. No special space for this one.
        UV = vertexUV;

        // color
        v_color = vec4(a_color);
    }

}
