import os
import shutil
import json
import random
from pathlib import Path
from PIL import Image
from typing import Dict, List
import argparse


def generate_mixed_resolution_dataset(
    input_dir: str,
    output_dir: str,
    base_factor: int = 5,
    extra_factor: int = 2,
    high_res_pct: float = 0.3,
    seed: int = 42,
) -> Dict:
    """
    Creates mixed-resolution images.
    - All images are downsampled by `base_factor`
    - A subset (1 - high_res_pct) is downsampled further (total = base_factor * extra_factor)
    - Keeps track of which are HR/LR.

    Returns:
        metadata dict with lists of HR and LR image names.
    """
    random.seed(seed)
    input_dir = Path(input_dir)
    out_img_dir = Path(output_dir) / "images"
    out_img_dir.mkdir(parents=True, exist_ok=True)

    image_files = sorted([f for f in input_dir.iterdir() if f.suffix.lower() in [".jpg", ".png"]])

    num_images = len(image_files)
    num_hr = int(num_images * high_res_pct)

    hr_images = set(random.sample(image_files, num_hr))
    lr_images = set(image_files) - hr_images

    metadata = {"high_res": [], "low_res": []}

    print(f"Found {num_images} images.")
    print(f"High-res: {len(hr_images)} | Low-res: {len(lr_images)}")

    for img_path in image_files:
        img = Image.open(img_path)
        w, h = img.size

        # base downsample
        w1, h1 = w // base_factor, h // base_factor
        img_down = img.resize((w1, h1), Image.LANCZOS)

        # extra downsample for LR set
        if img_path in lr_images:
            w2, h2 = w1 // extra_factor, h1 // extra_factor
            img_down = img_down.resize((w2, h2), Image.LANCZOS)
            metadata["low_res"].append(img_path.name)
        else:
            metadata["high_res"].append(img_path.name)

        img_down.save(out_img_dir / img_path.name)

    return metadata


def copy_colmap_data(original_dataset: str, output_dir: str):
    """
    Copies COLMAP outputs:
    - sparse/ folder
    - database.db
    - poses_bounds.npy (if present)
    """
    orig = Path(original_dataset)
    out = Path(output_dir)

    # sparse/
    sparse_src = orig / "sparse"
    sparse_dst = out / "sparse"
    if sparse_src.exists():
        print("Copying sparse/ ...")
        if sparse_dst.exists():
            shutil.rmtree(sparse_dst)
        shutil.copytree(sparse_src, sparse_dst)
    else:
        print("WARNING: sparse/ not found in source dataset.")

    # database.db
    if (orig / "database.db").exists():
        print("Copying database.db ...")
        shutil.copy2(orig / "database.db", out / "database.db")
    else:
        print("WARNING: database.db not found.")

    # poses_bounds.npy (LLFF-specific)
    if (orig / "poses_bounds.npy").exists():
        print("Copying poses_bounds.npy ...")
        shutil.copy2(orig / "poses_bounds.npy", out / "poses_bounds.npy")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_dir", required=True,
                        help="Path to the original LLFF images folder (e.g. LLFF/images)")
    parser.add_argument("--orig_dataset_root", required=True,
                        help="Path to the original LLFF dataset root (contains sparse, db, etc.)")
    parser.add_argument("--output_dir", required=True,
                        help="Where to save the XR-GS dataset folder")
    parser.add_argument("--base_factor", type=int, default=5)
    parser.add_argument("--extra_factor", type=int, default=2)
    parser.add_argument("--high_res_pct", type=float, default=0.3)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    print("=== Generating XR-GS Mixed Resolution Dataset ===")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate mixed-resolution images
    metadata = generate_mixed_resolution_dataset(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        base_factor=args.base_factor,
        extra_factor=args.extra_factor,
        high_res_pct=args.high_res_pct,
        seed=args.seed,
    )

    # 2. Copy COLMAP data
    copy_colmap_data(args.orig_dataset_root, args.output_dir)

    # 3. Save metadata JSON
    with open(Path(args.output_dir) / "mixed_res_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    print("=== XR-GS dataset created successfully ===")
    print(f"Saved to: {args.output_dir}")
    print(f"High-res count: {len(metadata['high_res'])}")
    print(f"Low-res count: {len(metadata['low_res'])}")


if __name__ == "__main__":
    main()
