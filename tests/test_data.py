from unox import data as udata
from unox import unox as unox
import xarray as xr
import numpy as np
import pandas as pd
import os
import pytest

minimal_xr0 = xr.DataArray(
    data=[[[1], [2]], [[3], [4]]],
    coords={
        "lat": [-90, 90],
        "lon": [-180, 180],
        "time": [np.datetime64("2019-01-01")],
    },
    dims=["lat", "lon", "time"]
)

minimal_xr1 = xr.DataArray(
    data=[[[2], [4]], [[6], [8]]],
    coords={
        "Latitude": [-60, 60],
        "Longitude": [-100, 100],
        "Datetime": [np.datetime64("2009-05-01")],
    },
    dims=["Latitude", "Longitude", "Datetime"]
)

sample_datafiles = [
    'datafiles/sample_data/2019u10.nc',
    'datafiles/sample_data/daily_42602_2019.csv',
    'datafiles/sample_data/nox_2019_t106_US.nc',
    'datafiles/sample_data/TROPESS_reanalysis_mon_emi_nox_anth_2021.nc',
]

invalid_datasets = [
    "invalid_string",
    12345,
    None,
]

def test_generate_lats_lons():
    """Test the generate_lats_lons function."""
    # Test with the ERA5 sample data file
    sample_filepath = 'datafiles/sample_data/2019u10.nc'
    output_dir = 'tests/data_for_tests/'
    expected_lats = np.load('datafiles/lats.npy')
    expected_lons = np.load('datafiles/lons.npy')
    # Generate lats and lons with file path input
    actual_lats, actual_lons = udata.generate_lats_lons(dataset=sample_filepath, output_dir=output_dir)
    assert np.array_equal(actual_lats, expected_lats), f"Expected lats {expected_lats} do not match actual lats {actual_lats}"
    assert np.array_equal(actual_lons, expected_lons), f"Expected lons {expected_lons} do not match actual lons {actual_lons}"
    # Clean up generated files
    os.remove(os.path.join(output_dir, 'lats.npy'))
    os.remove(os.path.join(output_dir, 'lons.npy'))
    # Generate lats and lons with xarray dataset input
    xr_dataset = xr.open_dataset(sample_filepath)
    actual_lats, actual_lons = udata.generate_lats_lons(dataset=xr_dataset, output_dir=output_dir)
    assert np.array_equal(actual_lats, expected_lats), f"Expected lats {expected_lats} do not match actual lats {actual_lats}"
    assert np.array_equal(actual_lons, expected_lons), f"Expected lons {expected_lons} do not match actual lons {actual_lons}"
    # Clean up generated files
    os.remove(os.path.join(output_dir, 'lats.npy'))
    os.remove(os.path.join(output_dir, 'lons.npy'))

