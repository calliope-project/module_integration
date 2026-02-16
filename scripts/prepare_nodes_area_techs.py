import pandas as pd
import geopandas as gpd


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
        [nodes["nodes"].unique(), techs],
        names=["nodes", "techs"],
    ).to_frame(index=False)
    return techs_df


def main(path_nodes, path_area_onshore, path_area_offshore, path_nodes_area, path_techs):
    nodes = pd.read_parquet(path_nodes)
    area_onshore = gpd.read_parquet(path_area_onshore).reset_index()
    area_offshore = gpd.read_parquet(path_area_offshore).reset_index()

    # Prepare the DataFrame for nodes_area_techs
    nodes.loc[:, "available_area"] = area_onshore["sum"]

    nodes_with_offshore = area_offshore.loc[area_offshore["sum"] > 0]
    nodes_with_offshore = nodes_with_offshore["shape_id"].str.replace("_maritime", "")

    techs_df_onshore = create_techs_df(
        nodes.loc[~nodes["nodes"].isin(nodes_with_offshore)], TECHS_ONSHORE
    )
    techs_df_offshore = create_techs_df(
        nodes.loc[nodes["nodes"].isin(nodes_with_offshore)], [*TECHS_ONSHORE, *TECHS_OFFSHORE]
    )
    techs_df = pd.concat([techs_df_onshore, techs_df_offshore], ignore_index=True)
    techs_df = techs_df.sort_values(by=["nodes", "techs"]).reset_index(drop=True)
    techs_df["exists"] = True

    # Save results
    techs_df.to_parquet(path_techs, index=False)
    nodes.to_parquet(path_nodes_area, index=False)


if __name__ == "__main__":
    main(
        path_nodes=snakemake.input.nodes,
        path_area_onshore=snakemake.input.area_onshore,
        path_area_offshore=snakemake.input.area_offshore,
        path_nodes_area=snakemake.output.nodes_area,
        path_techs=snakemake.output.techs,
    )
