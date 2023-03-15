#version 330 core

// used with the rubber band box

layout (points) in;
layout (line_strip, max_vertices = 5) out;

in vec4 v_color[];
out vec4 f_color;

uniform vec3 scale;

void build_box(vec4 position)
{

    f_color = v_color[0];
    vec4 new_position = gl_in[0].gl_Position;
    gl_Position = new_position + vec4(-scale[0] / 2, scale[1] / 2, 0.0, 0.0);    // 1:bottom-left
    EmitVertex();
    gl_Position = new_position + vec4( scale[0] / 2, scale[1] / 2, 0.0, 0.0);    // 2:bottom-right
    EmitVertex();
    gl_Position = new_position + vec4(scale[0] / 2, -scale[1] / 2, 0.0, 0.0);    // 3:top-right
    EmitVertex();
    gl_Position = new_position + vec4(-scale[0] / 2, -scale[1] / 2, 0.0, 0.0);    // 4:top-left
    EmitVertex();
    gl_Position = new_position + vec4( -scale[0] / 2, scale[1] / 2, 0.0, 0.0);    // 5:bottom-left
    EmitVertex();
    EndPrimitive();


}

void main() {
    build_box(gl_in[0].gl_Position);
}
