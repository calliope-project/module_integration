configfile: "config/modules/module_pv_wind.yaml"

module module_pv_wind:
    snakefile:
        github(
            "calliope-project/module_pv_wind",
            path="workflow/Snakefile",
            tag="f16dfe3",
        )
    config: config["module_pv_wind"]
    prefix: "results/module_pv_wind"

use rule * from module_pv_wind as module_pv_wind_*

wildcard_constraints:
    on_or_offshore = "onshore|offshore",
    tech = "wind_offshore|wind_onshore|pv_rooftop|pv_open_field"

rule input_cutout:
    message: "Copy the cutout 'modules_pv_wind'."
    input: "data/module_pv_wind/cutout/era5.nc"
    output: "results/module_pv_wind/resources/user/cutout_era5.nc"
    conda: "../envs/shell.yaml"
    shell: "cp {input} {output}"

rule input_layout:
    message: "Copy the layout to 'modules_pv_wind'."
    input: "results/prepare/raster/area_potential_{name_layout}.tif"
    output: "results/module_pv_wind/resources/user/layout/{name_layout}.tif"
    conda: "../envs/shell.yaml"
    shell: "cp {input} {output}"

rule input_shapes_to_module_pv_wind:
    message: "Copy the shapes at desired resolution to 'modules_pv_wind'."
    input: "results/prepare/{resolution}/shapes.parquet"
    output:
        onshore="results/module_pv_wind/resources/user/spatial_units/{resolution}_onshore.parquet",
        offshore="results/module_pv_wind/resources/user/spatial_units/{resolution}_offshore.parquet"
    run:
        import geopandas as gpd
        gdf = gpd.read_parquet(input[0])
        gdf.loc[gdf["shape_class"] == "land"].set_index("bus").to_parquet(output.onshore)
        gdf.loc[gdf["shape_class"] == "maritime"].set_index("bus").to_parquet(output.offshore)

rule input_tech_specs:
    message: "Copy the tech_specs to 'modules_pv_wind'."
    input: "data/module_pv_wind/tech_specs/{tech}.yaml"
    output: "results/module_pv_wind/resources/user/tech_specs/{tech}.yaml"
    conda: "../envs/shell.yaml"
    wildcard_constraints:
        tech = "wind_offshore_3.6MW|wind_onshore_3MW|pv_rooftop_CSi_S|pv_rooftop_CSi_W|pv_open_field_CSi_S",
    shell: "cp {input} {output}"

rule prepare_capacity_factors:
    message: "Convert the capacity factors to model format."
    input: "results/module_pv_wind/results/era5/{resolution}_{on_or_offshore}/{name_layout}/capacityfactors_{tech}.nc"  # {resolution}/{config['scope']['temporal']['year']}/
    output: "results/prepare/{resolution}/{on_or_offshore}/{name_layout}/capacityfactors_{tech}.parquet"
    params:
        zero_tol = config["capacity_factors"]["zero_tol"]
    wildcard_constraints:
        on_or_offshore = "onshore|offshore",
        tech = "wind_offshore_3.6MW|wind_onshore_3MW|pv_rooftop_CSi_S|pv_rooftop_CSi_W|pv_open_field_CSi_S",
    shell: "python scripts/prepare_capacity_factors.py {input} {wildcards.name_layout} {params.zero_tol} {output}"

rule all_capacity_factors:
    input:
        expand(
            [
                "results/prepare/{resolution}/offshore/wind_offshore/capacityfactors_wind_offshore_3.6MW.parquet",
                "results/prepare/{resolution}/onshore/pv_open_field/capacityfactors_pv_open_field_CSi_S.parquet",
                "results/prepare/{resolution}/onshore/pv_rooftop/capacityfactors_pv_rooftop_CSi_S.parquet",
                "results/prepare/{resolution}/onshore/wind_onshore/capacityfactors_wind_onshore_3MW.parquet",
            ],
            resolution=["NUTS0", "NUTS2", "NUTS3"],
        )
