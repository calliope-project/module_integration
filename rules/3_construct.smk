rule construct_model:
    input:
        nodes=PATH_PREPARE / "nodes.parquet",
        techs=PATH_PREPARE / "techs.parquet",
        links=PATH_PREPARE / "scaled/links.parquet",
        flow_cap_min=PATH_PREPARE / "scaled/powerplants_combined.parquet",
        flow_cap_max=PATH_PREPARE / "scaled/power_potentials_combined.parquet",
        demand=PATH_PREPARE / "scaled/combined_demands/demand_combined_sum_{scenario}.parquet",
        wind_onshore=PATH_PREPARE / "onshore/wind_onshore/capacityfactors_wind_onshore_3MW.parquet",
        wind_offshore=PATH_PREPARE / "offshore/wind_offshore/capacityfactors_wind_offshore_3.6MW.parquet",
        pv_open_field=PATH_PREPARE / "onshore/pv_open_field/capacityfactors_pv_open_field_CSi_S.parquet",
        pv_rooftop=PATH_PREPARE / "onshore/pv_rooftop/capacityfactors_pv_rooftop_CSi_S.parquet",
        model="template_components/model_{template}.yaml",
        validated="results/prepare/{shape}/validated.txt"
    output:
        destination=directory(PATH_MODELS + "construct"),
        model_file=PATH_MODELS + "construct/model.yaml",
    script: "../scripts/construct_model.py"
