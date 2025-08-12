from lib.templater import Templater
from pathlib import Path


if __name__ == "__main__":

    templater = Templater(snakemake.output[0])

    def filter_dictionary(dictionary, filter_func):
        """Filter a dictionary based on a function."""
        return {k: v for k, v in dictionary.items() if filter_func(k, v)}

    data_tables = filter_dictionary(snakemake.input, lambda k, v: v.endswith(".csv"))
    templates = filter_dictionary(snakemake.input, lambda k, v: v.endswith(".yaml"))

    for key, value in data_tables.items():
        print(f"Adding data_table {key} with source {value}")
        templater.add_data_table(key, source=value)

    for key, value in templates.items():
        print(f"Adding template {key} with source {value}")
        templater.add_template(key, source=value)

    templater.parametrise_templates()
    templater.copy_data_tables()
