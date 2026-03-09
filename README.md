# Module Integration Workflow

This workflow integrates several data modules to generate a set of Calliope models, run them, and
post-process the results.

## Getting started

First, create a new conda environment with the required dependencies:

```bash
conda env create -f environment.yaml
conda activate module_integration
```

There are several target rules that you can run to create results. `construct_all_eu` will construct all
available Europe-level models at resolution NUTS0 and NUTS2. `run_min_cost_eu` runs all the cost-minimising
models, while `run_max_techs_eu` runs the models that maximise the deployment of a given technology.

Before constructing models, you can also run the target rule for a specific module. Each rule `rules/0_module_*.smk`
contains a target rule that triggers the output of the module.

Rules in `rules/2_prepare.smk` further process the data to meet the data model of the Calliope models. Intermediate
results are stored in `results/prepare/`.

Based on the data in `results/prepare/`, the rules in `rules/3_construct.smk` construct the Calliope models. Different models
can be constructed based on specific templates, defined in `template_components`.

After running the models, the results can be post-processed one-by-one or for several models at once, using
the `Postprocessor` and `Processor` classes, together with extendable routines that process `calliope.Model` results and
return a `pandas.DataFrame`.
