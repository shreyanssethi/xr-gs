import os
import json
import csv
from pathlib import Path
import argparse
import re


def extract_version(name: str):
    """
    Extracts the integer version from a folder name containing '_vX'.
    Example: 'results_NewDensify_v4' -> 4
    """
    m = re.search(r"_v(\d+)", name)
    if m:
        return int(m.group(1))
    return -1  # fallback if no version found


def load_json(path: Path):
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def collect_stats(dataset_dir: str, out_csv: str):
    dataset_dir = Path(dataset_dir)
    results_dirs = [d for d in dataset_dir.iterdir() if d.is_dir() and d.name.startswith("results")]

    rows = []

    for rdir in results_dirs:
        stats_dir = rdir / "stats"
        if not stats_dir.exists():
            print(f"No stats folder in {rdir.name}, skipping")
            continue

        # Expected files
        step7k = stats_dir / "val_step6999.json"
        step30k = stats_dir / "val_step29999.json"

        # Training summary that includes mem + ellipse_time
        train30k = stats_dir / "train_step29999_rank0.json"

        js7 = load_json(step7k)
        js30 = load_json(step30k)
        js_train = load_json(train30k)

        if js7 is None or js30 is None:
            print(f"Missing val json files in {rdir.name}, skipping")
            continue

        mem_30k = js_train.get("mem") if js_train else None
        ellipse_30k = js_train.get("ellipse_time") if js_train else None

        row = {
            "name": rdir.name,
            "version": extract_version(rdir.name),

            "psnr_7k": js7.get("psnr"),
            "ssim_7k": js7.get("ssim"),
            "lpips_7k": js7.get("lpips"),
            "numGS_7k": js7.get("num_GS"),

            "psnr_30k": js30.get("psnr"),
            "ssim_30k": js30.get("ssim"),
            "lpips_30k": js30.get("lpips"),
            "numGS_30k": js30.get("num_GS"),

            "mem_30k": mem_30k,
            "ellipse_30k": ellipse_30k,
        }

        rows.append(row)

    # Sort by version number
    rows.sort(key=lambda r: r["version"])

    # Write CSV
    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "name",
                "version",
                "psnr_7k", "ssim_7k", "lpips_7k", "numGS_7k",
                "psnr_30k", "ssim_30k", "lpips_30k", "numGS_30k",
                "mem_30k", "ellipse_30k",
            ]
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Saved CSV to {out_csv}")


def main():
    parser = argparse.ArgumentParser(description="Collect XRGS stats from results folders.")
    parser.add_argument("--dataset_dir", type=str, required=True,
                        help="Directory that contains images/ and results_* folders")
    parser.add_argument("--out_csv", type=str, required=True,
                        help="Where to save the output CSV")

    args = parser.parse_args()
    collect_stats(args.dataset_dir, args.out_csv)


if __name__ == "__main__":
    main()