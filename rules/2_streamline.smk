rule validate_schema:
    message: "Validate the prepared data against the defined schema."
    # could instead list all module outputs here (rules.module_area_potentials_prepare.output)
    # and define the schema in the rule that produces the file.
    input:
        files=expand(
            "results/prepare/{{shape}}/{model_file}",
            model_file=model_files
        )
    params:
        base_path="results/prepare/{shape}"
    log: "results/prepare/{shape}/validate_schema.log"
    output: "results/prepare/{shape}/validated.txt"
    script: "../scripts/validate_schema.py"


rule apply_scaling:
    message: "Apply scaling factors to the prepared data for {wildcards.model_file}."
    input: "results/prepare/{shape}/{model_file}"
    params:
        scaling=lambda wildcards: get_param("scaling", wildcards),
        zero_tol=lambda wildcards: get_param("zero_tol", wildcards)
    output: "results/prepare/{shape}/scaled/{model_file}"
    script: "../scripts/apply_scaling_factors.py"


def get_param(param, wildcards):
    if wildcards.model_file not in config["model_files"]:
        raise ValueError(f"Model file '{wildcards.model_file}' is not described in config.")

    return config["model_files"][wildcards.model_file].get(param, None)


# TODO: cannot have wildcards in target rule.
rule prepare_package:
    input:
        expand("results/prepare/{{shape}}/{model_file}", model_file=model_files),
        expand("results/prepare/{{shape}}/scaled/{model_file}", model_file=scaled_files),
        "results/prepare/{shape}/validated.txt"


rule zip_prepared:
    input: rules.prepare_package.input
    output: "results/prepare/{shape}.zip"
    shell:
        """
        zip -r results/prepare/{wildcards.shape}.zip {input}
        """
