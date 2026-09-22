from pathlib import Path
import logging

import pandas as pd

from lib.schema import Nodes, Techs, Links, NodeTimeSeries, ConsistentModel
from lib.utils import configure_logging


def validate_schema(df, schema):
    if schema == "Nodes":
        return Nodes.validate(df)
    elif schema == "Techs":
        return Techs.validate(df)
    elif schema == "Links":
        return Links.validate(df)
    elif schema == "NodeTimeSeries":
        return NodeTimeSeries.validate(df)
    else:
        raise ValueError(f"Unknown schema: {schema}")


logger = logging.getLogger()


if __name__ == "__main__":
    configure_logging(config={}, log=[str(snakemake.log)])

    warnings = False

    model = {
        "nodes": {},
        "techs": {},
        "links": {},
        "node_time_series": {}
    }

    for file, model_file in snakemake.config["model_files"].items():
        file_path = Path(snakemake.params.base_path) / file
        schema = model_file["schema"]

        table = pd.read_parquet(file_path)
        model[schema][file] = table
    
    try:
        ConsistentModel(**model)
        logger.info("Model is consistent.")
    except Exception as e:
        logger.warning(e)
        warnings = True

    if not warnings:
        with open(snakemake.output[0], "w") as f:
            f.write("All files are valid under the given config.")
