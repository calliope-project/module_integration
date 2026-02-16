rule demand_transport_output:
    message: "Move into place the transport demand timeseries."
    input: "data/module_demand_transport/{nuts_level}/demand_profiles_total_MW.parquet"
    output: "results/prepare/{nuts_level}/demand_transport.parquet"
    wildcard_constraints:
        nuts_level="NUTS0|NUTS2|NUTS3"
    run:
        import pandas as pd
        df = pd.read_parquet(input[0])
        df.index.name = None
        df.columns = pd.MultiIndex.from_product([["demand_transport"], df.columns], names=['techs', 'nodes'])
        df.to_parquet(output[0])
