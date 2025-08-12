configfile: "config/default.yaml"

PATH_PREPARE = Path("results/prepare/{resolution}")
PATH_MODELS = "results/models/{resolution}/{template}/{scenario}/"

wildcard_constraints:
    scenario = "|".join(config["demand_scenario"]),
    resolution="NUTS0|NUTS2|NUTS3|NUTS3_PRT",

# module rules
include: "./rules/0_module_area_potentials.smk"
include: "./rules/0_module_demand_electricity.smk"
include: "./rules/0_module_pv_wind.smk"
include: "./rules/0_module_geo_boundaries.smk"
include: "./rules/0_module_electricity_grid.smk"
include: "./rules/0_module_demand_heat.smk"
include: "./rules/0_module_demand_transport.smk"
include: "./rules/0_module_powerplants.smk"

# rules
include: "./rules/2_prepare.smk"
include: "./rules/3_construct.smk"
include: "./rules/4_run.smk"
include: "./rules/5_postprocess.smk"

rule dag:
    message: "Plot dependency graph of the workflow."
    conda: "envs/dag.yaml"
    shell:
        """
        mkdir -p build
        snakemake --rulegraph > build/dag.dot
        dot -Tpdf -o build/dag.pdf build/dag.dot
        """

rule clean: # removes all generated results
    message: "Remove all build results but keep downloaded data."
    run:
        import shutil
        shutil.rmtree("results")
        print("Data downloaded to data/ has not been cleaned.")

rule construct_all_eu:
    input:
        expand(
            "results/models/{resolution}/{method}/{scenario}/construct",
            resolution=["NUTS0", "NUTS2"],
            scenario=["base", "res_50", "res_75", "res_90"],
            method=["min_cost", "max_techs"]
        )

rule run_min_cost_eu:
    input:
        expand(
            "results/models/{resolution}/min_cost/{scenario}/run/{scenario}/model.nc",
            resolution=["NUTS0", "NUTS2"],
            scenario=["base", "res_50", "res_75", "res_90"]
        ),

rule run_max_techs_eu:
    input:
        expand(
            "results/models/{resolution}/max_techs/{scenario}/run/{scenario}_{slack}/model.nc",
            resolution=["NUTS0", "NUTS2"],
            scenario=["base", "res_50", "res_75", "res_90"],
            slack=["slack_01", "slack_05", "slack_10"],
        )
