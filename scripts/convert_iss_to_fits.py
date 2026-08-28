#!/usr/bin/env python3
"""Convert a calibrated Cassini ISS VICAR/PDS3 image into FITS."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
from astropy.io import fits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a calibrated Cassini ISS IMG/LBL product to FITS."
    )
    parser.add_argument("label", type=Path, help="Detached PDS3 .LBL file")
    parser.add_argument("output", type=Path, help="Output FITS file")
    parser.add_argument("--opus-id", help="Optional OPUS observation ID")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def extract_label_value(text: str, key: str) -> str | None:
    pattern = rf"(?m)^\s*{re.escape(key)}\s*=\s*(.+?)\s*$"
    match = re.search(pattern, text)
    if not match:
        return None
    return match.group(1).strip()


def clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().strip('"').strip("'")


def extract_vicar_value(text: str, key: str) -> str:
    pattern = rf"\b{re.escape(key)}\s*=\s*('[^']*'|\"[^\"]*\"|[^\s]+)"
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"Missing VICAR field: {key}")
    return clean_value(match.group(1)) or ""


def find_image_path(label_path: Path, label_text: str) -> Path:
    match = re.search(
        r'\^IMAGE\s*=\s*\(\s*"([^"]+)"',
        label_text,
        flags=re.IGNORECASE,
    )
    if not match:
        raise ValueError("Could not find the ^IMAGE filename in the PDS label")

    image_path = label_path.parent / match.group(1)
    if not image_path.exists():
        raise FileNotFoundError(f"Referenced IMG file not found: {image_path}")

    return image_path


def read_vicar_header(image_path: Path) -> tuple[str, int]:
    with image_path.open("rb") as handle:
        initial = handle.read(4096)

    initial_text = initial.decode("ascii", errors="replace")
    label_size = int(extract_vicar_value(initial_text, "LBLSIZE"))

    with image_path.open("rb") as handle:
        full_header = handle.read(label_size)

    return full_header.decode("ascii", errors="replace"), label_size


def read_iss_image(image_path: Path) -> tuple[np.ndarray, dict[str, object]]:
    vicar_text, label_size = read_vicar_header(image_path)

    image_format = extract_vicar_value(vicar_text, "FORMAT").upper()
    organization = extract_vicar_value(vicar_text, "ORG").upper()
    real_format = extract_vicar_value(vicar_text, "REALFMT").upper()

    record_size = int(extract_vicar_value(vicar_text, "RECSIZE"))
    lines = int(extract_vicar_value(vicar_text, "NL"))
    samples = int(extract_vicar_value(vicar_text, "NS"))
    bands = int(extract_vicar_value(vicar_text, "NB"))
    prefix_bytes = int(extract_vicar_value(vicar_text, "NBB"))
    binary_header_records = int(extract_vicar_value(vicar_text, "NLB"))

    if image_format != "REAL":
        raise ValueError(f"Unsupported VICAR FORMAT: {image_format}")

    if organization != "BSQ":
        raise ValueError(f"Unsupported VICAR organization: {organization}")

    if bands != 1:
        raise ValueError(f"Expected one ISS band, found {bands}")

    dtype_map = {
        "RIEEE": np.dtype("<f4"),
        "IEEE": np.dtype(">f4"),
    }

    try:
        source_dtype = dtype_map[real_format]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported VICAR REALFMT: {real_format}"
        ) from exc

    bytes_per_row = samples * source_dtype.itemsize

    if record_size < prefix_bytes + bytes_per_row:
        raise ValueError(
            "VICAR record is too small for the declared image row: "
            f"RECSIZE={record_size}, NBB={prefix_bytes}, "
            f"pixel bytes={bytes_per_row}"
        )

    image_offset = label_size + binary_header_records * record_size
    array = np.empty((lines, samples), dtype=np.float32)

    with image_path.open("rb") as handle:
        for row_index in range(lines):
            row_offset = (
                image_offset
                + row_index * record_size
                + prefix_bytes
            )
            handle.seek(row_offset)

            raw = handle.read(bytes_per_row)
            if len(raw) != bytes_per_row:
                raise EOFError(
                    f"Incomplete image row {row_index}: "
                    f"expected {bytes_per_row} bytes, received {len(raw)}"
                )

            array[row_index] = np.frombuffer(
                raw,
                dtype=source_dtype,
                count=samples,
            )

    metadata: dict[str, object] = {
        "LBLSIZE": label_size,
        "RECSIZE": record_size,
        "NLB": binary_header_records,
        "NBB": prefix_bytes,
        "NL": lines,
        "NS": samples,
        "NB": bands,
        "REALFMT": real_format,
        "OFFSET": image_offset,
    }

    return array, metadata


def add_header_value(
    header: fits.Header,
    key: str,
    value: str | None,
    comment: str,
) -> None:
    cleaned = clean_value(value)
    if cleaned is not None:
        header[key] = (cleaned[:68], comment)


def main() -> int:
    args = parse_args()

    if not args.label.exists():
        print(f"Label does not exist: {args.label}", file=sys.stderr)
        return 2

    try:
        label_text = args.label.read_text(
            encoding="ascii",
            errors="replace",
        )
        image_path = find_image_path(args.label, label_text)
        image, vicar = read_iss_image(image_path)

        header = fits.Header()
        header["ORIGIN"] = "Saturn Hexagon pipeline"
        header["SRCFILE"] = (image_path.name, "Original Cassini ISS IMG")
        header["PDSLABEL"] = (args.label.name, "Original detached PDS label")
        header["BUNIT"] = ("I/F", "Calibrated radiance factor")
        header["CALSTAT"] = ("CISSCAL", "Source product already calibrated")
        header["MAPPROJ"] = (False, "No map projection applied")

        if args.opus_id:
            header["OPUSID"] = (args.opus_id, "PDS OPUS observation ID")

        add_header_value(
            header,
            "PRODUCT",
            extract_label_value(label_text, "PRODUCT_ID"),
            "PDS product ID",
        )
        add_header_value(
            header,
            "TARGET",
            extract_label_value(label_text, "TARGET_NAME"),
            "Observation target",
        )
        add_header_value(
            header,
            "INSTRUME",
            extract_label_value(label_text, "INSTRUMENT_ID"),
            "Cassini ISS instrument ID",
        )
        add_header_value(
            header,
            "FILTERS",
            extract_label_value(label_text, "FILTER_NAME"),
            "ISS filter combination",
        )
        add_header_value(
            header,
            "PDSSTART",
            extract_label_value(label_text, "START_TIME"),
            "Original PDS start time",
        )
        add_header_value(
            header,
            "PDSSTOP",
            extract_label_value(label_text, "STOP_TIME"),
            "Original PDS stop time",
        )
        add_header_value(
            header,
            "EXPOSURE",
            extract_label_value(label_text, "EXPOSURE_DURATION"),
            "Original PDS exposure value",
        )

        header["VICLBL"] = (vicar["LBLSIZE"], "VICAR label bytes")
        header["VICREC"] = (vicar["RECSIZE"], "VICAR record bytes")
        header["VICNLB"] = (vicar["NLB"], "VICAR binary header records")
        header["VICNBB"] = (vicar["NBB"], "VICAR row prefix bytes")
        header["SRCOFF"] = (vicar["OFFSET"], "Image byte offset in IMG")

        header.add_history(
            "Converted from calibrated Cassini ISS VICAR/PDS3 product."
        )
        header.add_history(
            "No additional radiometric calibration or map projection applied."
        )

        primary = fits.PrimaryHDU(data=image, header=header)

        args.output.parent.mkdir(parents=True, exist_ok=True)
        primary.writeto(
            args.output,
            overwrite=args.overwrite,
            checksum=True,
        )

        print(f"Wrote: {args.output}")
        print(f"Source: {image_path}")
        print(f"Shape: {image.shape}")
        print(f"Dtype: {image.dtype}")
        print(f"Minimum: {np.min(image):.9g}")
        print(f"Maximum: {np.max(image):.9g}")
        print(f"Mean: {np.mean(image, dtype=np.float64):.9g}")
        print(f"Image offset: {vicar['OFFSET']} bytes")
        return 0

    except Exception as exc:
        print(f"ISS conversion failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())