#!/usr/bin/env python3
import csv
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint

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


class ChannelMapper:
    mapping: dict[str, str]

    def __init__(self):
        self.mapping = {}
        with open(find_channel_name_mapping(), newline="") as f:
            r = csv.reader(f)
            for row in r:
                self.mapping[row[0]] = row[1]

    def map_channel_name(self, name: str) -> str:
        c = self.mapping.get(name, name)
        if c.lower().startswith("dapi"):
            c = c.split("-")[0]
        return c

    def map_channel_names(self, names: list[str]) -> list[str]:
        return [self.map_channel_name(name) for name in names]


def get_channel_names(image: tifffile.TiffFile) -> list[str]:
    tree = lxml.etree.fromstring(image.ome_metadata.encode("utf-8"))
    namespaces = tree.nsmap.copy()
    namespaces["OME"] = namespaces[None]
    del namespaces[None]
    channels = tree.xpath("//OME:Pixels/OME:Channel/@Name", namespaces=namespaces)
    return channels


def convert_expr_image(expr_image: Path):
    print("Reading", expr_image)
    e = tifffile.TiffFile(expr_image)
    mapper = ChannelMapper()
    orig_channels = get_channel_names(e)
    print("Original channel names:")
    pprint(orig_channels)
    channels = mapper.map_channel_names(orig_channels)
    print("Adjusted channel names:")
    pprint(channels)

    # TODO: track this more directly
    differences = []
    for orig_ch, new_ch in zip(orig_channels, channels):
        if orig_ch != new_ch:
            differences.append((orig_ch, new_ch))
    if differences:
        print("Differences (old → new):")
        for orig_ch, new_ch in differences:
            print(orig_ch, "→", new_ch)

    with open("markers.txt", "w") as f:
        for c in channels:
            print(c, file=f)
    image_data = e.asarray()
    print("Original expression shape:", image_data.shape)
    squeezed = image_data.squeeze()
    print("New expression shape:", squeezed.shape)
    assert len(squeezed.shape) == 3, "Need only CYX dimensions"
    tifffile.imwrite("expr.tiff", squeezed)


def convert_mask_image(mask_image: Path):
    print("Reading", mask_image)
    m = tifffile.TiffFile(mask_image)
    channels = get_channel_names(m)
    for i, name in enumerate(channels):
        if name in {"cell", "cells"}:
            break
    else:
        raise ValueError("No cell channel found in mask")
    mask_data = m.asarray()
    print("Mask shape:", mask_data.shape)
    squeezed = mask_data.squeeze()
    cell_mask = squeezed[i]
    tifffile.imwrite("mask.tiff", cell_mask)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("expr_image", type=Path)
    p.add_argument("mask_image", type=Path)
    args = p.parse_args()

    convert_expr_image(args.expr_image)
    convert_mask_image(args.mask_image)
