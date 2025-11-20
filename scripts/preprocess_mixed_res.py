import os
import json
import argparse
import random
from PIL import Image

def downsample(img: Image.Image, factor: float) -> Image.Image:
    """Downsample an image by a given factor."""
    w, h = img.size
    new_w, new_h = int(w / factor), int(h / factor)
    return img.resize((new_w, new_h), Image.LANCZOS)

def make_mixed_resolution_images(
    img_dir: str,
    base_factor: float,
    highres_pct: float,
    extra_factor: float,
    seed: int,
):
    """
    Produces mixed-resolution images.

    Steps:
    (1) All images are downsampled by `base_factor` (e.g. 5x)
    (2) A fraction `highres_pct` stays at this resolution
    (3) Remaining images are further downsampled by `extra_factor` (E.g. 2x for a total of 10x)

    Returns:
        mixed_images: list of (filename, PIL.Image)
        metadata: dict with {"high_res": [...], "low_res": [...]}
    """

    random.seed(seed)

    files = sorted([
        f for f in os.listdir(img_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])

    if len(files) == 0:
        raise ValueError(f"No image files found in directory: {img_dir}")

    num_images = len(files)
    num_highres = int(num_images * highres_pct)


    highres_indices = set(random.sample(range(num_images), num_highres))

    mixed_images = []
    high_res_files = []
    low_res_files = []

    for idx, fname in enumerate(files):
        path = os.path.join(img_dir, fname)
        img = Image.open(path)

        # Step 1: base downsample
        img = downsample(img, base_factor)

        # Step 2: further downsample low-res subset
        if idx in highres_indices:
            high_res_files.append(fname)
        else:
            img = downsample(img, extra_factor)
            low_res_files.append(fname)

        mixed_images.append((fname, img))

    metadata = {
        "high_res": high_res_files,
        "low_res": low_res_files,
        "base_factor": base_factor,
        "extra_factor": extra_factor,
        "highres_pct": highres_pct,
        "seed": seed
    }

    return mixed_images, metadata


def main():
    parser = argparse.ArgumentParser(description="Generate mixed-resolution image dataset.")
    parser.add_argument("--in_dir", type=str, required=True,
                        help="Directory containing original images (e.g. data/llff/fern/images)")
    parser.add_argument("--out_dir", type=str, required=True,
                        help="Directory where processed images + metadata.json will be saved")
    parser.add_argument("--base_factor", type=float, default=5.0,
                        help="Base downsample factor for all images (default: 5)")
    parser.add_argument("--highres_pct", type=float, default=0.3,
                        help="Percentage of images to keep at the base resolution (default: 0.3)")
    parser.add_argument("--extra_factor", type=float, default=2.0,
                        help="Extra downsample factor for low-resolution subset (default: 2)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility (default: 42)")

    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    mixed_images, metadata = make_mixed_resolution_images(
        img_dir=args.in_dir,
        base_factor=args.base_factor,
        highres_pct=args.highres_pct,
        extra_factor=args.extra_factor,
        seed=args.seed,
    )

    # save images
    os.makedirs(os.path.join(args.out_dir, "images"), exist_ok=True)

    for fname, img in mixed_images:
        out_path = os.path.join(args.out_dir, "images/", fname)
        img.save(out_path)

    # save metadata JSON
    metadata_path = os.path.join(args.out_dir, "mixed_res_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"\n✓ Mixed-resolution dataset saved to: {args.out_dir}")
    print(f"✓ Metadata saved to: {metadata_path}")
    print(f"High-res images: {len(metadata['high_res'])}")
    print(f"Low-res images:  {len(metadata['low_res'])}")


if __name__ == "__main__":
    main()
