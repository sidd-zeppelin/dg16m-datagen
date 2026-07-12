# DG16M Data Generation (dg16m-datagen)

This repository contains the dataset generation pipeline for the DG16M dataset (dual-arm force-optimized grasps).

---

## Setup

We use `uv` to manage dependencies. From within the `dg16m-datagen` directory, simply run:
```bash
uv sync
```
*Note: This automatically handles all dependencies and sets up the local `meshpy` package from `core/` in editable mode.*

---

## Generating Data (`main.py`)

The `main.py` script samples grasps and performs force-closure optimization using Dex-Net and CVXPY. It outputs `.h5` files containing the successful grasps, contact points, and wrench statistics.

**Option 1: Process a single object**
```bash
uv run python main.py --mesh ../DG16M-dataset/meshes/1.obj --output-dir output/
```

**Option 2: Process a full directory of objects**
```bash
uv run python main.py --meshes-dir ../DG16M-dataset/meshes --num-workers 16 --output-dir output/
```

**Option 3: Use config fallback**
If you don't provide arguments, the script will read defaults from `config.yaml`:
```bash
uv run python main.py
```

### Key Arguments:
- `--mesh`: Path to a single `.obj` file.
- `--meshes-dir`: Path to a folder of `.obj` meshes.
- `--output-dir`: Where to save the output files (defaults to `output/`).
- `--num-workers`: Number of CPU processes for the parallel optimization solver.
- `--target-grasps`: The initial number of antipodal grasps to sample before optimization.

---

## Visualizing Data (`visualize.py`)

The `visualize.py` script renders an interactive 3D scene directly to your web browser (zero dependencies required outside of Python).

**Basic Visualization**
Provide the mesh and the generated `.h5` grasps file:
```bash
uv run python visualize.py --mesh ../DG16M-dataset/meshes/1.obj --grasps output/grasps/1.h5
```
*(Passing grasps will be highlighted in **green**, and failing grasps in **red**)*

**Filtering Visualizations**
To avoid a cluttered scene (especially with thousands of grasps), you can filter the output:
```bash
# Only render passing grasps
uv run python visualize.py --mesh ../DG16M-dataset/meshes/1.obj --grasps output/grasps/1.h5 --passing-grasps

# Only render failing grasps
uv run python visualize.py --mesh ../DG16M-dataset/meshes/1.obj --grasps output/grasps/1.h5 --failing-grasps

# Cap the visualization at 50 grasps per category for faster rendering
uv run python visualize.py --mesh ../DG16M-dataset/meshes/1.obj --grasps output/grasps/1.h5 --max-grasps 50
```

*Note: The script natively exports the 3D scene to a temporary HTML file and automatically opens it in your default web browser!*