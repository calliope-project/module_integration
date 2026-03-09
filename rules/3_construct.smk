rule construct_model:
    input:
        nodes=PATH_PREPARE / "scaled/nodes_area.csv",
        techs=PATH_PREPARE / "techs.csv",
        links=PATH_PREPARE / "scaled/links.csv",
        flow_cap_min=PATH_PREPARE / "scaled/flow_cap_min.csv",
        flow_cap_max=PATH_PREPARE / "scaled/flow_cap_max.csv",
        demand=PATH_PREPARE / "scaled/combined_demands/demand_combined_sum_{scenario}.csv",
        wind_onshore=PATH_PREPARE / "onshore/wind_onshore/capacityfactors_wind_onshore_3MW.csv",
        wind_offshore=PATH_PREPARE / "offshore/wind_offshore/capacityfactors_wind_offshore_3.6MW.csv",
        pv_open_field=PATH_PREPARE / "onshore/pv_open_field/capacityfactors_pv_open_field_CSi_S.csv",
        pv_rooftop=PATH_PREPARE / "onshore/pv_rooftop/capacityfactors_pv_rooftop_CSi_S.csv",
        model="template_components/model_{template}.yaml",
    output:
        destination=directory(PATH_MODELS + "construct"),
        model_file=PATH_MODELS + "construct/model.yaml",
    script: "../scripts/construct_model.py"
