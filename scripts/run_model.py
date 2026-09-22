import argparse
from pathlib import Path
import logging
import calliope
import datetime
from lib.utils import configure_logging


logger = logging.getLogger()


def main(
    model: str | Path, scenario: str | Path, log: str | Path, destination: str | Path
):
    configure_logging(config={}, log=[log])
    print(log[0])
    calliope.set_log_verbosity(
        "info", include_solver_output=True, capture_warnings=True
    )
    model = calliope.Model(model, scenario=scenario)

    logger.info(f"Starting the model run at {datetime.datetime.now()}")
    model.build()
    model.solve()

    logger.info(f"Finished the model run at {datetime.datetime.now()}")

    logger.info(f"Saving results to {destination}")
    model.to_netcdf(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("scenario")
    parser.add_argument("log")
    parser.add_argument("destination")
    args = parser.parse_args()

    main(**vars(args))
