from pathlib import Path
import logging

import pandas as pd

from lib.schema import Nodes, Techs, Links, NodeTimeSeries
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

    for model_file in snakemake.config["model_files"]:
        file = model_file["file"]
        file_path = Path(snakemake.params.base_path) / file
        schema = model_file["schema"]

        try:
            df = pd.read_parquet(file_path)
            df = validate_schema(df, schema)
            logger.info(f"{file_path} is valid according to the '{schema}' schema.")
        except Exception as e:
            logger.warning(f"{file_path} failed validation: {e}")
            warnings = True

    if not warnings:
        with open(snakemake.output[0], "w") as f:
            f.write("All files are valid under the given config.")
