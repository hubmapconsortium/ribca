#!/usr/bin/env python3
from argparse import ArgumentParser
from ast import literal_eval
from pathlib import Path

import pandas as pd


def convert_ribca_output(results_dir: Path):
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

    with pd.HDFStore("results.hdf5") as store:
        store["annotations"] = df
        store["votes"] = votes_df


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("results_dir", type=Path)
    args = p.parse_args()

    convert_ribca_output(args.results_dir)
