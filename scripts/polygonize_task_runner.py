import os
import json
import glob
import polygonize


def convert_type(var, f, expected_type):

    # try to convert the inputs to correct types
    if var is None:
        return None

    try:
        var = f(var)
    except ValueError as e:
        err = "Inputs {var} cannot be converted to type {expected_type}".format(var=var,
                                                                                expected_type=expected_type)
        raise ValueError(err)

    return var


def main():

    # get the inputs
    input_folder_tif = '/mnt/work/input/tif'
    string_ports = '/mnt/work/input/ports.json'

    # create output directory
    out_path = '/mnt/work/output/data'
    if os.path.exists(out_path) is False:
        os.makedirs(out_path)

    # read the inputs
    with open(string_ports) as ports:
        inputs = json.load(ports)
    out_name = inputs.get('out_name', 'polygons.shp')
    driver = inputs.get('driver', 'ESRI Shapefile')
    band = inputs.get('band', '1')
    connectivity = inputs.get('connectivity', '4')
    mask = inputs.get('mask', 'True')
    expression = inputs.get('expression', None)

    # convert the inputs to the correct dtypes
    out_name = convert_type(out_name, str, 'String')
    driver = convert_type(driver, str, 'String')
    band = convert_type(band, int, 'Integer')
    connectivity = convert_type(connectivity, int, 'Integer')
    mask = convert_type(mask, bool, 'Boolean')
    expression = convert_type(expression, str, 'String')

    # get the raster in the input folder
    rasters = glob.glob1(input_folder_tif, '*.tif')
    if len(rasters) == 0:
        raise ValueError("No tifs found in input data port 'reference'")
    if len(rasters) > 1:
        raise ValueError("Multiple tifs found in input data port 'reference'")
    in_raster = os.path.join(input_folder_tif, rasters[0])

    # set the output file path
    out = os.path.join(out_path, out_name)

    print("Polygonizing raster...")
    # run the processing
    polygonize.main([in_raster, out, '-d', driver, '-b', band, '-c', connectivity, '-m', mask, '-x', expression])
    print("Polygonization process completed successfully.")


if __name__ == '__main__':
    main()
