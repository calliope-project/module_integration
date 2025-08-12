import pandas as pd
import geopandas as gpd
import pycountry
from lib.data_processing import filter_df

COLS_LINES = [
    "Line",
    "bus0",
    "bus1",
    "s_nom",
    "capital_cost",
    "build_year",
    "lifetime",
    "length",
    "carrier",
    "terrain_factor",
    "geometry",
]

COLS_LINKS = [
    "Link",
    "bus0",
    "bus1",
    "efficiency",
    "build_year",
    "lifetime",
    "p_nom",
    "p_set",
    "p_min_pu",
    "capital_cost",
    "marginal_cost",
    "marginal_cost_quadratic",
    "stand_by_cost",
    "length",
    "geometry",
]


def order_buses(row: pd.Series) -> pd.Series:
    """Order buses so that bus0 is alphabetically first."""
    if row["bus0"] > row["bus1"]:
        row["bus0"], row["bus1"] = row["bus1"], row["bus0"]
    return row


def prepare_lines_links(lines: pd.DataFrame, links: pd.DataFrame) -> pd.DataFrame:
    lines = lines.loc[:, COLS_LINES]
    links = links.loc[:, COLS_LINKS]

    lines.loc[:, "component"] = "Line"
    links.loc[:, "component"] = "Link"

    combined_df = pd.concat([lines, links], ignore_index=True)
    assert lines.crs == links.crs
    combined_df = gpd.GeoDataFrame(
        combined_df,
        geometry="geometry",
        crs=lines.crs,
    )

    combined_df = combined_df.apply(order_buses, axis=1)

    combined_df["bus0_to_bus1"] = combined_df.apply(lambda x: f"{x['bus0']}_to_{x['bus1']}", axis=1)

    return combined_df


def prepare_calliope_links(lines_links):
    calliope_links = lines_links[["bus0_to_bus1", "bus0", "bus1", "geometry"]].rename(
        columns={"bus0_to_bus1": "techs", "bus0": "from", "bus1": "to"}
    )
    calliope_links["distance"] = lines_links["length"]
    calliope_links.loc[lines_links["component"] == "Line", "flow_cap_min"] = lines_links.loc[
        lines_links["component"] == "Line", "s_nom"
    ]
    calliope_links.loc[lines_links["component"] == "Link", "flow_cap_min"] = lines_links.loc[
        lines_links["component"] == "Link", "p_nom"
    ]
    calliope_links = calliope_links[["techs", "from", "to", "distance", "flow_cap_min", "geometry"]]

    calliope_links = calliope_links.groupby("techs").agg(
        {
            "from": lambda x: x.iloc[0],
            "to": lambda x: x.iloc[0],
            "distance": lambda x: x.mean(),
            "flow_cap_min": lambda x: x.sum(),
            "geometry": lambda x: x.iloc[0],
        }
    )
    calliope_links = gpd.GeoDataFrame(calliope_links, geometry="geometry", crs=lines_links.crs)

    calliope_links = calliope_links.reset_index()

    return calliope_links


def prepare_calliope_nodes(buses: pd.DataFrame) -> pd.DataFrame:
    assert buses.crs == "EPSG:4326"
    nodes = buses[["Bus", "y", "x", "country"]].rename(
        columns={"Bus": "nodes", "y": "lat", "x": "lon", "country": "country_id"}
    )

    return nodes


if __name__ == "__main__":
    lines = gpd.read_parquet(snakemake.input.lines).reset_index()
    links = gpd.read_parquet(snakemake.input.links).reset_index()
    nodes = gpd.read_parquet(snakemake.input.buses).reset_index()

    combined_df = prepare_lines_links(lines, links)
    combined_df = combined_df.loc[combined_df["build_year"] <= 2050]

    calliope_links = prepare_calliope_links(combined_df)
    calliope_nodes = prepare_calliope_nodes(nodes)

    if snakemake.params.limit_scope:
        config = snakemake.config
        nodes_selected = config["spatial_scope"][snakemake.wildcards.spatial_scope]
        calliope_nodes = filter_df(calliope_nodes, {"nodes": nodes_selected})
        calliope_links = filter_df(calliope_links, {"from": nodes_selected, "to": nodes_selected})

    calliope_links.to_parquet(snakemake.output.calliope_links_geo)
    calliope_links.drop(columns="geometry").to_csv(snakemake.output.calliope_links, index=False)
    calliope_nodes.to_csv(snakemake.output.calliope_nodes, index=False)
