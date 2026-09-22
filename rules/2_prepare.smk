# combine demands
rule combine_demands:
    message: "Combine electricity, heat and transport demand timeseries."
    input:
        demand_electricity="results/prepare/{shape}/demand_electricity_MW.parquet",
        demand_heat="data/module_demand_heat/{shape}/demand_heat_profiles_MW.parquet",
        demand_transport="data/module_demand_transport/{shape}/demand_profiles_total_MW.parquet",
    output:
        "results/prepare/{shape}/combined_demands/demand_combined_sum_base.parquet",
        "results/prepare/{shape}/combined_demands/demand_combined_sum_res_50.parquet",
        "results/prepare/{shape}/combined_demands/demand_combined_sum_res_75.parquet",
        "results/prepare/{shape}/combined_demands/demand_combined_sum_res_90.parquet",
        scenarios=directory("results/prepare/{shape}/combined_demands/"),
        plot="results/prepare/{shape}/combined_demands/demand_assumptions.png",
    script: "../scripts/combine_demands.py"

# prepare techs definition
rule prepare_techs:
    input:
        nodes="results/prepare/{shape}/nodes.parquet",
        shapes="results/prepare/{shape}/shapes.parquet",
        map_shapes_to_nodes="results/module_electricity_grid/{shape}/results/map_shapes_to_nodes.parquet",
    output:
        techs="results/prepare/{shape}/techs.parquet",
    script: "../scripts/prepare_techs.py"
