# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 26,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say hello
```

`@function demo:bar`

```mcfunction
say world
```

`@function_tag demo:abc`

```json
{
  "values": [
    "demo:foo"
  ]
}
```

### minecraft

`@function_tag minecraft:tick`

```json
{
  "values": [
    "demo:before",
    "demo:foo",
    "demo:bar",
    "demo:after"
  ]
}
```

## Resource pack

`@resource_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 22,
    "description": ""
  }
}
```

### minecraft

`@glsl_shader minecraft:include/matrix`

```glsl
#version 150

mat2 mat2_rotate_z(float radians) {
    return mat2(
        cos(radians), -sin(radians),
        sin(radians), cos(radians)
    );
}
```

`@fragment_shader minecraft:core/blit_screen`

```glsl
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
```

`@vertex_shader minecraft:core/blit_screen`

```glsl
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
```
