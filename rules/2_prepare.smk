# prepare electricity grid


# prepare demands
rule combine_demands:
    message: "Combine electricity, heat and transport demand timeseries."
    input:
        demand_electricity="results/prepare/{resolution}/demand_electricity.csv",
        demand_heat="results/prepare/{resolution}/demand_heat.csv",
        demand_transport="results/prepare/{resolution}/demand_transport.csv",
    output:
        "results/prepare/{resolution}/combined_demands/demand_combined_sum_base.csv",
        "results/prepare/{resolution}/combined_demands/demand_combined_sum_res_50.csv",
        "results/prepare/{resolution}/combined_demands/demand_combined_sum_res_75.csv",
        "results/prepare/{resolution}/combined_demands/demand_combined_sum_res_90.csv",
        scenarios=directory("results/prepare/{resolution}/combined_demands/"),
        plot="results/prepare/{resolution}/combined_demands/demand_assumptions.png",
    script:
        "../scripts/combine_demands.py"

# prepare the rest
rule prepare_nodes_area_techs:
    input:
        nodes="results/prepare/{resolution}/nodes.csv",
        area_onshore="results/prepare/{resolution}/area_potential_wind_onshore.parquet",
        area_offshore="results/prepare/{resolution}/area_potential_wind_offshore.parquet",
    output:
        nodes_area="results/prepare/{resolution}/nodes_area.csv",
        techs="results/prepare/{resolution}/techs.csv",
    script: "../scripts/prepare_nodes_area_techs.py"


rule apply_scaling_factors:
    input:
        demand_combined_sum_base="results/prepare/{resolution}/combined_demands/demand_combined_sum_base.csv",
        demand_combined_sum_res_50="results/prepare/{resolution}/combined_demands/demand_combined_sum_res_50.csv",
        demand_combined_sum_res_75="results/prepare/{resolution}/combined_demands/demand_combined_sum_res_75.csv",
        demand_combined_sum_res_90="results/prepare/{resolution}/combined_demands/demand_combined_sum_res_90.csv",
        flow_cap_max="results/prepare/{resolution}/flow_cap_max.csv",
        flow_cap_min="results/prepare/{resolution}/flow_cap_min.csv",
        links="results/prepare/{resolution}/links.csv",
        nodes_area="results/prepare/{resolution}/nodes_area.csv",
    output:
        demand_combined_sum_base="results/prepare/{resolution}/scaled/combined_demands/demand_combined_sum_base.csv",
        demand_combined_sum_res_50="results/prepare/{resolution}/scaled/combined_demands/demand_combined_sum_res_50.csv",
        demand_combined_sum_res_75="results/prepare/{resolution}/scaled/combined_demands/demand_combined_sum_res_75.csv",
        demand_combined_sum_res_90="results/prepare/{resolution}/scaled/combined_demands/demand_combined_sum_res_90.csv",
        flow_cap_max="results/prepare/{resolution}/scaled/flow_cap_max.csv",
        flow_cap_min="results/prepare/{resolution}/scaled/flow_cap_min.csv",
        links="results/prepare/{resolution}/scaled/links.csv",
        nodes_area="results/prepare/{resolution}/scaled/nodes_area.csv",
    script: "../scripts/apply_scaling_factors.py"

