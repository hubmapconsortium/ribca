#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path

import lxml.etree
import tifffile


def get_channel_names(image: tifffile.TiffFile) -> list[str]:
    tree = lxml.etree.fromstring(image.ome_metadata.encode("utf-8"))
    namespaces = tree.nsmap.copy()
    namespaces["OME"] = namespaces[None]
    del namespaces[None]
    channels = tree.xpath("//OME:Pixels/OME:Channel/@Name", namespaces=namespaces)
    return channels


def convert_expr_image(expr_image: Path):
    e = tifffile.TiffFile(expr_image)
    channels = get_channel_names(e)
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
