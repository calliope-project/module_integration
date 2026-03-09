configfile: "config/modules/module_demand_electricity.yaml"

module module_demand_electricity:
    snakefile:
        github(
            "calliope-project/module_demand_electricity",
            path="workflow/Snakefile",
            tag="56afb6b"
        )
    config: config["module_demand_electricity"]
    prefix: "results/module_demand_electricity"

use rule * from module_demand_electricity as module_demand_electricity_*

rule copy_shapes:
    message:
        "Copy shapes."
    input:
        "results/prepare/{resolution}/shapes.parquet",
    output:
        "results/module_demand_electricity/resources/user/shapes_{resolution}.parquet",
    run:
        import geopandas as gpd
        gdf = gpd.read_parquet(input[0])
        gdf = gdf.loc[gdf["shape_class"] == "land"]  # select only shapes of shape_type=="land"
        gdf = gdf.set_index("shape_id")  # set index, which will be the columns of the resulting data
        gdf.to_parquet(output[0])

rule copy_countries:
    message: "Copy countries."
    input:"results/prepare/NUTS0/shapes.parquet",
    output: "results/module_demand_electricity/resources/user/countries.parquet"
    conda: "../envs/shell.yaml"
    shell: "cp {input} {output}"

rule copy_token_entsoe:
    input:
        ".secrets/entsoe.txt"
    output:
        "results/module_demand_electricity/resources/user/token_entsoe.txt"
    conda: "../envs/shell.yaml"
    shell:
        "cp {input} {output}"

rule prepare_demand_electricity:
    input:
        data="results/module_demand_electricity/results/demand_electricity_{resolution}_MW.parquet",
        map_shapes_to_nodes="results/module_electricity_grid/{resolution}/results/map_shapes_to_nodes.parquet",
    output:
        "results/prepare/{resolution}/demand_electricity_MW.parquet"
    run:
        import pandas as pd
        from lib.data_processing import map_index
        data = pd.read_parquet(input.data)
        map_shapes_to_nodes = pd.read_parquet(input.map_shapes_to_nodes)
        map_shapes_to_nodes = dict(map_shapes_to_nodes.set_index("shape_id")["nodes"])
        data = map_index(data, map_shapes_to_nodes, axis=1)
        data = data.rename(columns={"shape_id": "nodes"})
        data.to_parquet(output[0])

rule all_demand_electricity:
    input:
        expand(
            "results/module_demand_electricity/results/demand_electricity_{nuts_level}_MW.parquet",
            nuts_level=["NUTS0", "NUTS2", "NUTS3"],
        )
