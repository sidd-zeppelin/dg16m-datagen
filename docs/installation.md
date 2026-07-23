# Installation

## Prerequisites

- Python ≥ 3.12
- [uv](https://docs.astral.sh/uv/)
- On **NixOS**: `nix` with flakes enabled (provides `libxcb`, `glib`, Qt
  shared libraries that OpenCV / mayavi need at runtime).

## Setup

```bash
git clone <repo-url> && cd dg16m-datagen
uv sync
```

On NixOS, wrap all commands with the flake:

```bash
nix develop -c ...
# e.g.
nix develop -c uv sync
nix develop -c uv run main.py --mesh path/to/mesh.obj
```

## Verify

```bash
uv run python -c "from generate_dg16m import f; print('OK')"
```

If you see import warnings about ROS, mayavi, OpenRAVE, gqcnn or pyhull,
those are harmless — those features are not used by this pipeline.
