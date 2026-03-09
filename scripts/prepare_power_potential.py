from pathlib import Path
import logging
import geopandas as gpd
import pandas as pd

from _schemas import AreaPotential, PowerDensity
from lib.data_processing import map_values, ShapeTechMatcher

logger = logging.getLogger(__name__)


def get_flow_cap_max(area_potential, power_density, tech):
    m2_to_km2 = 1e-6  # Convert m^2 to km^2
    print(f"Calculating power potential for {tech}.")
    power_density = power_density.set_index("techs")["power_density_MW_per_km2"]

    area_potential = (
        area_potential
            .set_index("shape_id")
            .dropna(subset="sum")
            .drop(columns=["geometry"])
            .multiply({"sum": m2_to_km2})
    )

    print(f"Multiply with power density of {tech}: {power_density[tech]} MW per km^2")
    power_potential = area_potential * power_density[tech]

    # formatting the result
    power_potential = power_potential.rename(columns={"sum": "flow_cap_max"})
    power_potential["techs"] = tech
    power_potential = power_potential[["techs", "flow_cap_max"]]
    power_potential = power_potential.reset_index()

    return power_potential


def main(
    path_area_potential: str | Path,
    path_power_densities: str | Path,
    path_shapes: str | Path,
    map_shapes_to_nodes: str | Path,
    config: dict,
    destination: str | Path,
):
    # load data
    power_densities = pd.read_csv(path_power_densities)
    area_potential = gpd.read_parquet(path_area_potential)
    shapes = gpd.read_parquet(path_shapes)
    map_shapes_to_nodes = pd.read_parquet(map_shapes_to_nodes)
    map_shapes_to_nodes = map_shapes_to_nodes.set_index("shape_id")["nodes"].to_dict()

    # validate
    power_densities = PowerDensity.validate(power_densities)
    area_potential = AreaPotential.validate(area_potential)

    # calculate power potential
    power_potential = get_flow_cap_max(area_potential, power_densities, snakemake.wildcards.tech)

    # select shape_class that matches for tech
    matcher = ShapeTechMatcher(shapes=shapes, techs_land=config["techs_onshore"], techs_maritime=config["techs_offshore"])
    condition = power_potential.apply(lambda row: matcher.shape_matches_tech(row["shape_id"], row["techs"]), axis=1)
    power_potential = power_potential.loc[condition]

    # map shapes to nodes
    power_potential = map_values(power_potential, map_shapes_to_nodes, column="shape_id")
    power_potential = power_potential.rename(columns={"shape_id": "nodes"})

    power_potential.to_parquet(destination)


if __name__ == "__main__":
    main(
        path_area_potential=snakemake.input.area_potential,
        path_power_densities=snakemake.input.power_densities,
        path_shapes=snakemake.input.shapes,
        map_shapes_to_nodes=snakemake.input.map_shapes_to_nodes,
        config=snakemake.config,
        destination=snakemake.output[0],
    )
