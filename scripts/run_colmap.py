import os
import shutil
from pathlib import Path
import argparse


def run_colmap_reconstruction(dataset_dir: str):
    """
    Runs COLMAP on the mixed-resolution dataset:
      - feature_extractor
      - exhaustive_matcher
      - mapper

    Produces:
      dataset_dir/database.db
      dataset_dir/sparse/0/{cameras.bin, images.bin, points3D.bin}
    """

    dataset_dir = Path(dataset_dir)
    images_dir = dataset_dir / "images"
    database_path = dataset_dir / "database.db"
    sparse_dir = dataset_dir / "sparse"

    if not images_dir.exists():
        raise FileNotFoundError(f"Images directory not found: {images_dir}")

    # Remove old files if they exist
    if database_path.exists():
        print("Removing old database.db")
        database_path.unlink()

    if sparse_dir.exists():
        print("Removing old sparse folder")
        shutil.rmtree(sparse_dir)

    print("\n=== Running COLMAP: Feature Extraction ===")
    os.system(
        f"colmap feature_extractor "
        f"--database_path {database_path} "
        f"--image_path {images_dir} "
        f"--ImageReader.single_camera 0 "
        f"--SiftExtraction.max_image_size 5000 "
        f"--SiftExtraction.use_gpu 0"
    )

    print("\n=== Running COLMAP: Exhaustive Matcher ===")
    os.system(
        f"colmap exhaustive_matcher "
        f"--database_path {database_path} "
        f"--SiftMatching.use_gpu 0"
    )

    print("\n=== Running COLMAP: Mapper ===")
    sparse_dir.mkdir(parents=True, exist_ok=True)
    os.system(
        f"colmap mapper "
        f"--database_path {database_path} "
        f"--image_path {images_dir} "
        f"--output_path {sparse_dir}"
    )

    print("\n=== COLMAP Reconstruction Complete ===")


def main():
    parser = argparse.ArgumentParser(description="Run COLMAP reconstruction on a dataset.")
    parser.add_argument(
        "--dataset_dir",
        type=str,
        required=True,
        help="Path to the dataset directory containing the 'images/' folder."
    )

    args = parser.parse_args()
    run_colmap_reconstruction(args.dataset_dir)


if __name__ == "__main__":
    main()
