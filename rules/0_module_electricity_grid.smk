configfile: "config/modules/module_electricity_grid.yaml"

NUTS_LEVELS = ["NUTS0", "NUTS2", "NUTS3"]

module module_electricity_grid:
    snakefile:
        # "../../module_electricity_grid/workflow/Snakefile"
        github(
            "calliope-project/module_electricity_grid",
            path="workflow/Snakefile",
            tag="9260841"
        )
    config: config["module_electricity_grid"]
    prefix: "results/module_electricity_grid/{nuts_level}"

use rule * from module_electricity_grid as module_electricity_grid_*


rule input_network:
    message: "Copy the pypsa network 'module_electricity_grid'."
    input: "data/module_electricity_grid/pypsa_eur_resources/base_s_adm_{nuts_level}.nc"
    output: "results/module_electricity_grid/{nuts_level}/resources/user/network.nc"
    conda: "../envs/shell.yaml"
    shell: "cp {input} {output}"

rule input_shapes_to_module_electricity_grid:
    message: "Copy the shapes to 'module_electricity_grid'."
    input: 
        onshore="data/module_electricity_grid/pypsa_eur_resources/regions_onshore_base_s_adm_{nuts_level}.geojson",
        offshore="data/module_electricity_grid/pypsa_eur_resources/regions_offshore_base_s_adm_{nuts_level}.geojson",
    output: 
        onshore="results/module_electricity_grid/{nuts_level}/resources/user/shapes_onshore.geojson",
        offshore="results/module_electricity_grid/{nuts_level}/resources/user/shapes_offshore.geojson",
    conda: "../envs/shell.yaml"
    shell:
        """
        cp {input.onshore} {output.onshore};
        cp {input.offshore} {output.offshore};
        """

rule copy_outputs:
    message: "Copy module's outputs to results/prepare."
    input:
        "results/module_electricity_grid/{nuts_level}/results/shapes_clean.parquet",
    output:
        "results/prepare/{nuts_level}/shapes.parquet",
    shell:
        """
        cp {input[0]} {output[0]};
        """

rule prepare_calliope_links_nodes:
    message: "Prepare calliope links and nodes."
    input:
        lines="results/module_electricity_grid/{nuts_level}/results/lines_clean.parquet",
        links="results/module_electricity_grid/{nuts_level}/results/links_clean.parquet",
        buses="results/module_electricity_grid/{nuts_level}/results/nodes_clean.parquet",
    output:
        calliope_nodes="results/prepare/{nuts_level}/nodes.parquet",
        calliope_links="results/prepare/{nuts_level}/links.parquet",
        calliope_links_geo="results/prepare/{nuts_level}/links_geometries.parquet",
    params:
        limit_scope=False
    script:
        "../scripts/prepare_calliope_links_nodes.py"

rule all_electricity_grid:
    input:
        expand(
            "results/module_electricity_grid/{nuts_level}/results/shapes_clean.parquet",
            nuts_level=NUTS_LEVELS
        )
