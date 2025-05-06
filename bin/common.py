from pathlib import Path

required_files = [
    channel_mapping_filename := "channel_name_mapping.csv",
    known_channels_filename := "ribca_known_channels.txt",
    cell_type_mapping_filename := "cell_type_mapping.csv",
]

data_dir_possibilities = [
    Path("/opt"),
    Path(__file__).parent / "data",
]


def find_data_dir() -> Path:
    for path in data_dir_possibilities:
        if all((path / filename).is_file() for filename in required_files):
            return path
    message_pieces = [f"Couldn't find data directory; tried:"]
    message_pieces.extend([f"\t{path}" for path in data_dir_possibilities])
    raise FileNotFoundError("\n".join(message_pieces))
