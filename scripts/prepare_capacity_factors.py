from pathlib import Path
import pandas as pd
import xarray as xr
import argparse

from lib.data_processing import map_index


def main(capacityfactors, zero_tol, map_shapes_to_nodes, destination):
    capacityfactors = xr.load_dataarray(capacityfactors)
    map_shapes_to_nodes = pd.read_parquet(map_shapes_to_nodes)
    
    # prepare mapping
    map_shapes_to_nodes = dict(map_shapes_to_nodes.set_index("shape_id")["nodes"])

    # prepare capacity factors dataframe
    df = capacityfactors.to_series()
    df = df.unstack(df.index.names[1])
    df.index.name = "timesteps"

    # map shapes to nodes
    df = map_index(df, map_shapes_to_nodes, axis=1)
    df.index.name = "nodes"

    # set values smaller than zero_tol to zero
    zero_tol = float(zero_tol)
    df = df.where(df >= zero_tol, 0.0)

    df.to_parquet(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("capacityfactors")
    parser.add_argument("map_shapes_to_nodes")
    parser.add_argument("zero_tol")
    parser.add_argument("destination")
    args = parser.parse_args()

    main(**vars(args))
