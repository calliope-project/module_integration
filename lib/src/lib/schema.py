import pandas as pd
from pandera.pandas import DataFrameModel, Field, dataframe_check
from pandera.typing import DataFrame, Series, Index
from typing import Dict, Optional
import re

import pydantic


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


class ConsistentModel(pydantic.BaseModel):
    """
    """
    nodes: Dict[str, DataFrame[Nodes]] = {}
    techs: Dict[str, DataFrame[Techs]] = {}
    links: Dict[str, DataFrame[Links]] = {}
    node_time_series: Dict[str, DataFrame[NodeTimeSeries]] = {}
    
    @pydantic.model_validator(mode="after")
    def check_consistency(self):
        """Check that all nodes in techs and links are defined in nodes."""
        defined_nodes = set()
        for node_df in self.nodes.values():
            defined_nodes.update(node_df["nodes"].unique())
        
        for tech_df in self.techs.values():
            undefined_nodes = set(tech_df["nodes"]) - defined_nodes
            if undefined_nodes:
                raise ValueError(f"Techs contain undefined nodes: {undefined_nodes}")

        for link_df in self.links.values():
            undefined_link_from = set(link_df["link_from"]) - defined_nodes
            if undefined_link_from:
                raise ValueError(f"Links contain undefined 'from' nodes: {undefined_link_from}")
            
            undefined_link_to = set(link_df["link_to"]) - defined_nodes
            if undefined_link_to:
                raise ValueError(f"Links contain undefined 'to' nodes: {undefined_link_to}")
            
        for node_ts_df in self.node_time_series.values():
            undefined_nodes = set(node_ts_df.columns) - defined_nodes
            if undefined_nodes:
                raise ValueError(f"Node time series contain undefined nodes: {undefined_nodes}")
        
        return self