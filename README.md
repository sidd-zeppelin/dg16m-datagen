# DG16M Data Generation

This repository contains the dataset generation pipeline for the DG16M dataset. It generates dual arm force optimized grasps.

## Setup

We use uv to manage dependencies. Run this command inside the directory.

```bash
uv sync
```

## Generating Data

The main script samples grasps. It also performs force closure optimization. It outputs h5 files with successful grasps, contact points, and wrench statistics.

### Run on a single object

```bash
uv run python main.py --mesh ../DG16M-dataset/meshes/1.obj --output-dir output/
```

### Run on a folder of objects

```bash
uv run python main.py --meshes-dir ../DG16M-dataset/meshes --num-workers 16 --output-dir output/
```

### Run with config defaults

```bash
uv run python main.py
```

### Arguments

* mesh: Path to a single obj file.
* meshes dir: Path to a folder of obj meshes.
* output dir: Location to save output files.
* num workers: Number of CPU processes to use.
* target grasps: Number of initial grasps to sample.

## Visualizing Data

You can use the Jupyter notebook to visualize the generated grasps.

Open the notebook.

```bash
uv run jupyter notebook visualize_grasps.ipynb
```

The notebook has blocks to visualize one passing grasp, one failing grasp, or all grasps.