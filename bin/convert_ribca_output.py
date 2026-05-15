#!/usr/bin/env python3
from argparse import ArgumentParser
from ast import literal_eval
from csv import DictReader
from pathlib import Path
from shutil import copy, copytree

import pandas as pd
import json
from common import cell_type_mapping_filename, find_data_dir


def read_clid_mapping():
    reference = pd.read_csv("/opt/ribca-crosswalk.csv", header=10)
    label_to_cl_label = dict(zip(reference['Annotation_Label'], reference['CL_Label']))
    label_to_cl_id = dict(zip(reference['Annotation_Label'], reference['CL_ID']))
    return label_to_cl_label, label_to_cl_id


def map_to_clid(annotations):
    cl_label_map, cl_id_map = read_clid_mapping()
    annotations['RIBCA_CL_Label'] = annotations['RIBCA_CellType'].map(cl_label_map)
    annotations['RIBCA_CL_ID'] = annotations['RIBCA_CellType'].map(cl_id_map)
    annotations['RIBCA_CL_ID'] = annotations['RIBCA_CL_ID'].fillna('CL:0000000')

    return annotations


def create_cell_type_manifest(df, outdir):
    cell_type_manifest_dict = {}

    for column_header in ['RIBCA_CellType', 'RIBCA_CL_ID']:
        sub_dict = {
            val: int((df[column_header] == val).sum())
            for val in df[column_header].unique()
        }
        # Remove NaN key if it exists
        sub_dict = {k: v for k, v in sub_dict.items() if not pd.isna(k)}
        cell_type_manifest_dict[column_header] = sub_dict

    with open(f'{outdir}/cell_type_manifest.json', 'w') as f:
        json.dump(cell_type_manifest_dict, f)


def write_cl_mapping(df, outdir):
    mapping = df[['RIBCA_CellType', 'RIBCA_CL_ID']].drop_duplicates(subset=['RIBCA_CellType'])
    mapping.set_index('RIBCA_CellType')
    mapping_dict = {}
    for i, j in zip(mapping['RIBCA_CellType'].to_list(), mapping['RIBCA_CL_ID'].to_list()):
        mapping_dict[i] = j
    json_path = outdir / "cl_mapping.json"
    with open(json_path, 'w') as f:
        json.dump(mapping_dict, f)


def read_ribca_output(
    results_dir: Path
) -> tuple[pd.DataFrame, pd.DataFrame]:
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

    annotations = map_to_clid(annotations)
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
    ribca_results_dir = Path("ribca_results")
    with open(results_dir / "image_name.txt") as f:
        image_name = f.read().strip()
    ribca_results_subdir = ribca_results_dir / image_name
    ribca_results_subdir.mkdir(exist_ok=True, parents=True)
    copytree(results_dir, ribca_results_subdir, dirs_exist_ok=True)

    df, votes_df = read_ribca_output(results_dir)
    create_cell_type_manifest(df, ribca_results_subdir)
    print(
        "Writing results in HDF5 format to",
        (hdf5_path := ribca_results_subdir / "ribca_results.hdf5"),
    )
    with pd.HDFStore(hdf5_path) as store:
        store.put("annotations", df, format="table")
        store.put("votes", votes_df)

    sprm_dir = Path("ribca_for_sprm")
    sprm_dir.mkdir(exist_ok=True, parents=True)
    print("Writing CSV annotation results to", (csv_path := sprm_dir / f"{image_name}.csv"))
    df["RIBCA_CL_ID"].to_csv(csv_path, index=False)
    # Write a CLID mapping json for portal
    write_cl_mapping(df, ribca_results_dir)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("results_dir", type=Path, nargs="+")
    args = p.parse_args()

    for directory in args.results_dir:
        convert_ribca_output(directory)
