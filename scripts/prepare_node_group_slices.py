import pandas as pd
from pathlib import Path


def prepare_node_group_slices(source, destination):
    df = pd.read_csv(source)
    df = df.rename(columns={"nodes": "nodes_in_node_group"})
    df = df[["node_groups", "nodes_in_node_group"]]

    if not Path(destination).exists():
        df.to_csv(destination, index=False)
        print(f"Node group slicing data prepared and saved to {destination}.")
    else:
        raise ValueError(
            f"Destination file {destination} already exists. Please remove it before running this script."
        )


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent
    source_path = base_path / "results" / "prepare" / "NUTS2" / "node_groups_NUTS2_to_NUTS0.csv"
    destination_path = (
        base_path / "results" / "prepare" / "NUTS2" / "node_groups_NUTS2_to_NUTS0_slices.csv"
    )

    prepare_node_group_slices(source_path, destination_path)
