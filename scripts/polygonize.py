import tqdm
import click
from shapely import geometry
import fiona
import rasterio
from affine import Affine
from rasterio import features
import numexpr as ne

@click.command()
@click.argument('in_raster')
@click.argument('out')
@click.option('driver', '-d', required=False, type=str, default='ESRI Shapefile',
              help="Output vector format (ogr driver). Default is 'ESRI Shapefile'")
@click.option('band', '-b', required=False, type=int, default=1,
              help="Input raster band to process")
@click.option('connectivity', '-c', required=False, type=int, default=4,
              help="Connectivity (4 or 8). Default is 4.")
@click.option('mask', '-m', required=False, type=bool, default=True,
              help="Should zero values be interpreted as masked? Default is true.")
@click.option('expression', '-x', required=False, type=str, default=None,
              help="Expression to apply before vectorizing like in gdal_calc.py (e.g., 'data>=2').")
def main(in_raster, out, driver, band, connectivity, mask, expression=None):
    # specify the output schema for the output vector file
    schema = {'geometry'  : 'Polygon',
              'properties': {'val': 'int'}}
    with rasterio.open(in_raster) as src, \
            fiona.open(out, 'w', driver=driver, schema=schema, crs=src.crs) as dst:

        # check that the dataset is tiled
        if src.profile['tiled'] is False:
            err = """Input dataset is not tiled. This may affect performance or appearance of results.
                     It is recommended that you stop processing and tile your raster before running this utility:
                     gdal_translate -co TILED=YES in_raster.tif  out_raster.tif"""
            raise TypeError(err)

        src_affine = src.transform
        for ji, window in tqdm.tqdm(list(src.block_windows(band))):
            data = src.read(band, window=window)
            window_affine = Affine(src_affine.a,
                                   src_affine.b,
                                   src_affine.c + window.col_off * src_affine.a,
                                   src_affine.d,
                                   src_affine.e,
                                   src_affine.f + window.row_off * src_affine.e)

            if expression is not None:
                # apply the expression to the data
                if 'data' not in expression:
                    raise ValueError("Invalid expression. Must include 'data'.")
                ev_data = ne.evaluate(expression).astype(data.dtype)
            else:
                ev_data = data

            if mask is True:
                feature_mask = ev_data
            else:
                feature_mask = None

            feats = features.shapes(ev_data, mask=feature_mask, connectivity=connectivity, transform=window_affine)
            for g, v in feats:
                geom = geometry.shape(g)
                if geom.is_valid is True:
                    g_valid = geom
                else:
                    g_valid = geom.buffer(0)

                if isinstance(g_valid, geometry.MultiPolygon):
                    for g_part in g_valid:
                        geojson = {'geometry': g_part.__geo_interface__,
                                   'properties': {'val': v}}
                        dst.write(geojson)
                else:
                    geojson = {'geometry': g_valid.__geo_interface__,
                               'properties': {'val': v}}
                    dst.write(geojson)

if __name__ == '__main__':
    main()