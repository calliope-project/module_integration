# combine demands
rule combine_demands:
    message: "Combine electricity, heat and transport demand timeseries."
    input:
        demand_electricity="results/prepare/{resolution}/demand_electricity_MW.parquet",
        demand_heat="data/module_demand_heat/{resolution}/demand_heat_profiles_MW.parquet",
        demand_transport="data/module_demand_transport/{resolution}/demand_profiles_total_MW.parquet",
    output:
        "results/prepare/{resolution}/combined_demands/demand_combined_sum_base.parquet",
        "results/prepare/{resolution}/combined_demands/demand_combined_sum_res_50.parquet",
        "results/prepare/{resolution}/combined_demands/demand_combined_sum_res_75.parquet",
        "results/prepare/{resolution}/combined_demands/demand_combined_sum_res_90.parquet",
        scenarios=directory("results/prepare/{resolution}/combined_demands/"),
        plot="results/prepare/{resolution}/combined_demands/demand_assumptions.png",
    script: "../scripts/combine_demands.py"

# prepare techs definition
rule prepare_techs:
    input:
        nodes="results/prepare/{resolution}/nodes.parquet",
        shapes="results/prepare/{resolution}/shapes.parquet",
        map_shapes_to_nodes="results/module_electricity_grid/{resolution}/results/map_shapes_to_nodes.parquet",
    output:
        techs="results/prepare/{resolution}/techs.parquet",
    script: "../scripts/prepare_techs.py"
