rule validate_schema:
    message: "Validate the prepared data against the defined schema."
    # could instead list all module outputs here (rules.module_area_potentials_prepare.output)
    # and define the schema in the rule that produces the file.
    input:
        files=expand(
            "results/prepare/{{resolution}}/{model_file}",
            model_file=model_files
        )
    params:
        base_path="results/prepare/{resolution}"
    log: "results/prepare/{resolution}/validate_schema.log"
    output: "results/prepare/{resolution}/validated.txt"
    script: "../scripts/validate_schema.py"


rule apply_scaling:
    message: "Apply scaling factors to the prepared data for {wildcards.model_file}."
    input: "results/prepare/{resolution}/{model_file}"
    params:
        scaling=lambda wildcards: get_param("scaling", wildcards),
        zero_tol=lambda wildcards: get_param("zero_tol", wildcards)
    output: "results/prepare/{resolution}/scaled/{model_file}"
    script: "../scripts/apply_scaling_factors.py"


def get_param(param, wildcards):
    if wildcards.model_file not in config["model_files"]:
        raise ValueError(f"Model file '{wildcards.model_file}' is not described in config.")

    return config["model_files"][wildcards.model_file].get(param, None)
