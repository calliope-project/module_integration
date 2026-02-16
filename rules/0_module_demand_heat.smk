rule demand_heat_output:
    message: "Move into place the heat demand timeseries."
    input: "data/module_demand_heat/{nuts_level}/demand_heat_profiles_MW.parquet"
    output: "results/prepare/{nuts_level}/demand_heat.parquet"
    wildcard_constraints:
        nuts_level="NUTS0|NUTS2|NUTS3"
    run:
        import pandas as pd
        df = pd.read_parquet(input[0])
        df.index.name = None
        df.columns = pd.MultiIndex.from_product([["demand_heat"], df.columns], names=['techs', 'nodes'])
        df.to_parquet(output[0])