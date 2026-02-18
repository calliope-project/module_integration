import pandas as pd
from pandera.pandas import DataFrameModel, Field, dataframe_check
from pandera.typing import Series
from typing import Optional
import re


class Nodes(DataFrameModel):
    """
    Schema for model nodes.
    """
    nodes: Series[str] = Field(unique=True)


class Links(DataFrameModel):
    """
    Schema for model links.
    """
    # links (techs) must be unique.
    techs: Series[str] = Field(unique=True)
    # 'from_node' must not be empty.
    from_node: Series[str] = Field()  # not nullable by default
    # 'to_node' must not be empty.
    to_node: Series[str] = Field()  # not nullable by default

    @dataframe_check
    def check_alphabetic_order(cls, df: pd.DataFrame) -> Series[bool]:
        """'from_node' and 'to_node' must be ordered alphabetically."""
        return df["from_node"] < df["to_node"]

    @dataframe_check
    def naming_convention(cls, df: pd.DataFrame) -> Series[bool]:
        """Name must obey the naming convention {from_node}_{to_node}."""
        def name(row):
            return re.compile(
                f"{row['from_node']}_to_{row['to_node']}(_[0-9]+)?$"
            )
        def match_row(row):
            return name(row).match(row["techs"]) is not None
        return df.apply(match_row, axis=1)


class Techs(DataFrameModel):
    """
    Schema for model technologies.
    """
    nodes: Series[str] = Field()
    techs: Series[str] = Field()
    carriers: Optional[Series[str]] = Field(nullable=True)


class NodeTimeSeries(DataFrameModel):
    """
    Schema for time series defined on nodes.
    """
    timesteps: Series[pd.Timestamp] = Field()
    nodes: Series[str] = Field()
    techs: Series[str] = Field()
    carriers: Optional[Series[str]] = Field(nullable=True)

