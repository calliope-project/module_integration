rule run_model:
    input:
        PATH_MODELS + "construct/model.yaml",
    output:
        PATH_MODELS + "run/{run_scenario}/model.nc"
    log: PATH_MODELS + "run/{run_scenario}/model_.log"
    benchmark: PATH_MODELS + "run/{run_scenario}/model.benchmark.tsv"
    shell: "python scripts/run_model.py {input} {wildcards.run_scenario} {log} {output}"
