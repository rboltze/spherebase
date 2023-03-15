#version 330 core

layout(location = 0) in vec3 aPos;
layout(location = 1) in vec2 aTexCoord;

out vec2 TexCoord;
out vec4 v_color;

uniform mat4 model;
uniform mat4 transform;
uniform vec4 a_color;

void main()
{

    gl_Position = model * transform * vec4(aPos, 1.0);
    TexCoord = aTexCoord;
    v_color = a_color;
}