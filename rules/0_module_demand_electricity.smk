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
        gdf = gdf.set_index("bus")
        gdf = gdf.loc[gdf["shape_class"] == "land"]
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

rule demand_electricity_output:
    message: "Move into place the electricity demand timeseries."
    input: "results/module_demand_electricity/results/demand_electricity_{resolution}_MW.parquet"
    output: "results/prepare/{resolution}/demand_electricity.parquet"
    run:
        import pandas as pd
        df = pd.read_parquet(input[0])
        df.index.name = None
        df.columns = pd.MultiIndex.from_product([["demand_electricity"], df.columns], names=['techs', 'nodes'])
        df.to_parquet(output[0])

rule all_demand_electricity:
    input:
        expand(
            "results/module_demand_electricity/results/demand_electricity_{nuts_level}_MW.parquet",
            nuts_level=["NUTS0", "NUTS2", "NUTS3"],
        )
