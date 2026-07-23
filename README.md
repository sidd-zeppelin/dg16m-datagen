# DG16M Data Generation

Generate dual-arm force-optimised grasps. Antipodal grasp sampling via
Dex-Net, force-closure evaluation via convex optimisation.

## Quick start

```bash
uv sync
uv run main.py --mesh path/to/mesh.obj
uv run main.py --meshes-dir path/to/meshes --num-workers 16
```

## Documentation

```bash
uv run mkdocs serve
```

Then open <http://127.0.0.1:8000> in your browser.

## Credits

* **[Dex-Net](https://github.com/BerkeleyAutomation/dex-net)** (Mahler et al., UC Berkeley Autolab) — `core/scripts/dexnet/`: grasping framework, antipodal sampling, gripper models.
* **[meshpy](https://github.com/BerkeleyAutomation/meshpy)** (UC Berkeley Autolab) — vendored in `core/meshpy/`: mesh I/O and representation.
* **[ACRONYM](https://github.com/NVlabs/acronym)** (NVIDIA) — `core/scripts/DA2_tools/` scene utilities, modified by Guangyao Zhai.
