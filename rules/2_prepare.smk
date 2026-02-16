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


rule apply_scaling_factors:
    input:
        demand_combined_sum_base="results/prepare/{resolution}/combined_demands/demand_combined_sum_base.parquet",
        demand_combined_sum_res_50="results/prepare/{resolution}/combined_demands/demand_combined_sum_res_50.parquet",
        demand_combined_sum_res_75="results/prepare/{resolution}/combined_demands/demand_combined_sum_res_75.parquet",
        demand_combined_sum_res_90="results/prepare/{resolution}/combined_demands/demand_combined_sum_res_90.parquet",
        flow_cap_max="results/prepare/{resolution}/flow_cap_max.parquet",
        flow_cap_min="results/prepare/{resolution}/flow_cap_min.parquet",
        links="results/prepare/{resolution}/links.parquet",
        nodes_area="results/prepare/{resolution}/nodes_area.parquet",
    output:
        demand_combined_sum_base="results/prepare/{resolution}/scaled/combined_demands/demand_combined_sum_base.parquet",
        demand_combined_sum_res_50="results/prepare/{resolution}/scaled/combined_demands/demand_combined_sum_res_50.parquet",
        demand_combined_sum_res_75="results/prepare/{resolution}/scaled/combined_demands/demand_combined_sum_res_75.parquet",
        demand_combined_sum_res_90="results/prepare/{resolution}/scaled/combined_demands/demand_combined_sum_res_90.parquet",
        flow_cap_max="results/prepare/{resolution}/scaled/flow_cap_max.parquet",
        flow_cap_min="results/prepare/{resolution}/scaled/flow_cap_min.parquet",
        links="results/prepare/{resolution}/scaled/links.parquet",
        nodes_area="results/prepare/{resolution}/scaled/nodes_area.parquet",
    script: "../scripts/apply_scaling_factors.py"