def test_get_extent():
    """Test the get_extent function."""
    # Test with sample data files
    expected_extents = [
        (11.776000022888184, 73.45700073242188, -174.375, -40.5),   # For 2019u10.nc
        (18.198712, 64.84569, -159.36624, -66.052237),              # For daily_42602_2019.csv
        (24.112, 58.878, -126.0, -59.625),                          # For nox_2019_t106_US.nc
        (-89.14199829101562, 89.14199829101562, 0 , 358.875),       # For TROPESS_reanalysis_mon_emi_nox_anth_2021.nc
    ]
    for i, datafile in enumerate(sample_datafiles):
        xr_dataset = udata.load_dataset(datafile)
        actual_extent = udata.get_extent(xr_dataset)
        assert list(actual_extent) == list(expected_extents[i]), f"Expected extent {expected_extents[i]} does not match actual extent {actual_extent} for {datafile}"
    # Test shifting longitudes in sample data files
    expected_extents = [
        (11.776000022888184, 73.45700073242188, 185.625, 319.5),    # For 2019u10.nc
        (18.198712, 64.84569, 200.63376, 293.947763),               # For daily_42602_2019.csv
        (24.112, 58.878, 234.0, 300.375),                           # For nox_2019_t106_US.nc
        (-89.14199829101562, 89.14199829101562, -178.875, 180),     # For TROPESS_reanalysis_mon_emi_nox_anth_2021.nc
    ]
    PM_centereds = [False, False, False, True]
    for i, datafile in enumerate(sample_datafiles):
        xr_dataset = udata.load_dataset(datafile)
        actual_extent = udata.get_extent(xr_dataset, shift_lons=True, PM_centered=PM_centereds[i])
        assert list(actual_extent) == list(expected_extents[i]), f"Expected extent {expected_extents[i]} does not match actual extent {actual_extent} for {datafile}"
    # Test with minimal xarray DataArray
    expected = (-90.0, 90.0, -180.0, 180.0)
    actual = udata.get_extent(minimal_xr0)
    assert actual == expected, f"Expected extent {expected} does not match actual extent {actual}"
    # Test with lats and lons
    lats = np.array([-90, 90])
    lons = np.array([-180, 180])
    expected = (-90.0, 90.0, -180.0, 180.0)
    actual = udata.get_extent(lats=lats, lons=lons)
    assert actual == expected, f"Expected extent {expected} does not match actual extent {actual}"
    # Select a tolerance for comparisons
    selected_tol = 1e-15
    # Test shifting longitudes
    lats = np.array([-90, -45, 45, 90])
    lons = np.array([0, 179.9, 180.1, 360])
    expected = (-90.0, 90.0, -179.9, 179.9)
    actual = udata.get_extent(lats=lats, lons=lons, shift_lons=True)
    assert np.allclose(expected, actual, atol=selected_tol, rtol=selected_tol), f"Expected extent {expected} does not match actual extent {actual}"
    # Test with invalid inputs
    for invalid_input in invalid_datasets:
        try:
            udata.get_extent(xr_dataset=invalid_input)
        except (TypeError, ValueError) as e:
            assert True, f"get_extent raised an exception on invalid input: {e}"
        else:
            assert False, f"get_extent did not raise an exception on invalid input: {invalid_input}"

def test_get_lats_lons():
    """Test the get_lats_lons function."""
    # Load a sample xarray dataset for testing
    sample_filepath = 'datafiles/sample_data/TROPESS_reanalysis_mon_emi_nox_anth_2021.nc'
    expected_lats = np.load('tests/data_for_tests/lats_TROPESS_reanalysis_mon_emi_nox_anth_2021.npy')
    expected_lons = np.load('tests/data_for_tests/lons_TROPESS_reanalysis_mon_emi_nox_anth_2021.npy')
    actual_lats, actual_lons = udata.get_lats_lons(xr_dataset=xr.open_dataset(sample_filepath))
    assert np.array_equal(actual_lats, expected_lats), f"Expected lats {expected_lats} do not match actual lats {actual_lats}"
    assert np.array_equal(actual_lons, expected_lons), f"Expected lons {expected_lons} do not match actual lons {actual_lons}"
    # Load a minimal xarray dataset for testing
    expected_lats = np.array([-90, 90])
    expected_lons = np.array([-180, 180])
    actual_lats, actual_lons = udata.get_lats_lons(xr_dataset=minimal_xr0)
    assert np.array_equal(actual_lats, expected_lats), f"Expected lats {expected_lats} do not match actual lats {actual_lats}"
    assert np.array_equal(actual_lons, expected_lons), f"Expected lons {expected_lons} do not match actual lons {actual_lons}"
    # Load with second minimal xarray dataset for testing
    expected_lats = np.array([-60, 60])
    expected_lons = np.array([-100, 100])
    actual_lats, actual_lons = udata.get_lats_lons(xr_dataset=minimal_xr1)
    assert np.array_equal(actual_lats, expected_lats), f"Expected lats {expected_lats} do not match actual lats {actual_lats}"
    assert np.array_equal(actual_lons, expected_lons), f"Expected lons {expected_lons} do not match actual lons {actual_lons}"
    # Test with invalid inputs
    for invalid_input in invalid_datasets:
        try:
            udata.get_lats_lons(xr_dataset=invalid_input)
        except (TypeError, ValueError) as e:
            assert True, f"get_lats_lons raised an exception on invalid input: {e}"
        else:
            assert False, f"get_lats_lons did not raise an exception on invalid input: {invalid_input}"

