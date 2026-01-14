# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      94,
      1
    ],
    "max_format": [
      94,
      1
    ],
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
    "min_format": [
      75,
      0
    ],
    "max_format": [
      75,
      0
    ],
    "description": ""
  }
}
```

### minecraft

`@model minecraft:item/bow`

```json
{
  "parent": "item/generated",
  "textures": {
    "layer0": "item/bow"
  },
  "display": {
    "thirdperson_righthand": {
      "rotation": [
        -80,
        260,
        -40
      ],
      "translation": [
        -1,
        -2,
        2.5
      ],
      "scale": [
        0.9,
        0.9,
        0.9
      ]
    },
    "thirdperson_lefthand": {
      "rotation": [
        -80,
        -280,
        40
      ],
      "translation": [
        -1,
        -2,
        2.5
      ],
      "scale": [
        0.9,
        0.9,
        0.9
      ]
    },
    "firstperson_righthand": {
      "rotation": [
        0,
        -90,
        25
      ],
      "translation": [
        1.13,
        3.2,
        1.13
      ],
      "scale": [
        0.68,
        0.68,
        0.68
      ]
    },
    "firstperson_lefthand": {
      "rotation": [
        0,
        90,
        -25
      ],
      "translation": [
        1.13,
        3.2,
        1.13
      ],
      "scale": [
        0.68,
        0.68,
        0.68
      ]
    }
  },
  "overrides": [
    {
      "predicate": {
        "custom_model_data": 1
      },
      "model": "demo:item/cool_bow"
    },
    {
      "predicate": {
        "pulling": 1
      },
      "model": "item/bow_pulling_0"
    },
    {
      "predicate": {
        "custom_model_data": 1,
        "pulling": 1
      },
      "model": "demo:item/cool_bow_pulling_0"
    },
    {
      "predicate": {
        "pulling": 1,
        "pull": 0.65
      },
      "model": "item/bow_pulling_1"
    },
    {
      "predicate": {
        "custom_model_data": 1,
        "pulling": 1,
        "pull": 0.65
      },
      "model": "demo:item/cool_bow_pulling_1"
    },
    {
      "predicate": {
        "pulling": 1,
        "pull": 0.9
      },
      "model": "item/bow_pulling_2"
    },
    {
      "predicate": {
        "custom_model_data": 1,
        "pulling": 1,
        "pull": 0.9
      },
      "model": "demo:item/cool_bow_pulling_2"
    }
  ]
}
```

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
