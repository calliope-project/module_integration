import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


COLUMNS = {
    "shape_id": "nodes",
    "technology": "techs",
    "output_capacity_mw": "flow_cap_min",
}


def remove_suffix(df):

    df["nodes"] = df["nodes"].str.replace("_land", "")
    df["nodes"] = df["nodes"].str.replace("_maritime", "")

    return df


def prepare_flow_cap_min(df, destination):
    flow_cap_min = df.loc[:, COLUMNS.keys()].rename(columns=COLUMNS)
    flow_cap_min = flow_cap_min[flow_cap_min["flow_cap_min"] > 0]
    flow_cap_min = remove_suffix(flow_cap_min)
    flow_cap_min = flow_cap_min.groupby(["nodes", "techs"], as_index=False).sum()

    techs = snakemake.config["techs_onshore"] + snakemake.config["techs_offshore"]
    flow_cap_min = flow_cap_min.loc[flow_cap_min["techs"].isin(techs)]

    flow_cap_min.to_csv(destination, index=False)


if __name__ == "__main__":
    dfs = []
    for path in snakemake.input:
        logger.info(f"Processing file: {path}")
        df = pd.read_parquet(path)
        dfs.append(df)

    dfs = pd.concat(dfs, ignore_index=True)

    prepare_flow_cap_min(dfs, snakemake.output[0])
