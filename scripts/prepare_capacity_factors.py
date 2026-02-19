from pathlib import Path
import xarray as xr
import argparse


def main(capacityfactors, tech, zero_tol, destination):
    capacityfactors = xr.load_dataarray(capacityfactors)
    df = capacityfactors.to_series()
    df = df.unstack(df.index.names[1])

    # set values smaller than zero_tol to zero
    zero_tol = float(zero_tol)
    df = df.where(df >= zero_tol, 0.0)

    df.to_parquet(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("capacityfactors")
    parser.add_argument("tech")
    parser.add_argument("zero_tol")
    parser.add_argument("destination")
    args = parser.parse_args()

    main(**vars(args))
