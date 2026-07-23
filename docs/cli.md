# CLI Reference

## Usage

```bash
uv run main.py [OPTIONS]
```

## Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--mesh` | `str` | — | Path to a single `.obj` file. |
| `--meshes-dir` | `str` | `config.yaml meshes_path` | Directory of `.obj` files to process. |
| `--output-dir` | `str` | `config.yaml output_path` | Root output directory. |
| `--num-sampled-grasps` | `int` | `config.yaml num_sampled_grasps` | Number of grasps to sample per object. |
| `--num-positive` | `int` | `config.yaml num_positive` | Number of FC-passing grasps to save. |
| `--num-negative` | `int` | `config.yaml num_negative` | Number of FC-failing grasps to save. |
| `--num-workers` | `int` | `config.yaml num_workers` | CPU worker processes. |
| `--debug` / `--no-debug` | flag | `config.yaml debug` | Enable verbose sampler diagnostics. |

## Examples

### Single object

```bash
uv run main.py --mesh my_mesh.obj
```

Output goes to `output/grasps/my_mesh.h5`.

### Batch processing

```bash
uv run main.py --meshes-dir ../DG16M-dataset/meshes --num-workers 16
```

### Override everything via CLI

```bash
uv run main.py --mesh model.obj --output-dir results --num-sampled-grasps 1000 \
    --num-positive 500 --num-negative 500 --num-workers 4 --debug
```

### Use defaults from config.yaml

```bash
uv run main.py
```

Processes all `.obj` files found in `config.yaml`'s `meshes_path`.

## Environment variables

| Variable | Description |
|---|---|
| `DG16M_DEBUG` | Set to `1` to enable verbose antipodal-sampler diagnostics (equivalent to `--debug`). Inherited by spawned worker processes. |
