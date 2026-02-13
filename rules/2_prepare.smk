# prepare electricity grid
rule prepare_calliope_links_nodes:
    message: "Prepare calliope links and nodes."
    input:
        lines="results/module_electricity_grid/{nuts_level}/results/lines_clean.parquet",
        links="results/module_electricity_grid/{nuts_level}/results/links_clean.parquet",
        buses="results/module_electricity_grid/{nuts_level}/results/buses_clean.parquet",
    output:
        calliope_links="results/prepare/{nuts_level}/links.csv",
        calliope_nodes="results/prepare/{nuts_level}/nodes.csv",
        calliope_links_geo="results/prepare/{nuts_level}/links.parquet",
    params:
        limit_scope=False
    script:
        "../scripts/prepare_calliope_links_nodes.py"

# prepare powerplants brown-field capacities
rule prepare_flow_cap_min:
    input: 
        expand(
            "results/module_powerplants/results/{{resolution}}/aggregated/adjusted/{category}.parquet",
            category=["bioenergy", "fossil", "geothermal", "hydropower", "nuclear", "wind"]
        )
    output: 
        "results/prepare/{resolution}/flow_cap_min.csv"
    script: "../scripts/prepare_flow_cap_min.py"

# prepare area potentials
rule aggregate_raster_to_poly:
    input:
        raster="results/prepare/raster/{dataset}.tif",
        polygons="results/prepare/{resolution}/shapes.parquet",
    output: "results/prepare/{resolution}/{dataset}.parquet"
    shell: "python scripts/aggregate_raster_to_poly.py {input.raster} {input.polygons} {output[0]}"

rule prepare_flow_cap_max:
    input: 
        area_potentials_pv_rooftop="results/prepare/{resolution}/area_potential_pv_rooftop.parquet",
        area_potentials_wind_offshore="results/prepare/{resolution}/area_potential_wind_offshore.parquet",
        power_density="data/prepare/power_densities/power_densities.csv",
    output:
        path_flow_cap_max="results/prepare/{resolution}/flow_cap_max.csv",
    script: "../scripts/prepare_flow_cap_max.py"

# prepare capacity factors for pv and wind
rule prepare_capacity_factors_csv:
    message: "Convert the capacity factors to calliope ready format."
    input: "results/module_pv_wind/results/era5/{resolution}_{on_or_offshore}/{name_layout}/capacityfactors_{tech}.nc"  # {resolution}/{config['scope']['temporal']['year']}/
    output: "results/prepare/{resolution}/{on_or_offshore}/{name_layout}/capacityfactors_{tech}.csv"
    params:
        zero_tol = config["capacity_factors"]["zero_tol"]
    wildcard_constraints:
        on_or_offshore = "onshore|offshore",
        tech = "wind_offshore_3.6MW|wind_onshore_3MW|pv_rooftop_CSi_S|pv_rooftop_CSi_W|pv_open_field_CSi_S",
    shell: "python scripts/prepare_capacity_factors_csv.py {input} {wildcards.name_layout} {params.zero_tol} {output}"

# prepare demands
rule demand_electricity_output:
    message: "Move into place the electricity demand timeseries."
    input: "results/module_demand_electricity/results/demand_electricity_{resolution}_MW.parquet"
    output: "results/prepare/{resolution}/demand_electricity.csv"
    run:
        import pandas as pd
        df = pd.read_parquet(input[0])
        df.index.name = None
        df.columns = pd.MultiIndex.from_product([["demand_electricity"], df.columns], names=['techs', 'nodes'])
        df.to_csv(output[0])

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
rule prepare_node_link_groups:
    input:
        nodes_coarse="results/prepare/{resolution1}/nodes.csv",
        links_coarse="results/prepare/{resolution1}/links.csv",
        nodes_fine="results/prepare/{resolution2}/nodes.csv",
        links_fine="results/prepare/{resolution2}/links.csv",
    output:
        node_groups="results/prepare/{resolution2}/node_groups_{resolution2}_to_{resolution1}.csv",
        link_groups="results/prepare/{resolution2}/link_groups_{resolution2}_to_{resolution1}.csv"
    wildcard_constraints:
        resolution1="NUTS0|NUTS2",
    script: "../scripts/prepare_node_link_groups.py"


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