def test_get_latlon_resolution():
    """Test the get_latlon_resolution function."""
    # Test with sample data files
    expected_lat_reses = [
        '1.121472716331482 ± 0.0004995913477614522',    # For 2019u10.nc
        '0.00029904401007776294 ± 0.04318110228951739', # For daily_42602_2019.csv
        '1.121483870967742 ± 0.0004997397866077013',    # For nox_2019_t106_US.nc
        '1.1212830543518066 ± 0.11212115734815598',     # For TROPESS_reanalysis_mon_emi_nox_anth_2021.nc
    ]
    expected_lon_reses = [
        '1.125',                                        # For 2019u10.nc
        '0.0005982165372755421 ± 0.06670451139936068',  # For daily_42602_2019.csv
        '1.125',                                        # For nox_2019_t106_US.nc
        '1.125',                                        # For TROPESS_reanalysis_mon_emi_nox_anth_2021.nc
    ]
    for i, datafile in enumerate(sample_datafiles):
        xr_dataset = udata.load_dataset(datafile)
        actual_lat_res, actual_lon_res = udata.get_latlon_resolution(xr_dataset=xr_dataset)
        assert actual_lat_res == expected_lat_reses[i], f"Expected latitude resolution {expected_lat_reses[i]} does not match actual {actual_lat_res} for '{datafile}'"
        assert actual_lon_res == expected_lon_reses[i], f"Expected longitude resolution {expected_lon_reses[i]} does not match actual {actual_lon_res} for '{datafile}'"
    # Load a minimal xarray dataset for testing
    expected_lat_res = '180'
    expected_lon_res = '360'
    actual_lat_res, actual_lon_res = udata.get_latlon_resolution(xr_dataset=minimal_xr0)
    assert actual_lat_res == expected_lat_res, f"Expected latitude resolution {expected_lat_res} does not match actual {actual_lat_res}"
    assert actual_lon_res == expected_lon_res, f"Expected longitude resolution {expected_lon_res} does not match actual {actual_lon_res}"
    # Test with invalid inputs
    for invalid_input in invalid_datasets:
        try:
            udata.get_latlon_resolution(xr_dataset=invalid_input)
        except (TypeError, ValueError) as e:
            assert True, f"get_latlon_resolution raised an exception on invalid input: {e}"
        else:
            assert False, f"get_latlon_resolution did not raise an exception on invalid input: {invalid_input}"

def test_print_latlon_info():
    """Test the print_latlon_info function."""
    # Capture the printed output
    from io import StringIO
    import sys
    captured_output = StringIO()
    sys.stdout = captured_output
    # Use sample netCDF file for testing
    udata.print_latlon_info(xr_dataset='datafiles/sample_data/nox_2019_t106_US.nc')
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    # Check if the output contains expected strings
    expected_strings = [
        'For datafiles/sample_data/nox_2019_t106_US.nc: ',
	    'Latitude extent: 24.112 to 58.878',
	    'Longitude extent: -126.0 to -59.625',
	    'Latitude resolution: 1.121483870967742 ± 0.0004997397866077013',
        'Longitude resolution: 1.125'
    ]
    for expected in expected_strings:
        assert expected in output, f"Expected string '{expected}' not found in output"
    # Use sample lat lon arrays for testing
    captured_output = StringIO()
    sys.stdout = captured_output
    lats, lons = unox.load_lats_lons()
    udata.print_latlon_info(lats=lats, lons=lons)
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    # Check if the output contains expected strings
    expected_strings = [
        'For provided lat/lon arrays: ',
	    'Latitude extent: 11.776000022888184 to 73.45700073242188',
	    'Longitude extent: -174.375 to -40.5',
	    'Latitude resolution: 1.121472716331482 ± 0.0004995913477614522',
	    'Longitude resolution: 1.125',
    ]
    for expected in expected_strings:
        assert expected in output, f"Expected string '{expected}' not found in output"
    # Test with invalid inputs
    for invalid_input in invalid_datasets:
        try:
            udata.print_latlon_info(xr_dataset=invalid_input)
        except (TypeError, ValueError, FileNotFoundError) as e:
            assert True, f"print_latlon_info raised an exception on invalid input: {e}"
        else:
            assert False, f"print_latlon_info did not raise an exception on invalid input: {invalid_input}"

