#!/usr/bin/env python3
"""Download selected product types for one OPUS observation."""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
import zipfile
from pathlib import Path

import requests


METADATA_FILES = {"data.csv", "manifest.csv", "urls.txt"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download and extract products for one exact OPUS ID."
    )
    parser.add_argument("opus_id", help="Exact OPUS ID returned by an OPUS search")
    parser.add_argument("--types", help="Comma-separated OPUS product types")
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--keep-zip", action="store_true")
    return parser.parse_args()


def safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    """Extract a ZIP while rejecting members that escape the destination."""
    destination_resolved = destination.resolve()
    for member in archive.infolist():
        target = (destination / member.filename).resolve()
        if destination_resolved not in target.parents and target != destination_resolved:
            raise RuntimeError(f"Unsafe ZIP member path: {member.filename}")
    archive.extractall(destination)


def read_manifest_rows(extract_dir: Path) -> list[dict[str, str]]:
    manifest_path = extract_dir / "manifest.csv"
    if not manifest_path.exists():
        raise RuntimeError("OPUS archive did not contain manifest.csv")

    with manifest_path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    url = f"https://opus.pds-rings.seti.org/opus/api/download/{args.opus_id}.zip"
    params = {"types": args.types} if args.types else None

    zip_path = args.output_dir / f"{args.opus_id}.zip"
    part_path = zip_path.with_suffix(".zip.part")
    extract_dir = args.output_dir / args.opus_id
    temp_extract_dir = args.output_dir / f".{args.opus_id}.extracting"

    part_path.unlink(missing_ok=True)
    if temp_extract_dir.exists():
        shutil.rmtree(temp_extract_dir)

    try:
        with requests.get(url, params=params, stream=True, timeout=(15, 180)) as response:
            response.raise_for_status()
            with part_path.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)

        part_path.replace(zip_path)

        temp_extract_dir.mkdir(parents=True)
        with zipfile.ZipFile(zip_path) as archive:
            safe_extract(archive, temp_extract_dir)

        manifest_rows = read_manifest_rows(temp_extract_dir)
        if not manifest_rows:
            requested = args.types or "all available types"
            raise RuntimeError(
                "OPUS returned no matching product files for "
                f"{args.opus_id} using {requested}."
            )

        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        temp_extract_dir.replace(extract_dir)

        print(f"Extracted {len(manifest_rows)} OPUS product file(s) to {extract_dir}")
        for row in manifest_rows:
            path = row.get("File Path", "").strip()
            product_type = row.get("Product Type Abbrev", "").strip()
            if path and Path(path).name not in METADATA_FILES:
                label = f" [{product_type}]" if product_type else ""
                print(f"  - {path}{label}")

        if not args.keep_zip:
            zip_path.unlink(missing_ok=True)
        return 0

    except requests.RequestException as exc:
        print(f"Download failed: {exc}", file=sys.stderr)
    except zipfile.BadZipFile as exc:
        print(f"Downloaded file was not a valid ZIP archive: {exc}", file=sys.stderr)
    except (OSError, RuntimeError) as exc:
        print(f"Could not complete OPUS download: {exc}", file=sys.stderr)
    finally:
        part_path.unlink(missing_ok=True)
        if temp_extract_dir.exists():
            shutil.rmtree(temp_extract_dir, ignore_errors=True)

    zip_path.unlink(missing_ok=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
