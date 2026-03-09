rule postprocess_model:
    input: PATH_MODELS + "run/{scenario}/model.nc"
    output: directory(PATH_MODELS + "postprocess/{scenario}")
    log: PATH_MODELS + "postprocess/{scenario}.log"
    shell: "python scripts/postprocess.py {input} -d {output}"

rule postprocess_models:
    input:
        expand(
            PATH_MODELS + "run/{scenario}/model.nc",
            resolution=["NUTS0"],
            template=["min_cost"],
            scenario=["base", "res_50", "res_75", "res_90"],
        ),
        expand(
            PATH_MODELS + "run/{scenario}_{slack}/model.nc",
            resolution=["NUTS0"],
            template=["min_area_use"],
            scenario=["base", "res_50", "res_75", "res_90"],
            slack=["slack_01", "slack_05", "slack_10"],
        )
    output:
        directory("results/models/postprocess_combined"),
    log: "results/models/postprocess_combined.log"
    shell: "python scripts/postprocess.py {input} -d {output}"
