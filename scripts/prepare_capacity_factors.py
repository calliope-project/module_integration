from pathlib import Path
import xarray as xr
import argparse


def main(capacityfactors, tech, zero_tol, destination):
    capacityfactors = xr.load_dataarray(capacityfactors)
    df = capacityfactors.to_dataframe(name=tech)
    df = df.unstack(df.index.names[1])

    df.columns = df.columns.rename("techs", level=0)
    df.columns = df.columns.rename("nodes", level=1)
    df.index.name = None

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
