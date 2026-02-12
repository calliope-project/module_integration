configfile: "config/modules/module_electricity_grid.yaml"

NUTS_LEVELS = ["NUTS0", "NUTS2", "NUTS3"]

module module_electricity_grid:
    snakefile:
        github(
            "calliope-project/module_electricity_grid",
            path="workflow/Snakefile",
            tag="43f9d54"
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

rule all_electricity_grid:
    input:
        expand(
            "results/module_electricity_grid/{nuts_level}/results/shapes_clean.parquet",
            nuts_level=NUTS_LEVELS
        )
