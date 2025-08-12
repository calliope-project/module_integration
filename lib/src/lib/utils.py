import pandas as pd
from pathlib import Path
import yaml


def configure_logging(config, log):
    """
    Adapted from https://github.com/PyPSA/pypsa-eur/blob/master/scripts/_helpers.py

    Note: Must only be called once from the __main__ section of a script.

    The setup includes printing log messages to STDERR and to a log file defined
    by snakemake.log[0].

    Additional keywords from logging.basicConfig are accepted via the snakemake configuration
    file under snakemake.config.logging.

    Parameters
    ----------
    config : dict
    log : list
    """
    import logging
    import sys

    kwargs = config.get("logging", dict()).copy()
    kwargs.setdefault("level", "INFO")

    if log:
        logfile = log[0]
        kwargs.update(
            {
                "handlers": [
                    logging.FileHandler(logfile),
                    logging.StreamHandler(),
                ]
            }
        )

    logging.basicConfig(**kwargs)

    # Setup a function to handle uncaught exceptions and include them with their stacktrace into logfiles
    def handle_exception(exc_type, exc_value, exc_traceback):
        # Log the exception
        logger = logging.getLogger()
        logger.error(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception


def to_dict_of_list(df: pd.DataFrame, col_keys: str, col_values: str) -> dict:
    """Creates a dictionary containing lists from DataFrame."""
    return {
        key: [value for value in df.loc[df[col_keys] == key][col_values]]
        for key in df[col_keys].unique()
    }


def read_config(path_to_file):
    """Reads a configuration file."""
    path_to_file = Path(path_to_file)
    if not path_to_file.exists():
        raise ValueError("Config {} does not exist.".format(path_to_file))
    with path_to_file.open("r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise IOError(exc)
