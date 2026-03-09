import pandas as pd
import geopandas as gpd

from lib.data_processing import map_values


TECHS_ONSHORE = [
    "gas_pp",
    "wind_onshore",
    "pv_open_field",
    "pv_rooftop",
    "demand_electricity",
    "battery_storage",
]
TECHS_OFFSHORE = ["wind_offshore"]


def create_techs_df(nodes, techs):
    techs_df = pd.MultiIndex.from_product(
        [nodes, techs],
        names=["nodes", "techs"],
    ).to_frame(index=False)
    return techs_df


def main(path_nodes, path_shapes, path_map_shapes_to_nodes, techs_onshore, techs_offshore, path_techs):
    nodes = pd.read_parquet(path_nodes)
    shapes = gpd.read_parquet(path_shapes)
    map_shapes_to_nodes = pd.read_parquet(path_map_shapes_to_nodes)
    map_shapes_to_nodes = map_shapes_to_nodes.set_index("shape_id")["nodes"].to_dict()

    onshore_shapes = shapes.loc[shapes["shape_class"] == "land", "shape_id"]
    offshore_shapes = shapes.loc[shapes["shape_class"] == "maritime", "shape_id"]

    nodes_with_onshore = map_values(onshore_shapes, map_shapes_to_nodes)
    nodes_with_offshore = map_values(offshore_shapes, map_shapes_to_nodes)
    
    techs_df_onshore = create_techs_df(
        nodes_with_onshore.values, techs_onshore
    )
    techs_df_offshore = create_techs_df(
        nodes_with_offshore.values, techs_offshore
    )
    techs_df = pd.concat([techs_df_onshore, techs_df_offshore], ignore_index=True)
    techs_df = techs_df.sort_values(by=["nodes", "techs"]).reset_index(drop=True)
    techs_df["exists"] = True

    # Save results
    techs_df.to_parquet(path_techs, index=False)


if __name__ == "__main__":
    main(
        path_nodes=snakemake.input.nodes,
        path_shapes=snakemake.input.shapes,
        path_map_shapes_to_nodes=snakemake.input.map_shapes_to_nodes,
        techs_onshore=snakemake.config["techs_onshore"],
        techs_offshore=snakemake.config["techs_offshore"],
        path_techs=snakemake.output.techs,
    )
