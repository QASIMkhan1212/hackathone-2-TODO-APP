# Python Packaging & Distribution

## Modern pyproject.toml

### Complete Example

```toml
[project]
name = "my-package"
version = "1.0.0"
description = "A useful Python package"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "Your Name", email = "you@example.com"},
]
keywords = ["utility", "tools"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "pydantic>=2.0",
    "httpx>=0.25",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1",
    "mypy>=1.0",
    "pre-commit>=3.0",
]
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
]

[project.scripts]
my-cli = "my_package.cli:main"

[project.entry-points."my_package.plugins"]
plugin1 = "my_package.plugins:Plugin1"

[project.urls]
Homepage = "https://github.com/user/my-package"
Documentation = "https://my-package.readthedocs.io"
Repository = "https://github.com/user/my-package"
Issues = "https://github.com/user/my-package/issues"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]
```

---

## Project Layouts

### Src Layout (Recommended)

```
my-package/
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── core.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_core.py
├── pyproject.toml
├── README.md
└── LICENSE
```

### Flat Layout

```
my-package/
├── my_package/
│   ├── __init__.py
│   └── core.py
├── tests/
├── pyproject.toml
└── README.md
```

---

## Build Backends

### Hatchling (Recommended)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.sdist]
include = ["/src"]

[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]
```

### Setuptools

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

### Poetry

```toml
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "my-package"
version = "1.0.0"
packages = [{include = "my_package", from = "src"}]
```

---

## Version Management

### Static Version

```toml
[project]
version = "1.0.0"
```

### Dynamic Version from __init__.py

```toml
[project]
dynamic = ["version"]

[tool.hatch.version]
path = "src/my_package/__init__.py"
```

```python
# src/my_package/__init__.py
__version__ = "1.0.0"
```

### Dynamic Version from Git

```toml
[project]
dynamic = ["version"]

[tool.hatch.version]
source = "vcs"

[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"
```

---

## Building & Publishing

### Build Package

```bash
# Install build tool
pip install build

# Build sdist and wheel
python -m build

# Output in dist/
# - my_package-1.0.0.tar.gz (sdist)
# - my_package-1.0.0-py3-none-any.whl (wheel)
```

### Publish to PyPI

```bash
# Install twine
pip install twine

# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

### Using Trusted Publishing (GitHub Actions)

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for trusted publishing

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install build tools
        run: pip install build

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

---

## Entry Points

### CLI Scripts

```toml
[project.scripts]
my-cli = "my_package.cli:main"
my-tool = "my_package.tools:cli"
```

```python
# src/my_package/cli.py
import typer

app = typer.Typer()

@app.command()
def main():
    print("Hello from CLI!")

if __name__ == "__main__":
    app()
```

### Plugin System

```toml
[project.entry-points."my_package.plugins"]
builtin = "my_package.plugins.builtin:BuiltinPlugin"
```

```python
# Discover plugins
from importlib.metadata import entry_points

def load_plugins():
    eps = entry_points(group="my_package.plugins")
    plugins = {}
    for ep in eps:
        plugins[ep.name] = ep.load()
    return plugins
```

---

## Dependencies

### Required Dependencies

```toml
[project]
dependencies = [
    "requests>=2.28",
    "pydantic>=2.0,<3.0",
    "numpy~=1.24",  # Compatible release
]
```

### Optional Dependencies

```toml
[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]
docs = ["mkdocs", "mkdocs-material"]
all = ["my-package[dev,docs]"]
```

```bash
# Install with extras
pip install my-package[dev]
pip install -e ".[dev,docs]"
```

---

## Private Packages

### Install from Git

```bash
pip install git+https://github.com/user/private-repo.git
pip install git+https://github.com/user/repo.git@v1.0.0
pip install git+https://github.com/user/repo.git@main#subdirectory=pkg
```

### Install from Private PyPI

```bash
pip install --index-url https://pypi.company.com/simple/ my-package
```

### pyproject.toml with Private Index

```toml
# Not directly supported, use pip.conf or requirements.txt
```

---

## Package Metadata

### __init__.py

```python
"""My Package - A useful Python library."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "you@example.com"

from .core import main_function
from .models import MyModel

__all__ = ["main_function", "MyModel"]
```

### Runtime Metadata Access

```python
from importlib.metadata import version, metadata

# Get version
pkg_version = version("my-package")

# Get full metadata
meta = metadata("my-package")
print(meta["Summary"])
print(meta["Author-email"])
```

---

## Best Practices

### Include/Exclude Files

```toml
[tool.hatch.build.targets.sdist]
include = [
    "/src",
    "/tests",
    "README.md",
    "LICENSE",
]
exclude = [
    "*.pyc",
    "__pycache__",
    ".git",
]
```

### Type Stubs (py.typed)

```
src/my_package/
├── __init__.py
├── py.typed        # Marker file for PEP 561
└── core.py
```

### MANIFEST.in (for setuptools)

```
include LICENSE
include README.md
recursive-include src *.py *.typed
recursive-exclude tests *
```
