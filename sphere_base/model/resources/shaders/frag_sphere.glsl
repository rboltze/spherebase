#version 330 core
struct Material {
                    vec3 ambient;
                    vec3 diffuse;
                    vec3 specular;
                    float shininess;
                 };

// Interpolated values from the vertex shaders
in vec2 UV;
in vec3 Position_world_space;
in vec3 Normal_camera_space;
in vec3 EyeDirection_camera_space;
in vec3 LightDirection_camera_space;
in vec4 v_color;

// Output data
out vec4 color;
out vec3 FragColor;

// Values that stay constant for the whole mesh.
uniform sampler2D myTextureSampler;
uniform vec3 LightPosition_world_space;
//uniform Material material;
uniform vec3 LightColor = vec3(1, 1, 1);
//uniform vec3 object_color;
uniform Material material;
uniform int switcher;

uniform sampler2D texture_diffuse1;
uniform sampler2D texture_diffuse2;
uniform sampler2D texture_diffuse3;
uniform sampler2D texture_specular1;
uniform sampler2D texture_specular2;

void main()
{

    // Light emission properties
    // You probably want to put them as uniforms
    float LightPower = 10000.0f;

    // Material properties
    vec3 MaterialDiffuseColor = texture( myTextureSampler, UV).rgb;
    vec3 MaterialAmbientColor = vec3(0.3, 0.3, 0.3) * MaterialDiffuseColor;
    vec3 MaterialSpecularColor = vec3(0.3, 0.3, 0.3);

    // Distance to the light
    float distance = length( LightPosition_world_space - Position_world_space );

    // Normal of the computed fragment, in camera space
    vec3 n = normalize( Normal_camera_space );
    // Direction of the light (from the fragment to the light)
    vec3 l = normalize( LightDirection_camera_space );
    // Cosine of the angle between the normal and the light direction,
    // clamped above 0
    //  - light is at the vertical of the triangle -> 1
    //  - light is perpendicular to the triangle -> 0
    //  - light is behind the triangle -> 0
    float cosTheta = clamp(dot( n,l ), 0, 1);

    // Eye vector (towards the camera)
    vec3 E = normalize(EyeDirection_camera_space);
    // Direction in which the triangle reflects the light
    vec3 R = reflect(-l, n);
    // Cosine of the angle between the Eye vector and the Reflect vector,
    // clamped to 0
    //  - Looking into the reflection -> 1
    //  - Looking elsewhere -> < 1
    float cosAlpha = clamp(dot(E, R), 0,1);

    if (switcher == 0) {
        FragColor = MaterialAmbientColor + MaterialDiffuseColor * vec3(0.5, 0.5, 0.5);
        color = vec4(FragColor, 1);
        }
    else if (switcher == 1) {
        FragColor =
            // Ambient : simulates indirect lighting
            MaterialAmbientColor +
            // Diffuse : "color" of the object
            MaterialDiffuseColor * LightColor * LightPower * cosTheta / (distance*distance) +
            // Specular : reflective highlight, like a mirror
            MaterialSpecularColor * LightColor * LightPower * pow(cosAlpha,5) / (distance*distance);
        color = vec4(FragColor, 1.0);
        }
    else if (switcher == 2) {
        color = v_color;
    }
        else if (switcher == 3) {
        color = v_color;
    }

}
