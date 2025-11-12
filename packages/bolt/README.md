# Bolt

[![GitHub Actions](https://github.com/mcbeet/beet/workflows/CI/badge.svg)](https://github.com/mcbeet/beet/actions)
[![PyPI](https://img.shields.io/pypi/v/bolt.svg)](https://pypi.org/project/bolt/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bolt.svg)](https://pypi.org/project/bolt/)
[![Discord](https://img.shields.io/discord/900530660677156924?color=7289DA&label=discord&logo=discord&logoColor=fff)](https://discord.gg/98MdSGMm8j)

> Supercharge Minecraft commands with Python.

```python
infinite_invisibility = {
    Id: 14,
    Duration: 999999,
    Amplifier: 1,
    ShowParticles: false,
}

def summon_chicken_army(n):
    for i in range(n):
        summon chicken ~i ~ ~ {
            Tags: [f"quack{i}"],
            IsChickenJockey: true,
            Passengers: [{
                id: zombie,
                IsBaby: true,
                ActiveEffects: [infinite_invisibility]
            }]
        }

say Go forth, my minions!
summon_chicken_army(16)
```

## Installation

The package can be installed with `pip`.

```bash
$ pip install bolt
```

## Contributing

Contributions are welcome. Make sure to first open an issue discussing the problem or the new feature before creating a pull request. The project uses [`uv`](https://github.com/astral-sh/uv).

```console
$ uv sync
```

You can run the tests with `uv run pytest`.

```console
$ uv run pytest
```

The code is formatted and checked with [`ruff`](https://github.com/astral-sh/ruff).

```console
$ uv run ruff format
$ uv run ruff check
```

---

License - [MIT](https://github.com/mcbeet/beet/blob/main/packages/bolt/LICENSE)
