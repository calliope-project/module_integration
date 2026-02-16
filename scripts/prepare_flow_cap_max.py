from pathlib import Path
import logging
import rioxarray as rxr
import geopandas as gpd
import pandas as pd
from _schemas import AreaPotential, PowerDensity


logger = logging.getLogger(__name__)


def get_flow_cap_max(area_potential, power_density, tech):
    m2_to_km2 = 1e-6  # Convert m^2 to km^2
    print(f"Calculating flow_cap_max for {tech}.")
    power_density = power_density.set_index("techs")["power_density_MW_per_km2"]
    area_potential = (
        area_potential.dropna(subset="sum").drop(columns=["geometry"]).multiply({"sum": m2_to_km2})
    )

    print(f"Multiply with power density of {tech}: {power_density[tech]} MW per km^2")
    flow_cap_max = area_potential * power_density[tech]

    # formatting the result
    flow_cap_max = flow_cap_max.rename(columns={"sum": "flow_cap_max"})
    flow_cap_max["techs"] = tech
    flow_cap_max = flow_cap_max[["techs", "flow_cap_max"]]
    flow_cap_max.index.name = "nodes"

    return flow_cap_max


def remove_suffix(df):
    df = df.reset_index()
    df["nodes"] = df["nodes"].str.replace("_land", "")
    df["nodes"] = df["nodes"].str.replace("_maritime", "")
    df = df.set_index("nodes")
    return df


def main(
    path_area_potentials_pv_rooftop: str | Path,
    path_area_potentials_wind_offshore: str | Path,
    path_power_density: str | Path,
    path_flow_cap_max: str | Path,
):
    power_density = pd.read_csv(path_power_density)
    area_pv_rooftop = gpd.read_parquet(path_area_potentials_pv_rooftop)
    area_wind_offshore = gpd.read_parquet(path_area_potentials_wind_offshore)

    power_density = PowerDensity.validate(power_density)
    area_pv_rooftop = AreaPotential.validate(area_pv_rooftop)
    area_wind_offshore = AreaPotential.validate(area_wind_offshore)

    flow_cap_max_pv_rooftop = get_flow_cap_max(area_pv_rooftop, power_density, "pv_rooftop")
    flow_cap_max_wind_offshore = get_flow_cap_max(
        area_wind_offshore, power_density, "wind_offshore"
    )

    join_nodes_onshore_offshore = True
    if join_nodes_onshore_offshore:
        flow_cap_max_wind_offshore = remove_suffix(flow_cap_max_wind_offshore)
        flow_cap_max_pv_rooftop = remove_suffix(flow_cap_max_pv_rooftop)

    flow_cap_max = pd.concat(
        [flow_cap_max_pv_rooftop, flow_cap_max_wind_offshore],
    )

    # filter techs
    techs = snakemake.config["techs_onshore"] + snakemake.config["techs_offshore"]
    flow_cap_max = flow_cap_max.loc[flow_cap_max["techs"].isin(techs)]

    flow_cap_max.to_parquet(path_flow_cap_max)


if __name__ == "__main__":
    main(
        path_area_potentials_pv_rooftop=snakemake.input.area_potentials_pv_rooftop,
        path_area_potentials_wind_offshore=snakemake.input.area_potentials_wind_offshore,
        path_power_density=snakemake.input.power_density,
        path_flow_cap_max=snakemake.output.path_flow_cap_max,
    )
