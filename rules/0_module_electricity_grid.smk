configfile: "config/modules/module_electricity_grid.yaml"

SHAPES = ["NUTS0", "NUTS2", "NUTS3"]

module module_electricity_grid:
    snakefile:
        # "../../module_electricity_grid/workflow/Snakefile"
        github(
            "calliope-project/module_electricity_grid",
            path="workflow/Snakefile",
            tag="9260841"
        )
    config: config["module_electricity_grid"]
    prefix: "results/module_electricity_grid/{shape}"

use rule * from module_electricity_grid as module_electricity_grid_*


rule input_network:
    message: "Copy the pypsa network 'module_electricity_grid'."
    input: "data/module_electricity_grid/pypsa_eur_resources/base_s_adm_{shape}.nc"
    output: "results/module_electricity_grid/{shape}/resources/user/network.nc"
    conda: "../envs/shell.yaml"
    shell: "cp {input} {output}"

rule input_shapes_to_module_electricity_grid:
    message: "Copy the shapes to 'module_electricity_grid'."
    input: 
        onshore="data/module_electricity_grid/pypsa_eur_resources/regions_onshore_base_s_adm_{shape}.geojson",
        offshore="data/module_electricity_grid/pypsa_eur_resources/regions_offshore_base_s_adm_{shape}.geojson",
    output: 
        onshore="results/module_electricity_grid/{shape}/resources/user/shapes_onshore.geojson",
        offshore="results/module_electricity_grid/{shape}/resources/user/shapes_offshore.geojson",
    conda: "../envs/shell.yaml"
    shell:
        """
        cp {input.onshore} {output.onshore};
        cp {input.offshore} {output.offshore};
        """

rule copy_outputs:
    message: "Copy module's outputs to results/prepare."
    input:
        "results/module_electricity_grid/{shape}/results/shapes_clean.parquet",
    output:
        "results/prepare/{shape}/shapes.parquet",
    shell:
        """
        cp {input[0]} {output[0]};
        """

rule prepare_calliope_links_nodes:
    message: "Prepare calliope links and nodes."
    input:
        lines="results/module_electricity_grid/{shape}/results/lines_clean.parquet",
        links="results/module_electricity_grid/{shape}/results/links_clean.parquet",
        buses="results/module_electricity_grid/{shape}/results/nodes_clean.parquet",
    output:
        calliope_nodes="results/prepare/{shape}/nodes.parquet",
        calliope_links="results/prepare/{shape}/links.parquet",
        calliope_links_geo="results/prepare/{shape}/links_geometries.parquet",
    params:
        limit_scope=False
    script:
        "../scripts/prepare_calliope_links_nodes.py"

rule all_electricity_grid:
    input:
        expand(
            "results/module_electricity_grid/{shape}/results/shapes_clean.parquet",
            shape=SHAPES
        )
