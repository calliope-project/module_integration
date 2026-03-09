import pandas as pd

if __name__ == "__main__":
    dfs = []
    for path in snakemake.input:
        df = pd.read_parquet(path)
        dfs.append(df)

    dfs = pd.concat(dfs, ignore_index=True)

    dfs.to_parquet(snakemake.output[0], index=False)
