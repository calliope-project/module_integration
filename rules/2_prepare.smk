# combine demands
rule combine_demands:
    message: "Combine electricity, heat and transport demand timeseries."
    input:
        demand_electricity="results/prepare/{resolution}/demand_electricity.parquet",
        demand_heat="results/prepare/{resolution}/demand_heat.parquet",
        demand_transport="results/prepare/{resolution}/demand_transport.parquet",
    output:
        "results/prepare/{resolution}/combined_demands/demand_combined_sum_base.parquet",
        "results/prepare/{resolution}/combined_demands/demand_combined_sum_res_50.parquet",
        "results/prepare/{resolution}/combined_demands/demand_combined_sum_res_75.parquet",
        "results/prepare/{resolution}/combined_demands/demand_combined_sum_res_90.parquet",
        scenarios=directory("results/prepare/{resolution}/combined_demands/"),
        plot="results/prepare/{resolution}/combined_demands/demand_assumptions.png",
    script: "../scripts/combine_demands.py"

# combine nodes, area and techs
rule prepare_nodes_area_techs:
    input:
        nodes="results/prepare/{resolution}/nodes.parquet",
        area_onshore="results/prepare/{resolution}/area_potential_wind_onshore.parquet",
        area_offshore="results/prepare/{resolution}/area_potential_wind_offshore.parquet",
    output:
        nodes_area="results/prepare/{resolution}/nodes_area.parquet",
        techs="results/prepare/{resolution}/techs.parquet",
    script: "../scripts/prepare_nodes_area_techs.py"
