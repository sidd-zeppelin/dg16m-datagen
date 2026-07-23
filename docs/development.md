# Development guide

## Code structure

| Path | Role |
|---|---|
| `main.py` | CLI entry, config loading, iteration over meshes |
| `core/scripts/generate_dg16m.py` | Pipeline orchestration (`f()` — the main function) |
| `core/scripts/dexnet/` | Vendored Dex-Net (grasp sampling, gripper models, database) |
| `core/scripts/grasp_optimization/` | Force-closure optimisation (cvxpy) |
| `core/scripts/DA2_tools/` | ACRONYM utilities (marker generation) |
| `core/meshpy/` | Vendored meshpy (mesh I/O, SDF, stable poses) |
| `grippers/` | Gripper model definitions (only `robotiq_85`) |
| `config.yaml` | All user-facing configuration |
| `docs/` | Documentation (this section) |

## Modifying the FC optimisation

The FC solver lives in `force_closure_optmization.fc_optimization()`. To
change the formulation:

- **Friction model**: toggle `soft_contact` (currently hard-coded to
  `False` in `check_contact_points_parallel.py`).
- **Force limits**: adjust `f_high` in `fc_optimization()`.
- **Gravity direction**: the `orientation` parameter selects which axis
  gravity acts along.

## Running a subset of grasps

For quick iteration during development, pass small numbers via CLI:

```bash
uv run main.py --mesh test.obj --num-sampled-grasps 30 --num-positive 5 --num-negative 5
```

## Debugging the sampler

Set `--debug` (or `DG16M_DEBUG=1`) to print detailed per-grasp diagnostics
from the antipodal sampler, including why individual grasps were accepted or
rejected.

## Generating this documentation

```bash
mkdocs serve     # live preview
mkdocs build     # static site in site/
```
