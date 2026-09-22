import pandas as pd

from lib.templater import Templater


def parquet_to_csv(source, target):
    """Convert a parquet file to csv."""
    df = pd.read_parquet(source)
    if isinstance(df.index, pd.DatetimeIndex):
        df.to_csv(target, index=True)
    elif isinstance(df.index, pd.RangeIndex):
        df.to_csv(target, index=False)
    else:
        df.to_csv(target, index=False)


if __name__ == "__main__":

    templater = Templater(snakemake.output[0])

    def filter_dictionary(dictionary, filter_func):
        """Filter a dictionary based on a function."""
        return {k: v for k, v in dictionary.items() if filter_func(k, v)}

    data_tables = filter_dictionary(snakemake.input, lambda k, v: v.endswith(".parquet"))
    templates = filter_dictionary(snakemake.input, lambda k, v: v.endswith(".yaml"))

    for key, value in data_tables.items():
        print(f"Adding data_table {key} with source {value}")
        templater.add_data_table(key, source=value)

    for key, value in templates.items():
        print(f"Adding template {key} with source {value}")
        templater.add_template(key, source=value)

    templater.parametrise_templates(pd.read_parquet)
    templater.copy_data_tables(parquet_to_csv)
