import argparse
from pathlib import Path
import logging
import calliope
from lib.postprocessing import (
    model_specs,
    get_flow_cap,
    get_flow_cap_min,
    get_flow_cap_max,
    get_flow_cap_links,
    get_storage_cap,
    get_flow_out,
    get_link_flows,
    get_cost,
    get_from_to,
    get_emissions,
    get_area_use,
)
from lib.postprocessor import Processor, Postprocessor
from lib.postprocessing import get_flow_cap, get_flow_cap_min, get_flow_cap_max, get_flow_cap_links
from functools import partial


logger = logging.getLogger()


def create_model_specs(paths_models):
    all_model_specs = []
    for path_model in paths_models:
        path_model = Path(path_model)
        if not path_model.exists() or not path_model.suffix == ".nc":
            logger.warning(f"No model found at {path_model}. Skipping.")
            continue

        model = calliope.read_netcdf(path_model)
        all_model_specs.append(model_specs(model.name, model.inputs.attrs["scenario"], path_model))
    return all_model_specs


def main(paths_models: list[str | Path], destination: str | Path):
    destination = Path(destination)
    destination.mkdir()

    all_model_specs = create_model_specs(paths_models)
    if not all_model_specs:
        logger.error("No valid model specifications found. Exiting.")
        return

    CONV_100_GW_to_GW = 100
    CONV_1e4_km2_to_km2 = 1e4  # from 10.000 km2 to km2
    flow_cap = Processor(partial(get_flow_cap, rescale=CONV_100_GW_to_GW))
    flow_cap_min = Processor(partial(get_flow_cap_min, rescale=CONV_100_GW_to_GW))
    flow_cap_max = Processor(partial(get_flow_cap_max, rescale=CONV_100_GW_to_GW))
    flow_cap_links = Processor(partial(get_flow_cap_links, rescale=CONV_100_GW_to_GW))
    storage_cap = Processor(partial(get_storage_cap, rescale=CONV_100_GW_to_GW))
    flow_out = Processor(partial(get_flow_out, rescale=CONV_100_GW_to_GW))
    link_flows = Processor(partial(get_link_flows, rescale=CONV_100_GW_to_GW))
    cost = Processor(get_cost)
    emissions = Processor(get_emissions)
    area_use = Processor(partial(get_area_use, rescale=CONV_1e4_km2_to_km2))
    from_to = Processor(get_from_to)

    pp = Postprocessor(all_model_specs)

    for processor in [
        flow_cap,
        flow_cap_min,
        flow_cap_max,
        flow_cap_links,
        storage_cap,
        flow_out,
        link_flows,
        cost,
        emissions,
        area_use,
        from_to,
    ]:
        pp.add_processor(processor)


    pp.process_results()

    # Save results to CSV files
    flow_cap.results.to_csv(destination / "flow_cap.csv")
    flow_cap_min.results.to_csv(destination / "flow_cap_min.csv")
    flow_cap_max.results.to_csv(destination / "flow_cap_max.csv")
    flow_cap_links.results.to_csv(destination / "flow_cap_links.csv")
    storage_cap.results.to_csv(destination / "storage_cap.csv")
    flow_out.results.to_csv(destination / "flow_out.csv")
    link_flows.results.to_csv(destination / "link_flows.csv")
    cost.results.to_csv(destination / "cost.csv")
    emissions.results.to_csv(destination / "emissions.csv")
    area_use.results.to_csv(destination / "area_use.csv")
    from_to.results.to_csv(destination / "from_to.csv")

    logger.info("Postprocessing completed successfully.")
    logger.info(f"Results saved to {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths_models", nargs="+", type=str, help="Paths to the model files.")
    parser.add_argument("-d", "--destination")
    args = parser.parse_args()

    main(**vars(args))
