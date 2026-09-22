import pandas as pd


if __name__ == "__main__":
    zero_tol = snakemake.params["zero_tol"]

    scaling = snakemake.params["scaling"]

    df = pd.read_parquet(snakemake.input)

    if isinstance(scaling, str):
        scaling_factor = snakemake.config["scaling-factors"][scaling]
        scaling_factors = {col: scaling_factor for col in df.columns}

    elif isinstance(scaling, dict):
        scaling_factors = {
            col: snakemake.config["scaling-factors"][scal] for col, scal in scaling.items()
        }

    for col, factor in scaling_factors.items():
        print(f"Scaling {col} by factor {factor}")
        df[col] *= factor
        if zero_tol is not None:
            df[col] = df[col].where(df[col] >= zero_tol, 0.0)

    df.to_parquet(str(snakemake.output))
