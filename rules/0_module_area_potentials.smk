configfile: "config/modules/module_area_potentials.yaml"

module module_area_potentials:
    snakefile:
        github(
            "calliope-project/module_area_potentials",
            path="workflow/Snakefile",
            tag="36b6091",
        )
    config: config["module_area_potentials"]
    prefix: "results/module_area_potentials"

use rule * from module_area_potentials as module_area_potentials_*

rule input_shapes:
    message:
        "Move shapes to resources/user."
    input:
        "results/module_electricity_grid/{shape}/results/shapes_clean.parquet",
    output:
        "results/module_area_potentials/resources/user/shapes/{shape}.parquet",
    log:
        "results/module_area_potentials/logs/input_shapes_{shape}.log",
    shell:
        """
        cp "{input}" "{output}" 2> "{log}"
        """

rule input_protected_areas:
    message:
        "Move protected areas to resources/user."
    input:
        # Needs to be downloaded from https://www.protectedplanet.net/en/thematic-areas/wdpa?tab=WDPA
        # then unzipped and renamed to wdpa.gdb
        "data/module_area_potentials/WDPA/wdpa.gdb",
    output:
        directory("results/module_area_potentials/resources/user/wdpa.gdb"),
    log:
        "results/module_area_potentials/logs/input_protected_areas.log",
    conda:
        "../envs/shell.yaml"
    shell:
        """
        cp -r "{input[0]}" {output[0]} 2> "{log}"
        """

rule area_potentials_all:
    message:
        "Run the module."
    default_target: True
    input:
        "results/module_area_potentials/results/NUTS0/area_potential_report.html",

rule aggregate_raster_to_poly:
    input:
        raster="results/module_area_potentials/results/{shape}/area_potential_{tech}.tif",
        polygons="results/prepare/{shape}/shapes.parquet",
    output: "results/prepare/{shape}/area_potentials/area_potential_{tech}.parquet"
    shell: "python scripts/aggregate_raster_to_poly.py {input.raster} {input.polygons} {output[0]}"

rule prepare_power_potential:
    input:
        area_potential="results/prepare/{shape}/area_potentials/area_potential_{tech}.parquet",
        power_densities="data/prepare/power_densities/power_densities.csv",
        shapes="results/prepare/{shape}/shapes.parquet",
        map_shapes_to_nodes="results/module_electricity_grid/{shape}/results/map_shapes_to_nodes.parquet",
    output:
       "results/prepare/{shape}/power_potentials/power_potential_{tech}.parquet",
    script: "../scripts/prepare_power_potential.py"

rule combine_power_potentials:
    input:
        expand(
            "results/prepare/{{shape}}/power_potentials/power_potential_{tech}.parquet",
            tech=["pv_rooftop", "pv_open_field", "wind_onshore", "wind_offshore"]
        )
    output:
        "results/prepare/{shape}/power_potentials_combined.parquet",
    script: "../scripts/combine_power_potentials.py"

rule all_area_potentials:
    message: "Prepare all area potentials data."
    input:
        expand(
            "results/module_area_potentials/results/NUTS0/area_potential_{tech}.tif",
            tech=["wind_onshore", "wind_offshore", "pv_open_field", "pv_rooftop"]
        )
