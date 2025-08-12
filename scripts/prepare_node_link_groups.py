import geopandas as gpd
import pandas as pd
import yaml


def create_node_groups(df_fine, df_coarse, on="country_id"):
    """
    Creates a mapping from fine to coarse, based on the column `on`.
    """
    not_in_coarse = df_fine[~df_fine[on].isin(df_coarse[on])][on].to_list()
    not_in_fine = df_coarse[~df_coarse[on].isin(df_fine[on])][on].to_list()
    print("Not in coarse: ", not_in_coarse)
    print("Not in fine: ", not_in_fine)

    node_groups = pd.merge(df_fine[[on, "nodes"]], df_coarse[[on, "nodes"]], on=on, how="inner")
    node_groups = node_groups.rename(columns={"nodes_x": "nodes", "nodes_y": "node_groups"})

    node_groups = node_groups.set_index("nodes")
    node_groups["lookup_node_group"] = True

    node_groups = node_groups[["node_groups", "lookup_node_group"]]

    return node_groups


def create_link_groups(links_fine, node_groups):
    link_groups = links_fine.copy()[["techs", "from", "to"]]
    link_groups = link_groups.set_index("techs")

    # map from, to of links_fine from fine to coarse according to node_groups
    link_groups["from_coarse"] = link_groups["from"].map(node_groups["node_groups"])
    link_groups["to_coarse"] = link_groups["to"].map(node_groups["node_groups"])
    link_groups["techs_coarse"] = link_groups[["from_coarse", "to_coarse"]].apply(
        lambda x: f"{x.iloc[0]}_to_{x.iloc[1]}", axis=1
    )

    # if from, to are the same in coarse, drop the link (copperplate assumption)
    link_groups = link_groups[link_groups["from_coarse"] != link_groups["to_coarse"]]

    link_groups = link_groups.drop(columns=["from", "to", "from_coarse", "to_coarse"])

    link_groups.index.name = "techs"
    link_groups.columns = ["link_groups"]

    link_groups["lookup_link_group"] = True

    return link_groups


if __name__ == "__main__":
    links_fine = pd.read_csv(snakemake.input.links_fine)
    links_coarse = pd.read_csv(snakemake.input.links_coarse)
    nodes_fine = pd.read_csv(snakemake.input.nodes_fine)
    nodes_coarse = pd.read_csv(snakemake.input.nodes_coarse)

    node_groups = create_node_groups(nodes_fine, nodes_coarse)

    link_groups = create_link_groups(links_fine, node_groups)

    # compare with links_coarse
    not_in_coarse = sorted(
        list(set(link_groups["link_groups"]).difference(set(links_coarse["techs"])))
    )
    not_in_fine = sorted(
        list(set(links_coarse["techs"]).difference(set(link_groups["link_groups"])))
    )
    logger.info("Not in coarse: ", not_in_coarse)
    logger.info("Not in fine: ", not_in_fine)

    # save as csv
    node_groups.to_csv(snakemake.output.node_groups)
    link_groups.to_csv(snakemake.output.link_groups)
