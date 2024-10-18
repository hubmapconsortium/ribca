#!/usr/bin/env python3
import csv
from argparse import ArgumentParser
from pathlib import Path

import lxml.etree
import tifffile

channel_mapping_filename = "channel_name_mapping.csv"
channel_mapping_file_possibilities = [
    Path("/opt") / channel_mapping_filename,
    Path(__file__).parent / "data" / channel_mapping_filename,
]


def find_channel_name_mapping() -> Path:
    for path in channel_mapping_file_possibilities:
        if path.is_file():
            return path
    message_pieces = [f"Couldn't find {channel_mapping_filename} in any of:"]
    message_pieces.extend([f"\t{path}" for path in channel_mapping_file_possibilities])
    raise FileNotFoundError("\n".join(message_pieces))


def read_channel_name_mapping() -> dict[str, str]:
    mapping = {}
    with open(find_channel_name_mapping(), newline="") as f:
        r = csv.reader(f)
        for row in r:
            mapping[row[0]] = row[1]
    return mapping


def get_channel_names(image: tifffile.TiffFile) -> list[str]:
    tree = lxml.etree.fromstring(image.ome_metadata.encode("utf-8"))
    namespaces = tree.nsmap.copy()
    namespaces["OME"] = namespaces[None]
    del namespaces[None]
    channels = tree.xpath("//OME:Pixels/OME:Channel/@Name", namespaces=namespaces)
    return channels


def convert_expr_image(expr_image: Path):
    e = tifffile.TiffFile(expr_image)
    orig_channels = get_channel_names(e)
    channel_mapping = read_channel_name_mapping()
    channels = [channel_mapping.get(c, c) for c in orig_channels]
    with open("marker_list.txt", "w") as f:
        for c in channels:
            print(c, file=f)
    image_data = e.asarray()
    squeezed = image_data.squeeze()
    assert len(squeezed.shape) == 3, "Need only CYX dimensions"
    tifffile.imwrite("expr.tiff", squeezed)


def convert_mask_image(mask_image: Path):
    m = tifffile.TiffFile(mask_image)
    channels = get_channel_names(m)
    for i, name in enumerate(channels):
        if name in {"cell", "cells"}:
            break
    else:
        raise ValueError("No cell channel found in mask")
    mask_data = m.asarray()
    squeezed = mask_data.squeeze()
    cell_mask = squeezed[i]
    tifffile.imwrite("cell_mask.tiff", cell_mask)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("expr_image", type=Path)
    p.add_argument("mask_image", type=Path)
    args = p.parse_args()

    convert_expr_image(args.expr_image)
    convert_mask_image(args.mask_image)
