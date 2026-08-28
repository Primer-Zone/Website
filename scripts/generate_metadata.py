#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate standardized metadata for an image product."
    )

    parser.add_argument("--opus-id", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--data-csv", type=Path, required=True)
    parser.add_argument("--label", type=Path, required=True)
    parser.add_argument("--inspection-log", type=Path, required=True)
    parser.add_argument("--scientific-file", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--screenshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--region",
        default="North Polar Region",
    )

    return parser.parse_args()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    with path.open(
        newline="",
        encoding="utf-8-sig",
    ) as handle:
        return list(csv.DictReader(handle))


def read_first_csv_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)

    if not rows:
        raise ValueError(f"CSV contains no data rows: {path}")

    return rows[0]


def clean(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()

    if not value:
        return None

    return value.strip('"').strip("'")


def extract_label_value(
    text: str,
    key: str,
) -> str | None:
    pattern = rf"(?m)^\s*{re.escape(key)}\s*=\s*(.+?)\s*$"
    match = re.search(pattern, text)

    if not match:
        return None

    return clean(match.group(1))


def parse_filters(value: str | None) -> list[str]:
    if not value:
        return []

    value = value.strip()

    if value.startswith("(") and value.endswith(")"):
        value = value[1:-1]

    return [
        item.strip().strip('"').strip("'")
        for item in value.split(",")
        if item.strip()
    ]


def find_source_product(manifest_path: Path) -> str:
    rows = read_csv_rows(manifest_path)

    for row in rows:
        if row.get("Product Type Abbrev", "").strip() == "coiss_calib":
            file_path = row.get("File Path", "").strip()

            if file_path:
                filename = Path(file_path).name

                if filename.lower().endswith(".img"):
                    filename = filename[:-4]

                return filename

    raise ValueError(
        "Could not find a coiss_calib product in manifest.csv."
    )


def find_inspection_row(
    inspection_log_path: Path,
    opus_id: str,
) -> dict[str, str]:
    rows = read_csv_rows(inspection_log_path)

    for row in rows:
        if row.get("opus_id", "").strip() == opus_id:
            return row

    raise ValueError(
        f"No inspection record found for OPUS ID: {opus_id}"
    )


def build_metadata(
    args: argparse.Namespace,
) -> dict[str, Any]:
    data_row = read_first_csv_row(args.data_csv)

    inspection = find_inspection_row(
        args.inspection_log,
        args.opus_id,
    )

    if not args.label.exists():
        raise FileNotFoundError(
            f"PDS label not found: {args.label}"
        )

    label_text = args.label.read_text(
        encoding="ascii",
        errors="replace",
    )

    target = (
        clean(
            extract_label_value(
                label_text,
                "TARGET_NAME",
            )
        )
        or clean(
            data_row.get(
                "Intended Target Name(s)"
            )
        )
        or "Unknown"
    )

    instrument_id = clean(
        extract_label_value(
            label_text,
            "INSTRUMENT_ID",
        )
    )

    instrument_name = clean(
        data_row.get("Instrument Name")
    )

    filters = parse_filters(
        extract_label_value(
            label_text,
            "FILTER_NAME",
        )
    )

    source_product = find_source_product(
        args.manifest
    )

    screenshot_exists = args.screenshot.exists()

    north_pole_visible = (
        inspection.get(
            "north_pole_visible",
            "",
        ).strip().lower()
        == "yes"
    )

    hexagon_visible = (
        inspection.get(
            "hexagon_visible",
            "",
        ).strip().lower()
        == "yes"
    )

    ds9_verified = (
        screenshot_exists
        and north_pole_visible
        and hexagon_visible
    )

    calibration = inspection.get(
        "calibration_status",
        "",
    ).strip()

    if not calibration:
        calibration = "Not specified"

    return {
        "id": (
            f"saturn_hexagon_iss_"
            f"{args.opus_id.removeprefix('co-iss-')}"
        ),
        "target": target.title(),
        "region": args.region,
        "instrument": (
            "Cassini ISS Wide Angle Camera"
            if instrument_id == "ISSWA"
            else instrument_name or "Cassini ISS"
        ),
        "observation_id": args.opus_id,
        "filters": filters,
        "source": "NASA PDS OPUS",
        "source_product": source_product,
        "image": args.image,
        "scientific_file": args.scientific_file.as_posix(),
        "processing": "PDS3 → FITS",
        "calibration": calibration,
        "validation": {
            "dimensions": inspection.get(
                "array_shape",
                "",
            ),
            "ds9_verified": ds9_verified,
        },
        "publication_ready": ds9_verified,
        "website_ready": ds9_verified,
    }


def main() -> int:
    args = parse_args()

    try:
        metadata = build_metadata(args)

        args.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        args.output.write_text(
            json.dumps(
                metadata,
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        print(f"Wrote metadata: {args.output}")
        print(
            json.dumps(
                metadata,
                indent=2,
                ensure_ascii=False,
            )
        )

        return 0

    except (OSError, ValueError) as exc:
        print(
            f"Metadata generation failed: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
