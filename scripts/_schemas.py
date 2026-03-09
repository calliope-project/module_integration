from pandera.pandas import DataFrameModel, Field
from pandera.typing import Series
import geopandas as gpd


class AreaPotential(DataFrameModel):
    class Config:
        coerce = True

    shape_id: Series[str] = Field(description="Unique identifier for the area")
    sum: Series[float] = Field(description="Total area in square meters", nullable=True)
    geometry: Series[gpd.array.GeometryDtype] = Field(
        description="Geometry of the area in WKT format"
    )


class PowerDensity(DataFrameModel):
    class Config:
        coerce = True

    techs: Series[str] = Field(description="Technology type")
    power_density_MW_per_km2: Series[float] = Field(
        description="Power density in MW/km^2"
    )
