function_tag minecraft:tick {
    "values": [
        "demo:foo"
    ]
}

say hello

function demo:bar:
    say world

merge function_tag minecraft:tick {
    "values": [
        "demo:bar"
    ]
}

prepend function_tag minecraft:tick {
    "values": [
        "demo:before"
    ]
}

append function_tag minecraft:tick {
    "values": [
        "demo:after"
    ]
}


function_tag demo:abc {
    "values": [
        "demo:foo"
    ]
}

function_tag demo:abc {
    "values": [
        "demo:foo"
    ]
}

glsl_shader minecraft:include/matrix:
    #version 150

    mat2 mat2_rotate_z(float radians) {
        return mat2(
            cos(radians), -sin(radians),
            sin(radians), cos(radians)
        );
    }

fragment_shader minecraft:core/blit_screen:
    #version 150

    uniform sampler2D DiffuseSampler;

    uniform vec4 ColorModulator;

    in vec2 texCoord;
    in vec4 vertexColor;

    out vec4 fragColor;

    void main() {
        vec4 color = texture(DiffuseSampler, texCoord) * vertexColor;

        // blit final output of compositor into displayed back buffer
        fragColor = color * ColorModulator;
    }

vertex_shader minecraft:core/blit_screen:
    #version 150

    in vec3 Position;
    in vec2 UV;
    in vec4 Color;

    uniform mat4 ModelViewMat;
    uniform mat4 ProjMat;

    out vec2 texCoord;
    out vec4 vertexColor;

    void main() {
        gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);

        texCoord = UV;
        vertexColor = Color;
    }
