#version 330 core

in vec2 TexCoord;
in vec4 f_color;

out vec4 color;
out vec4 FragColor;

uniform sampler2D texture1;
uniform int switcher;

void main()
{
    vec4 texColor = texture(texture1, TexCoord);
    color = f_color;
}