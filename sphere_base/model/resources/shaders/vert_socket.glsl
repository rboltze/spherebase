#version 330 core

layout(location = 0) in vec3 vertexPosition_model_space;
layout(location = 1) in vec2 aTexCoord;
layout(location = 2) in vec3 vertexNormal_model_space;

out vec2 TexCoord;
out vec4 v_color;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;
uniform mat4 transform;
uniform vec4 a_color;


void main()
{

        gl_Position = projection * view * model * transform * vec4(vertexPosition_model_space, 1.0);

        TexCoord = aTexCoord;
        v_color = a_color;

}
