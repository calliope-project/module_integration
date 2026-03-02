import pandas as pd
from pandera.pandas import DataFrameModel, Field, dataframe_check
from pandera.typing import Series, Index
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
    link_from: Series[str] = Field()  # not nullable by default
    # 'to_node' must not be empty.
    link_to: Series[str] = Field()  # not nullable by default

    @dataframe_check
    def check_alphabetic_order(cls, df: pd.DataFrame) -> Series[bool]:
        """'link_from' and 'link_to' must be ordered alphabetically."""
        return df["link_from"] < df["link_to"]

    @dataframe_check
    def naming_convention(cls, df: pd.DataFrame) -> Series[bool]:
        """Name must obey the naming convention {link_from}_{link_to}."""
        def name(row):
            return re.compile(
                f"{row['link_from']}_to_{row['link_to']}(_[0-9]+)?$"
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
    # index
    timesteps: Index[pd.Timestamp] = Field()
