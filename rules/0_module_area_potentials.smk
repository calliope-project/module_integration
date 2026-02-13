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
        onshore="results/module_electricity_grid/{resolution}/results/shapes_clean.parquet",
    output:
        "results/module_area_potentials/resources/user/shapes/{resolution}.parquet",
    log:
        "results/module_area_potentials/logs/input_shapes_{resolution}.log",
    shell:
        """
        cp "{input.onshore}" "{output}" 2> "{log}"
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
        raster="results/module_area_potentials/results/{resolution}/area_potential_{techs}.tif",
        polygons="results/prepare/{resolution}/shapes.parquet",
    output: "results/prepare/{resolution}/area_potential_{techs}.parquet"
    shell: "python scripts/aggregate_raster_to_poly.py {input.raster} {input.polygons} {output[0]}"

rule prepare_flow_cap_max:
    input:
        area_potentials_pv_rooftop="results/prepare/{resolution}/area_potential_pv_rooftop.parquet",
        area_potentials_wind_offshore="results/prepare/{resolution}/area_potential_wind_offshore.parquet",
        power_density="data/prepare/power_densities/power_densities.csv",
    output:
        path_flow_cap_max="results/prepare/{resolution}/flow_cap_max.csv",
    script: "../scripts/prepare_flow_cap_max.py"

rule all_area_potentials:
    message: "Prepare all area potentials data."
    input:
        expand(
            "results/module_area_potentials/results/NUTS0/area_potential_{techs}.tif",
            techs=["wind_onshore", "wind_offshore", "pv_open_field", "pv_rooftop"]
        )
