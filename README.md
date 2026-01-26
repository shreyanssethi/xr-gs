# Cross-Resolution Gaussian Splatting (XR-GS)

**XR-GS** extends 3D Gaussian Splatting to handle **mixed-resolution input views**, enabling models to learn **global structure from low-resolution images** while preserving **fine detail from high-resolution anchors**.

This project was developed as part of **16-825: Learning for 3D Vision (CMU)** and explores resolution-aware optimization strategies for real-world capture scenarios, where uniform image resolution is rarely guaranteed.

<p align="center">
  <a href="assets/XRGS Final Report.pdf">📘 Read the final report</a>
</p>

---

<p align="center">
  <img src="assets/XRGS Poster Presentation.png" alt="XR-GS Poster" width="100%">
</p>

---

## Overview

Modern Gaussian Splatting methods assume all training views share the same resolution. In practice, real captures often mix:
- **High-resolution (HR)** views (optical zoom, close-ups, better sensors)
- **Low-resolution (LR)** views (digital zoom, compression, wide shots)

Naively optimizing across these views leads to hallucinated details, over-sharpening, unnecessary Gaussian growth, and unstable geometry.  
**XR-GS introduces resolution-aware training strategies** to address these issues.

---

## Key Contributions

### Data
- Created a **synthetic mixed-resolution benchmark** from the LLFF dataset by simulating HR/LR views
- Captured **two real-world scenes** under true mixed-resolution conditions (zoomed-in HR + distant LR views)

### Resolution-Aware Training
XR-GS introduces several modifications to the standard Gaussian Splatting pipeline:

- **Adaptive loss weighting & gradient scaling**  
  Prevents LR views from overwhelming HR supervision

- **Resolution-aware densification & pruning**
  - More lenient densification for HR views
  - Easier pruning for LR views to avoid noise-driven growth

- **LR-only warm-up phase (curriculum learning)**
  Encourages learning stable global structure before HR refinement

- **Cross-resolution consistency loss**
  Inspired by image pyramids: rendered views are upsampled/downsampled and supervised across scales to enforce structural consistency

---

## Results & Observations

- **Significant reductions** in:
  - Number of Gaussians
  - Training time
  - Memory usage
- **Comparable SSIM / PSNR** to baseline Gaussian Splatting  
  (with some degradation in LPIPS)
- Performs best on **cluttered, highly textured scenes**
- Underperforms on **low-texture or single-object scenes**, where HR detail supervision dominates

For full quantitative results and ablations, see the **final report** linked above.

---
## 🔧 Environment Setup  
These commands have been **verified on an AWS Ubuntu instance with CUDA**.

```bash
conda env create -f environment.yml
pip install git+https://github.com/nerfstudio-project/gsplat.git
cd gsplat/
pip install --no-build-isolation -e .

pip install git+https://github.com/rahul-goel/fused-ssim@328dc9836f513d00c4b5bc38fe30478b4435cbb5
pip install git+https://github.com/nerfstudio-project/nerfview@4538024fe0d15fd1a0e4d760f3695fc44ca72787
pip install git+https://github.com/rmbrualla/pycolmap@cc7ea4b7301720ac29287dbe450952511b32125e
pip install git+https://github.com/harry7557558/fused-bilagrid@90f9788e57d3545e3a033c1038bb9986549632fe

sudo apt install colmap
export QT_QPA_PLATFORM=offscreen
```
---

## 1. Pre-process Images to Simulate Mixed Resolution

```
python scripts/preprocess_mixed_res.py --in_dir data/nerf_llff_data/fern/images --out_dir data/nerf_llff_data/fern_xrgs
```
- See the script for optional arguments such as: `base_factor`, `highrest_pct`, `extra_factor`, etc.
- `in_dir` must point to a directory containing all desired images (Should all be the same resolution right now)
- This will create an `/images` subdir and a `mixed_res_metadata.json` 

## 2. Run COLMAP on mixed-resolution images

```
python scripts/run_colmap.py --dataset_dir data/nerf_llff_data/fern_xrgs
```
- The `dataset_dir` must contain an `/images` subdir (If you ran Step 1, this is already handled)
- This script runs the colmap feature extractor, exhaustive matcher and matcher
- It will generate a `database.db` file and a `/sparse` subdir containing extrinsic/intrinsic information about the cameras, bins, etc.

## 3. Run Gaussian Splatting with XR-GS Modifications

```
bash scripts/run_gs_xrgs_trainer.sh SCENE_NAME RUN_NAME
```
E.g.
```
bash scripts/run_gs_xrgs_trainer.sh flower_xrgs NewDensifyAndPrune_v1
```

- This will create a `results_NewDensifyAndPrune_v1` in the data directory, where the checkpoints, rendered images, stats, and rendered videos will be saved
- Note: This script is currently specific to the environment we ran on (Ubuntu AWS Instance) and you may need to change the data_dir prefix in the script for it to work for you
- Alternatively, you can run `run_gs_default_trainer.sh` if you want to run the default Gaussian Splatting implementation for comparison