def test_verify_var():
    """Test the verify_var function."""
    # Create lists of valid variables for the sample data files
    valid_vars = [
        ['u10'],                # 'datafiles/sample_data/2019u10.nc'
        ['no2'],                # 'datafiles/sample_data/daily_42602_2019.csv'
        ['nox'],                # 'datafiles/sample_data/nox_2019_t106_US.nc'
        ['nox'],       # 'datafiles/sample_data/TROPESS_reanalysis_mon_emi_nox_anth_2021.nc'
    ]
    # Create list of invalid variables for testing
    invalid_vars = [
        'invalid_var', 
        1234, 
        True, 
        None,
    ]
    # Test each sample dataset
    for i in range(len(valid_vars)):
        datafile = sample_datafiles[i]
        var_list = valid_vars[i]
        # Load the dataset
        xr_dataset = udata.load_dataset(datafile)
        # Test valid variables
        for var in var_list:
            try:
                udata.verify_var(xr_dataset, var)
            except (ValueError, TypeError) as e:
                assert False, f"verify_var raised an exception on valid variable '{var}' in '{datafile}': {e}"
        # Test invalid variables
        for var in invalid_vars:
            try:
                udata.verify_var(xr_dataset, var)
            except (ValueError, TypeError) as e:
                assert True, f"verify_var raised an exception on invalid variable '{var}' in '{datafile}': {e}"
            else:
                assert False, f"verify_var did not raise an exception on invalid variable '{var}' in '{datafile}'"

def test_get_years():
    """Test the get_years function."""
    # Test with sample data files
    expected_years = [
        [2019],         # For 2019u10.nc
        [2019],         # For daily_42602_2019.csv
        [2019],         # For nox_2019_t106_US.nc
        [2021],         # For TROPESS_reanalysis_mon_emi_nox_anth_2021.nc
    ]
    for i, datafile in enumerate(sample_datafiles):
        xr_dataset = udata.load_dataset(datafile)
        actual_years = udata.get_years(xr_dataset)
        assert actual_years == expected_years[i], f"Expected years {expected_years[i]} do not match actual years {actual_years} for '{datafile}'"
    # Test with minimal xarray DataArray
    expected_years = [2019]
    actual_years = udata.get_years(minimal_xr0)
    assert actual_years == expected_years, f"Expected years {expected_years} do not match actual years {actual_years} for minimal example 0"
    expected_years = [2009]
    actual_years = udata.get_years(minimal_xr1)
    assert actual_years == expected_years, f"Expected years {expected_years} do not match actual years {actual_years} for minimal example 1"
    # Test with invalid inputs
    for invalid_input in invalid_datasets:
        try:
            udata.get_years(invalid_input)
        except (TypeError, ValueError) as e:
            assert True, f"get_years raised an exception on invalid input: {e}"
        else:
            assert False, f"get_years did not raise an exception on invalid input: {invalid_input}"

def test_clean_num_list():
    """Test the clean_num_list function."""
    # Test a valid list
    sample_list = [1.0, 2, 3, 4, '5', np.nan, None, 'abc', np.inf, -np.inf]
    expected_list = [1.0, 2, 3, 4]
    assert udata.clean_num_list(sample_list) == expected_list, f"clean_num_list failed on valid list {sample_list}"
    # Test an invalid list
    invalid_list = ['2', np.nan, None, 'abc', np.inf, -np.inf]
    try:
        udata.clean_num_list(invalid_list)
    except ValueError as e:
        assert True, f"clean_num_list raised an exception on invalid list {invalid_list}: {e}"
    else:
        assert False, f"clean_num_list did not raise an exception on invalid list {invalid_list}"

def test_verify_lat():
    """Test the verify_lat function."""
    # Test valid latitude values
    valid_lats = [0, 45, -45, 90, -90, 41.7]
    for lat in valid_lats:
        assert udata.verify_lat(lat) == lat, f"verify_lat failed on valid latitude {lat}"
    # Test invalid latitude values
    invalid_lats = [91, -91, 100, -100, np.nan, '45']
    for lat in invalid_lats:
        try:
            udata.verify_lat(lat)
        except ValueError as e:
            assert True, f"verify_lat raised an exception on invalid latitude {lat}: {e}"
        else:
            assert False, f"verify_lat did not raise an exception on invalid latitude {lat}"

