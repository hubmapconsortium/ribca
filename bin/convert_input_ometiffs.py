#!/usr/bin/env python3
import csv
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint
from typing import NamedTuple

import lxml.etree
import tifffile

MATCHED_COLOR = "\033[01;32m"
UNMATCHED_COLOR = "\033[01;31m"
NO_COLOR = "\033[00m"

channel_mapping_filename = "channel_name_mapping.csv"
known_channels_filename = "ribca_known_channels.txt"
data_dir_possibilities = [
    Path("/opt"),
    Path(__file__).parent / "data",
]


def find_data_dir() -> Path:
    for path in data_dir_possibilities:
        if (path / channel_mapping_filename).is_file() and (
            path / known_channels_filename
        ).is_file():
            return path
    message_pieces = [f"Couldn't find data directory; tried:"]
    message_pieces.extend([f"\t{path}" for path in data_dir_possibilities])
    raise FileNotFoundError("\n".join(message_pieces))


class MappedChannelData(NamedTuple):
    new_channels: list[str]
    channel_differences: set[tuple[str, str]]
    matched_channels: set[str]
    unmatched_channels: set[str]


class ChannelMapper:
    mapping: dict[str, str]
    known_channels: set[str]

    def __init__(self):
        data_dir = find_data_dir()

        self.mapping = {}
        with open(data_dir / channel_mapping_filename, newline="") as f:
            r = csv.reader(f)
            for row in r:
                self.mapping[row[0]] = row[1]

        self.known_channels = set()
        with open(data_dir / known_channels_filename) as f:
            for line in f:
                self.known_channels.add(line.strip())

    def map_channel_name(self, name: str) -> str:
        c = self.mapping.get(name, name)
        if c.lower().startswith("dapi"):
            c = c.split("-")[0]
        return c

    def map_channel_names(self, names: list[str]) -> MappedChannelData:
        new_channels = []
        differences = set()
        for name in names:
            new_name = self.map_channel_name(name)
            new_channels.append(new_name)
            if name != new_name:
                differences.add((name, new_name))
        new_channel_set = set(new_channels)
        matched_channels = new_channel_set & self.known_channels
        unmatched_channels = new_channel_set - self.known_channels
        return MappedChannelData(
            new_channels=new_channels,
            channel_differences=differences,
            matched_channels=matched_channels,
            unmatched_channels=unmatched_channels,
        )


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
    mapping_data = mapper.map_channel_names(orig_channels)
    print("Adjusted channel names:")
    pprint(mapping_data.new_channels)

    if mapping_data.channel_differences:
        print("Differences (old → new):")
        for orig_ch, new_ch in mapping_data.channel_differences:
            print(f"\t{orig_ch} → {new_ch}")

    print(MATCHED_COLOR + "Matched channels:" + NO_COLOR)
    for c in sorted(mapping_data.matched_channels):
        print(MATCHED_COLOR + f"\t{c}" + NO_COLOR)
    print(UNMATCHED_COLOR + "Unmatched channels:" + NO_COLOR)
    for c in sorted(mapping_data.unmatched_channels):
        print(UNMATCHED_COLOR + "\t{c}" + NO_COLOR)

    with open("markers.txt", "w") as f:
        for c in mapping_data.new_channels:
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
    print("Original mask shape:", mask_data.shape)
    squeezed = mask_data.squeeze()
    cell_mask = squeezed[i]
    print("New cell mask shape:", cell_mask.shape)
    tifffile.imwrite("mask.tiff", cell_mask)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("expr_image", type=Path)
    p.add_argument("mask_image", type=Path)
    args = p.parse_args()

    convert_expr_image(args.expr_image)
    convert_mask_image(args.mask_image)
