import pandas as pd
import geopandas as gpd
from pathlib import Path
import logging

from lib.data_processing import ShapeTechMatcher, map_values


logger = logging.getLogger(__name__)


def prepare_powerplants(df, techs_land, techs_maritime, map_shapes_to_nodes, rename_columns, destination):
    # rename variables
    df = df.rename(columns=rename_columns)
    
    # select shape_class that matches for tech
    matcher = ShapeTechMatcher(shapes, techs_land, techs_maritime)
    condition = df.apply(lambda row: matcher.shape_matches_tech(row["shape_id"], row["techs"]), axis=1)
    df = df.loc[condition]

    # map shapes to nodes
    mapping = dict(map_shapes_to_nodes.set_index("shape_id")["nodes"])
    df = map_values(df, mapping, column="shape_id")
    df = df.rename(columns={"shape_id": "nodes"})

    df = df.loc[:, ["nodes"] + list(rename_columns.values())]
    df = df.reset_index(drop=True)

    # groupby and sum total capacities
    df = df.groupby(["nodes", "techs"], as_index=False).sum()

    df.to_parquet(destination, index=False)


if __name__ == "__main__":
    df = pd.read_parquet(snakemake.input.data)
    techs_land = snakemake.config["techs_onshore"]
    techs_maritime = snakemake.config["techs_offshore"]
    shapes = gpd.read_parquet(snakemake.input.shapes)
    map_shapes_to_nodes = pd.read_parquet(snakemake.input.map_shapes_to_nodes)
    rename_columns = snakemake.config["powerplants"]["rename_columns"]

    prepare_powerplants(
        df,
        techs_land=techs_land,
        techs_maritime=techs_maritime,
        map_shapes_to_nodes=map_shapes_to_nodes,
        rename_columns=rename_columns,
        destination=snakemake.output[0],
    )