def test_verify_lon():
    """Test the verify_lon function."""
    # Create test arrays of longitude values
    too_negative = [-181, -360, -400, -500, -1000, -180.1, -200.1, -360.1]
    negative = [-180, -179.9, -90, -45, -0.1, -0.0001]
    positive = [0.1, 0.0001, 45, 90, 179.9, 180]
    more_positive = [180.1, 180.0001, 225, 270, 359.9, 360]
    too_positive = [360.1, 361, 400, 500, 1000, ]
    # Test valid combinations of longitude values and PM_centered
    valid_lons = {
        None: [negative, positive, more_positive],
        True: [negative, positive],
        False: [positive, more_positive],
    }
    invalid_lons = {
        None: [too_negative, too_positive],
        True: [too_negative, more_positive, too_positive],
        False: [too_negative, negative, too_positive],
    }
    for test_PM_centered in [None, True, False]:
        for lons_arr in valid_lons[test_PM_centered]:
            for lon in lons_arr:
                assert udata.verify_lon(lon, PM_centered=test_PM_centered) == lon, f"verify_lon failed on valid longitude {lon} with PM_centered={test_PM_centered}"
        for lons_arr in invalid_lons[test_PM_centered]:
            for lon in lons_arr:
                try:
                    udata.verify_lon(lon, PM_centered=test_PM_centered)
                except ValueError as e:
                    assert True, f"verify_lon raised an exception on invalid longitude {lon} with PM_centered={test_PM_centered}: {e}"
                else:
                    assert False, f"verify_lon did not raise an exception on invalid longitude {lon} with PM_centered={test_PM_centered}"

def test_get_vminmax():
    """Test the get_vminmax function."""
    # Create a sample list of arrays for testing
    sample_array_list = [np.array([1, 2, 3]), np.array([4, 5, 6])]
    # Get the vmin and vmax values
    vmin, vmax = udata.get_vminmax(sample_array_list)
    # Check if the vmin and vmax values are correct
    assert vmin == 1.0, f"Expected vmin 1.0, but got {vmin}"
    assert vmax == 6.0, f"Expected vmax 6.0, but got {vmax}"

    # Create another sample list of arrays for testing
    sample_array_list_2 = [np.array([np.nan, -2, 3]), np.array([4, 5, np.nan])]
    # Get the vmin and vmax values
    vmin, vmax = udata.get_vminmax(sample_array_list_2)
    # Check if the vmin and vmax values are correct
    assert vmin == -2.0, f"Expected vmin -2.0, but got {vmin}"
    assert vmax == 5.0, f"Expected vmax 5.0, but got {vmax}"

    # Create an invalid sample list of arrays for testing
    invalid_array_list = [np.array([np.nan, np.nan, np.nan]), np.array([np.nan, np.nan, np.nan])]
    # Get the vmin and vmax values
    try:
        udata.get_vminmax(invalid_array_list)
    except ValueError as e:
        assert True, f"get_vminmax raised an exception on invalid input: {e}"
    else:
        assert False, "get_vminmax did not raise an exception on invalid input"
    
    # Create a sample xarray dataset for testing
    xr_dataset=xr.open_dataset('datafiles/sample_data/nox_2019_t106_US.nc')
    ex_lat_min = 24.112
    ex_lat_max = 58.878
    ex_lon_min = -126.0
    ex_lon_max = -59.625
    # Get the vmin and vmax values of the lat and lon coordinates
    lats, lons = udata.get_lats_lons(xr_dataset)
    lon_min, lon_max = udata.get_vminmax(lons)
    lat_min, lat_max = udata.get_vminmax(lats)
    # Check if the vmin and vmax values are correct
    assert lat_min == ex_lat_min, f"Expected lat_min {ex_lat_min}, but got {lat_min}"
    assert lat_max == ex_lat_max, f"Expected lat_max {ex_lat_max}, but got {lat_max}"
    assert lon_min == ex_lon_min, f"Expected lon_min {ex_lon_min}, but got {lon_min}"
    assert lon_max == ex_lon_max, f"Expected lon_max {ex_lon_max}, but got {lon_max}"

def test_get_max_abs_val():
    """Test the get_max_abs_val function."""
    # Create sample data array for testing
    sample_values = [1, -2, 3, -4, 5, -6]
    # Get the max absolute value
    max_abs_val = udata.get_max_abs_val(sample_values)
    # Check if the max absolute value is correct
    assert max_abs_val == 6.0, f"Expected max absolute value 6.0, but got {max_abs_val}"

    # Create sample data array for testing
    sample_values = np.arange(1, 7)
    # Get the max absolute value
    max_abs_val = udata.get_max_abs_val(sample_values)
    # Check if the max absolute value is correct
    assert max_abs_val == 6.0, f"Expected max absolute value 6.0, but got {max_abs_val}"
    
    # Create another sample data array for testing
    sample_values_2 = [-1, '-2', 3, -4, np.nan, -6]
    # Get the max absolute value
    max_abs_val = udata.get_max_abs_val(sample_values_2)
    # Check if the max absolute value is correct
    assert max_abs_val == 6.0, f"Expected max absolute value 6.0, but got {max_abs_val}"
    
    # Create an invalid sample data array for testing
    invalid_values = [np.nan, None, '1']
    # Get the max absolute value
    try:
        udata.get_max_abs_val(invalid_values)
    except ValueError as e:
        assert True, f"get_max_abs_val raised an exception on invalid input: {e}"
    else:
        assert False, f"get_max_abs_val did not raise an exception on invalid input: {invalid_values}"

