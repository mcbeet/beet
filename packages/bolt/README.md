# Bolt

[![GitHub Actions](https://github.com/mcbeet/bolt/workflows/CI/badge.svg)](https://github.com/mcbeet/bolt/actions)
[![PyPI](https://img.shields.io/pypi/v/bolt.svg)](https://pypi.org/project/bolt/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bolt.svg)](https://pypi.org/project/bolt/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
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

Contributions are welcome. Make sure to first open an issue discussing the problem or the new feature before creating a pull request. The project uses [`poetry`](https://python-poetry.org/).

```bash
$ poetry install
```

You can run the tests with `poetry run pytest`.

```bash
$ poetry run pytest
```

The project must type-check with [`pyright`](https://github.com/microsoft/pyright). If you're using VSCode the [`pylance`](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) extension should report diagnostics automatically. You can also install the type-checker locally with `npm install` and run it from the command-line.

```bash
$ npm run watch
$ npm run check
```

The code follows the [`black`](https://github.com/psf/black) code style. Import statements are sorted with [`isort`](https://pycqa.github.io/isort/).

```bash
$ poetry run isort bolt tests
$ poetry run black bolt tests
$ poetry run black --check bolt tests
```

---

License - [MIT](https://github.com/mcbeet/bolt/blob/main/LICENSE)
