### NUTS0
configfile: "config/modules/module_geo_boundaries_NUTS0.yaml"

module module_geo_boundaries:
    snakefile:
        github(
            "calliope-project/module_geo_boundaries",
            path="workflow/Snakefile",
            tag="main",
        )
    config:
        config["module_geo_boundaries_NUTS0"]
    prefix:
        "results/module_geo_boundaries/NUTS0"

use rule * from module_geo_boundaries as module_geo_boundaries_NUTS0_*


### NUTS2
configfile: "config/modules/module_geo_boundaries_NUTS2.yaml"

module module_geo_boundaries:
    snakefile:
        github(
            "calliope-project/module_geo_boundaries",
            path="workflow/Snakefile",
            tag="main",
        )
    config:
        config["module_geo_boundaries_NUTS2"]
    prefix:
        "results/module_geo_boundaries/NUTS2"

use rule * from module_geo_boundaries as module_geo_boundaries_NUTS2_*


### NUTS3
configfile: "config/modules/module_geo_boundaries_NUTS3.yaml"

module module_geo_boundaries:
    snakefile:
        github(
            "calliope-project/module_geo_boundaries",
            path="workflow/Snakefile",
            tag="main",
        )
    config:
        config["module_geo_boundaries_NUTS3"]
    prefix:
        "results/module_geo_boundaries/NUTS3"

use rule * from module_geo_boundaries as module_geo_boundaries_NUTS3_*


### Request all outputs
rule all_geo_boundaries:
    input:
        "results/module_geo_boundaries/NUTS0/results/shapes.parquet",
        "results/module_geo_boundaries/NUTS2/results/shapes.parquet",
        "results/module_geo_boundaries/NUTS3/results/shapes.parquet",
