#!/usr/bin/env python3
from argparse import ArgumentParser
from ast import literal_eval
from pathlib import Path
from shutil import copy

import pandas as pd


def read_ribca_output(results_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    annotations = pd.read_csv(
        results_dir / "headless_annotation_0.txt",
        index_col=0,
        dtype={"RIBCA_CellType": "category"},
    )
    confidence = pd.read_csv(
        results_dir / "headless_confidence_0.txt",
        index_col=0,
    )
    thresholds = pd.read_csv(
        results_dir / "headless_confidence_thresholds_0.txt",
        index_col=0,
    )
    df = pd.concat([annotations, confidence, thresholds], axis=1).sort_index()

    vote_ids = []
    votes = []
    with open(results_dir / "headless_votes_0.txt") as f:
        for line in f:
            cell_id_str, cell_votes_str = line.strip().split(",", 1)
            cell_votes = literal_eval(cell_votes_str)
            vote_ids.append(int(cell_id_str))
            votes.append(cell_votes)
    votes_df = pd.DataFrame(votes, index=vote_ids).sort_index()

    return df, votes_df


def convert_ribca_output(results_dir: Path):
    df, votes_df = read_ribca_output(results_dir)
    with open(results_dir / "image_name.txt") as f:
        image_name = f.read().strip()
    print("Writing results in HDF5 format to", (hdf5_path := f"ribca_{image_name}.hdf5"))
    with pd.HDFStore(hdf5_path) as store:
        store.put("annotations", df, format="table")
        store.put("votes", votes_df)
    ribca_dir = Path("ribca")
    ribca_dir.mkdir(exist_ok=True, parents=True)
    print("Copying CSV annotation results to", (csv_path := ribca_dir / f"{image_name}.csv"))
    copy(results_dir / "headless_annotation_0.txt", csv_path)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("results_dir", type=Path, nargs="+")
    args = p.parse_args()

    for directory in args.results_dir:
        convert_ribca_output(directory)