@pytest.mark.filterwarnings("ignore:loadtxt", "ignore:genfromtxt")
def test_verify_npy():
    """Test the verify_npy function."""
    
    # Create sample numpy array for testing
    my_array = np.array([1, 2, 3])
    verify_npy = udata.verify_npy(my_array)
    assert np.array_equal(verify_npy, my_array) == True, f"Expected {my_array}, but got {verify_npy}"

    # Create non-array varaible for testing
    not_array = 5
    try:
        verify_npy = udata.verify_npy(not_array)
    except TypeError as e:
        assert True, f"verify_npy raised an exception on invalid input: {e}"
    else:
        assert False, f"verify_npy did not raise an exception on invalid input: {not_array}"

    # Test invalid .npy file
    # Ensure sample file structure exists. If not create it.
    os.makedirs("tests/arrays", exist_ok=True)
    path = "tests/arrays/array1.npy"
    # Attempt to open file and write nothing to it. If it does not exist a new empty file will be created.
    with open(path, "w") as file:
        file.write("")
    try:
        verify_npy = udata.verify_npy(path)
    except ValueError:
        pass

    # Test valid .npy file
    np.save(path, my_array)
    verify_npy = udata.verify_npy(path)
    assert np.array_equal(verify_npy, my_array) == True, f"Expected True, but got {verify_npy}"

    # Test non-.npy file containing invalid npy array
    # Ensure non-npy file exists. If not create it.
    path = "tests/arrays/array1.txt"
    with open(path, "w") as file:
        file.write("")
    try:
        verify_npy = udata.verify_npy(path)
    except ValueError as e:
        assert True, f"verify_npy raised an exception on invalid input: {e}"
    else:
        assert False, f"verify_npy did not raise an exception on invalid input: {path}"

    # Test non-.npy file containing valid npy array
    np.savetxt(path, my_array, fmt="%d")
    verify_npy = udata.verify_npy(path)
    assert np.array_equal(verify_npy, my_array) == True, f"Expected True, but got {verify_npy}"

    # Test if non-existant files raise an Error.
    path = "tests/arrays/array2.npy"
    try:
        verify_npy = udata.verify_npy(path)
    except FileNotFoundError as e:
        assert True, f"verify_npy raised an exception on invalid input: {e}"
    else:
        assert False, f"verify_npy did not raise an exception on invalid input: {path}"

    # Test if folder paths raise an Error
    path = "tests/arrays"
    try:
        verify_npy = udata.verify_npy(path)
    except FileNotFoundError as e:
        assert True, f"verify_npy raised an exception on invalid input: {e}"
    else:
        assert False, f"verify_npy did not raise an exception on invalid input: {path}"
    
    # Clean up the test directory
    if os.path.exists("tests/arrays"):
        for file in os.listdir("tests/arrays"):
            file_path = os.path.join("tests/arrays", file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir("tests/arrays")

def test_get_num_from_string():
    """Test the get_num_from_string function."""
    
    # Test valid strings
    valid_string = 'The air will be -5.5 degrees this morning and rise by 10 this afternoon. It will then drop by 3.2 degrees in the evening.'
    expected_numbers = [-5.5, 10, 3.2]
    actual_numbers = udata.get_num_from_string(valid_string)
    assert actual_numbers == expected_numbers, f"Expected {expected_numbers}, but got {actual_numbers}"
    # Test invalid strings
    invalid_string = 'The air will be cold this morning and warm up this afternoon. It will then drop slightly in the evening.'
    actual_numbers = udata.get_num_from_string(invalid_string)
    assert actual_numbers == [], f"Expected [], but got {actual_numbers}"
    # Test invalid input
    invalid_input = 12345
    try:
        udata.get_num_from_string(invalid_input)
    except TypeError as e:
        assert True, f"get_num_from_string raised an exception on invalid input: {e}"
    else:
        assert False, f"get_num_from_string did not raise an exception on invalid input: {invalid_input}"

def test_get_DOY():
    """Test the get_DOY function."""
    # Test valid inputs
    valid_dates_and_expected = [
        (np.datetime64('1999-12-30'), 364),
        ('2004-02-29', 60),
        ('2021-01-01', 1),
        ('2020-12-31', 366),  # Leap year
        (np.datetime64('1984-02-29T05:39:10'), 60),  # Leap year with time
        ('2016-07-04T12:07:03', 186),  # Regular year with time
    ]
    for this_date, expected_doy in valid_dates_and_expected:
        actual_doy = udata.get_DOY(this_date)
        assert actual_doy == expected_doy, f"Expected {expected_doy}, but got {actual_doy}"
    
    # Test invalid inputs
    invalid_dates = [
        'not_a_date',
        1999,
        35.6
    ]
    for invalid_date in invalid_dates:
        try:
            udata.get_DOY(invalid_date)
        except (ValueError, TypeError) as e:
            assert True, f"get_DOY raised an exception on invalid input: {e}"
        else:
            assert False, f"get_DOY did not raise an exception on invalid input: {invalid_date}"

def test_increment_month():
    """Test the increment_month function."""
    
    # Test valid inputs
    this_month = 7
    expected_tuple = (8, False)
    actual_month = udata.increment_month(this_month, 1)
    assert actual_month == expected_tuple, f"Expected {expected_tuple}, but got {actual_month}"
    this_month = 11
    expected_tuple = (2, True)
    actual_month = udata.increment_month(this_month, 3)
    assert actual_month == expected_tuple, f"Expected {expected_tuple}, but got {actual_month}"
    this_month = '12'
    expected_tuple = ('1', True)
    actual_month = udata.increment_month(this_month, '1')
    assert actual_month == expected_tuple, f"Expected {expected_tuple}, but got {actual_month}"
    # Test invalid inputs
    invalid_month = 13
    try:
        udata.increment_month(invalid_month, 1)
    except ValueError as e:
        assert True, f"increment_month raised an exception on invalid input: {e}"
    else:
        assert False, f"increment_month did not raise an exception on invalid input: {invalid_month}"
    invalid_month = 'abc'
    try:
        udata.increment_month(invalid_month, 1)
    except TypeError as e:
        assert True, f"increment_month raised an exception on invalid input: {e}"
    else:
        assert False, f"increment_month did not raise an exception on invalid input: {invalid_month}"
    invalid_increment = 'xyz'
    try:
        udata.increment_month(5, invalid_increment)
    except TypeError as e:
        assert True, f"increment_month raised an exception on invalid increment: {e}"
    else:
        assert False, f"increment_month did not raise an exception on invalid increment: {invalid_increment}"

def test_get_YMD_from_date():
    """Test the get_YMD_from_date function."""
    
    # Test valid inputs
    this_date = np.datetime64('1999-12-30')
    expected_tuple = (1999, 12, 30)
    actual_date = udata.get_YMD_from_date(this_date)
    assert actual_date == expected_tuple, f"Expected {expected_tuple}, but got {actual_date}"
    
    this_date = '2004-02-29'
    expected_tuple = (2004, 2, 29)
    actual_date = udata.get_YMD_from_date(this_date)
    assert actual_date == expected_tuple, f"Expected {expected_tuple}, but got {actual_date}"
    
    this_date = '2021-01-01'
    expected_tuple = (2021, 1, 1)
    actual_date = udata.get_YMD_from_date(this_date)
    assert actual_date == expected_tuple, f"Expected {expected_tuple}, but got {actual_date}"
    
    # Test invalid inputs
    invalid_date = 'not_a_date'
    try:
        udata.get_YMD_from_date(invalid_date)
    except ValueError as e:
        assert True, f"get_YMD_from_date raised an exception on invalid input: {e}"
    else:
        assert False, f"get_YMD_from_date did not raise an exception on invalid input: {invalid_date}"
    invalid_date = 1999
    try:
        udata.get_YMD_from_date(invalid_date)
    except TypeError as e:
        assert True, f"get_YMD_from_date raised an exception on invalid input: {e}"
    else:
        assert False, f"get_YMD_from_date did not raise an exception on invalid input: {invalid_date}"

def test_get_increment_info():
    """Test the get_increment_info function."""
    
    # Test valid inputs
    this_increment = np.timedelta64(2, 'D')  # 2 days
    expected_tuple = (2, 'D')
    actual_increment = udata.get_increment_info(this_increment)
    assert actual_increment == expected_tuple, f"Expected {expected_tuple}, but got {actual_increment}"
    
    this_increment = '3M'  # 3 months
    expected_tuple = (3, 'M')
    actual_increment = udata.get_increment_info(this_increment)
    assert actual_increment == expected_tuple, f"Expected {expected_tuple}, but got {actual_increment}"
    
    this_increment = '4Y'  # 4 years
    expected_tuple = (4, 'Y')
    actual_increment = udata.get_increment_info(this_increment)
    assert actual_increment == expected_tuple, f"Expected {expected_tuple}, but got {actual_increment}"
    
    # Test invalid inputs
    invalid_increment = 'not_a_timedelta'
    try:
        udata.get_increment_info(invalid_increment)
    except ValueError as e:
        assert True, f"get_increment_info raised an exception on invalid input: {e}"
    else:
        assert False, f"get_increment_info did not raise an exception on invalid input: {invalid_increment}"
    
    invalid_increment = 12345
    try:
        udata.get_increment_info(invalid_increment)
    except TypeError as e:
        assert True, f"get_increment_info raised an exception on invalid input: {e}"
    else:
        assert False, f"get_increment_info did not raise an exception on invalid input: {invalid_increment}"

def test_add_amount_to_date():
    """Test the add_amount_to_date function."""
    # Test valid inputs
    date_increment_expected = [
        (np.datetime64('1999-12-30'), np.timedelta64(2, 'D'), np.datetime64('2000-01-01')),
        ('1999-12-30', '3D', '2000-01-02'),
        (np.datetime64('2004-02-28'), np.timedelta64(4, 'D'), np.datetime64('2004-03-03')),
        ('2004-02-28', '5D', '2004-03-04'),
        (np.datetime64('2004-02-20'), np.timedelta64(6, 'M'), np.datetime64('2004-08-20')),
        ('2004-07-20', '7M', '2005-02-20'),
        (np.datetime64('2004-01-31'), np.timedelta64(8, 'Y'), np.datetime64('2012-01-31')),
        ('2004-01-31', '9Y', '2013-01-31')
    ]
    for this_date, add_this, expected_date in date_increment_expected:
        actual_date = udata.add_amount_to_date(this_date, add_this)
        assert actual_date == expected_date, f"Expected {expected_date}, but got {actual_date}"
    # Test valid inputs with keep_within_year=True
    date_increment_expected = [
        (np.datetime64('1999-12-30'), np.timedelta64(2, 'D'), np.datetime64('1999-12-31')),
        ('1999-12-30', '3D', '1999-12-31'),
        (np.datetime64('2004-02-28'), np.timedelta64(4, 'D'), np.datetime64('2004-03-03')),
        ('2004-02-28', '5D', '2004-03-04'),
        (np.datetime64('2004-02-20'), np.timedelta64(6, 'M'), np.datetime64('2004-08-20')),
        ('2004-07-20', '7M', '2004-12-31'),
        (np.datetime64('2004-01-31'), np.timedelta64(8, 'Y'), np.datetime64('2004-12-31')),
        ('2004-01-31', '9Y', '2004-12-31')
    ]
    for this_date, add_this, expected_date in date_increment_expected:
        actual_date = udata.add_amount_to_date(this_date, add_this, keep_within_year=True)
        assert actual_date == expected_date, f"Expected {expected_date}, but got {actual_date}"
    # Test invalid inputs
    invalid_date_increment = [
        ('not_a_date', np.timedelta64(2, 'D')),
        (1999, np.timedelta64(2, 'D')),
        (np.datetime64('1999-12-30'), 'not_a_timedelta'),
        (np.datetime64('1999-12-30'), 12345)
    ]
    for this_date, add_this in invalid_date_increment:
        try:
            udata.add_amount_to_date(this_date, add_this)
        except (ValueError, TypeError) as e:
            assert True, f"add_amount_to_date raised an exception on invalid input: {e}"
        else:
            assert False, f"add_amount_to_date did not raise an exception on invalid input: {this_date}, {add_this}"
