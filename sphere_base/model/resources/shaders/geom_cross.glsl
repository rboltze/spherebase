#version 330 core

layout(points) in;
layout(line_strip, max_vertices = 61) out;

in vec4 v_color[];
out vec4 f_color;

const float PI = 3.1415926;
uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;
uniform mat4 transform;


void main()
{
    f_color = v_color[0];
    float ang = PI * 2.0 / 60.0 * 0;
    vec4 offset = vec4(cos(ang) * 0.15, -sin(ang) * 0.14, 0.0, 0.0);
    vec4 new_position = gl_in[0].gl_Position + vec4(-0.025, 0.0, 0.0, 0.0) + offset;
    gl_Position = projection * view * model * transform * new_position;
    EmitVertex();
    offset = vec4(cos(ang) * 0.15, -sin(ang) * 0.14, 0.0, 0.0);
    new_position = gl_in[0].gl_Position + vec4( 0.025, 0.0, 0.0, 0.0) + offset;
    gl_Position = projection * view * model * transform * new_position;
    EmitVertex();
    EndPrimitive();

    ang = PI * 2.0 / 60.0 * 30;
    offset = vec4(cos(ang) * 0.15, -sin(ang) * 0.14, 0.0, 0.0);
    new_position = gl_in[0].gl_Position + vec4( -0.025, 0.0, 0.0, 0.0) + offset;
    gl_Position = projection * view * model * transform * new_position;
    EmitVertex();
    offset = vec4(cos(ang) * 0.15, -sin(ang) * 0.14, 0.0, 0.0);
    new_position = gl_in[0].gl_Position + vec4( 0.025, 0.0, 0.0, 0.0) + offset;
    gl_Position = projection * view * model * transform * new_position;
    EmitVertex();
    EndPrimitive();

    ang = PI * 2.0 / 60.0 * 15;
    offset = vec4(cos(ang) * 0.15, -sin(ang) * 0.14, 0.0, 0.0);
    new_position = gl_in[0].gl_Position + vec4( 0.0, -0.025, 0.0, 0.0) + offset;
    gl_Position = projection * view * model * transform * new_position;
    EmitVertex();
    offset = vec4(cos(ang) * 0.15, -sin(ang) * 0.14, 0.0, 0.0);
    new_position = gl_in[0].gl_Position + vec4( 0.0, 0.025, 0.0, 0.0) + offset;
    gl_Position = projection * view * model * transform * new_position;
    EmitVertex();
    EndPrimitive();

    ang = PI * 2.0 / 60.0 * 45;
    offset = vec4(cos(ang) * 0.15, -sin(ang) * 0.14, 0.0, 0.0);
    new_position = gl_in[0].gl_Position + vec4( 0.0, -0.025, 0.0, 0.0) + offset;
    gl_Position = projection * view * model * transform * new_position;
    EmitVertex();
    offset = vec4(cos(ang) * 0.15, -sin(ang) * 0.14, 0.0, 0.0);
    new_position = gl_in[0].gl_Position + vec4( 0.0, 0.025, 0.0, 0.0) + offset;
    gl_Position = projection * view * model * transform * new_position;
    EmitVertex();
    EndPrimitive();

}