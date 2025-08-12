import pandas as pd


if __name__ == "__main__":
    non_overlap = set(dict(snakemake.input).keys()).symmetric_difference(
        set(dict(snakemake.output).keys())
    )
    assert not non_overlap, f"Input and output must match, but {non_overlap} does not match."

    for key, value in snakemake.input.items():
        zero_tol = float(snakemake.config["zero_tol"])

        header = snakemake.config["scaling"][key]["header"]
        index_col = snakemake.config["scaling"][key]["index_col"]
        scaling = snakemake.config["scaling"][key]["scaling"]

        df = pd.read_csv(value, header=header, index_col=index_col)

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
            df[col] = df[col].where(df[col] >= zero_tol, 0.0)

        df.to_csv(snakemake.output[key], index=True)
