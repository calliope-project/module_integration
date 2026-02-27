import argparse
import gregor
import geopandas as gpd
import rioxarray as rxr


def main(raster, polygons, output, nodata=-1):
    raster_data = rxr.open_rasterio(raster, nodata=nodata, masked=True).sel(band=1)
    gdf_polygons = gpd.read_parquet(polygons)
    gdf_polygons = gdf_polygons.set_index("shape_id")
    gdf_polygons = gdf_polygons["geometry"]

    result = gregor.aggregate.aggregate_raster_to_polygon(raster_data, gdf_polygons)
    result = result.reset_index()
    result.to_parquet(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("raster")
    parser.add_argument("polygons")
    parser.add_argument("output")
    args = parser.parse_args()

    main(**vars(args))
