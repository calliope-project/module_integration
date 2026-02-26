configfile: "config/modules/module_powerplants.yaml"

module module_powerplants:
    snakefile:
        github(
            "calliope-project/module_powerplants",
            path="workflow/Snakefile",
            tag="3384f3557dcd3db7a7e355b1840114ad0d4ad047",
        )
    config: config["module_powerplants"]
    prefix: "results/module_powerplants"

use rule * from module_powerplants as module_powerplants_*


rule input_shapes_powerplants:
    message: "Input shapes for the powerplants module."
    input:
        "results/prepare/{resolution}/shapes.parquet",
    output:
        "results/module_powerplants/resources/user/{resolution}/shapes.parquet",
    log:
        "results/module_powerplants/logs/input_shapes_{resolution}.log",
    conda:
        "../envs/shell.yaml"
    shell:
        """
        cp "{input}" "{output}" 2> "{log}"
        """

rule input_twp:
    message: "Input TWP for the powerplants module."
    input:
        "data/module_powerplants/the_wind_power/Windfarms_World_20230530.xls",
    output:
        "results/module_powerplants/resources/user/WEMI.xls",
    log:
        "results/module_powerplants/logs/input_twp.log",
    conda:
        "../envs/shell.yaml"
    shell:
        """
        cp "{input}" "{output}" 2> "{log}"
        """

rule input_potentials_pv_rooftop:
    message: "Input potentials for rooftop PV."
    input:
        potential="results/module_area_potentials/results/NUTS0/area_potential_pv_rooftop.tif",
        countries="results/module_electricity_grid/NUTS0/results/shapes_clean.parquet",
    output:
        potential="results/module_powerplants/resources/user/proxies/rooftop_pv/{resolution}.tif",
        countries="results/module_powerplants/resources/user/borders/{resolution}.parquet",
    log:
        "results/module_powerplants/logs/input_potentials_pv_rooftop_{resolution}.log",
    conda:
        "../envs/shell.yaml"
    shell:
        """
        cp "{input.potential}" "{output.potential}" 2> "{log}"
        cp "{input.countries}" "{output.countries}" 2> "{log}"
        """

rule prepare_flow_cap_min:
    input:
        categories=expand(
            "results/module_powerplants/results/{{resolution}}/aggregated/adjusted/{category}.parquet",
            category=["bioenergy", "fossil", "geothermal", "hydropower", "nuclear", "wind"]
        ),
        map_shapes_to_nodes="results/module_electricity_grid/{resolution}/results/map_shapes_to_nodes.parquet",
        shapes="results/prepare/{resolution}/shapes.parquet",
    output:
        "results/prepare/{resolution}/flow_cap_min.parquet"
    script: "../scripts/prepare_flow_cap_min.py"

rule all_powerplants:
    message: "Prepare all powerplants data."
    default_target: True
    input:
        expand(
            "results/module_powerplants/results/{shapes}/aggregated/{adjustment}/{category}.parquet", 
            shapes=["NUTS0", "NUTS2", "NUTS3"],
            adjustment=["adjusted", "unadjusted"],
            category=["bioenergy", "fossil", "geothermal", "hydropower", "nuclear", "wind", "solar"]  # "large_solar"
        )
