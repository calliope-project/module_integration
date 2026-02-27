import pandas as pd
import geopandas as gpd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ShapeTechMatcher:
    def __init__(self, shapes: gpd.GeoDataFrame, techs_land: list[str], techs_maritime: list[str]):
        self.shapes = shapes
        self.techs = dict(
            land=techs_land,
            maritime=techs_maritime,
        )

    def shape_matches_tech(self, shape_id, tech):
        shape_class = self.shapes.loc[self.shapes["shape_id"] == shape_id, "shape_class"]
        assert len(shape_class) == 1
        shape_class = shape_class.iloc[0]
        matches = tech in self.techs[shape_class]
        return matches


def shapes_to_nodes(df, mapping):
    df.loc[:, ["shape_id"]] = df.loc[:, ["shape_id"]].replace(mapping)
    df = df.rename(columns={"shape_id": "nodes"})
    return df


def prepare_powerplants(df, techs_land, techs_maritime, map_shapes_to_nodes, rename_columns, destination):
    # rename variables
    df = df.rename(columns=rename_columns)
    
    # select shape_class that matches for tech
    matcher = ShapeTechMatcher(shapes, techs_land, techs_maritime)
    condition = df.apply(lambda row: matcher.shape_matches_tech(row["shape_id"], row["techs"]), axis=1)
    df = df.loc[condition]

    # map shapes to nodes
    mapping = dict(map_shapes_to_nodes.set_index("shape_id")["nodes"])
    df = shapes_to_nodes(df, mapping)

    df = df.loc[:, ["nodes"] + list(rename_columns.values())]
    df = df.reset_index(drop=True)

    df.to_parquet(destination, index=False)


if __name__ == "__main__":
    dfs = []
    for path in snakemake.input.categories:
        logger.info(f"Processing file: {path}")
        df = pd.read_parquet(path)
        dfs.append(df)

    dfs = pd.concat(dfs, ignore_index=True)
    
    techs_land = snakemake.config["techs_onshore"]
    techs_maritime = snakemake.config["techs_offshore"]
    shapes = gpd.read_parquet(snakemake.input.shapes)
    map_shapes_to_nodes = pd.read_parquet(snakemake.input.map_shapes_to_nodes)
    rename_columns = snakemake.config["powerplants"]["rename_columns"]

    prepare_powerplants(
        dfs,
        techs_land=techs_land,
        techs_maritime=techs_maritime,
        map_shapes_to_nodes=map_shapes_to_nodes,
        rename_columns=rename_columns,
        destination=snakemake.output[0],
    )
