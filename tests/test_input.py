from unox import input as uin
import unox.unox as unox
import numpy as np
import xarray as xr
import pandas as pd
import os
import json

from unox.HPC.data0.paths import verify_path, remove_non_empty_directory
from unox.HPC.data0.dataset import uarray

# Create an example xarray Dataset for testing
# Include dimensions of time, lat, lon, and some example variables
n_lat = 10
n_lon = 20
n_start = '2020-01-01'
n_end = '2020-01-30'
time_arr = pd.date_range(start=n_start, end=n_end, freq='D')
n_time = len(time_arr)
example_xr = xr.Dataset(
    {
        'nox': (('time', 'lat', 'lon'), np.random.rand(n_time, n_lat, n_lon)),
        'u10': (('time', 'lat', 'lon'), np.random.rand(n_time, n_lat, n_lon)),
    },
    coords={
        'time': time_arr,
        'lat': np.linspace(-90, 90, n_lat),
        'lon': np.linspace(-180, 180, n_lon),
    }
)
# Create a second example xarray Dataset for test_make_input_metadata_file
n_lat2 = 2
n_lon2 = 4
n_start2 = '2005-01-01'
n_end2 = '2020-12-31'
time_arr2 = pd.date_range(start=n_start2, end=n_end2, freq='M')
n_time2 = len(time_arr2)
example_xr2 = xr.Dataset(
    {
        'no2': (('time', 'lat', 'lon'), np.random.rand(n_time2, n_lat2, n_lon2)),
        'no2_s2': (('time', 'lat', 'lon'), np.random.rand(n_time2, n_lat2, n_lon2)),
        'no2_tm1': (('time', 'lat', 'lon'), np.random.rand(n_time2, n_lat2, n_lon2)),
        'no2_s2_tm1': (('time', 'lat', 'lon'), np.random.rand(n_time2, n_lat2, n_lon2)),
        'u10': (('time', 'lat', 'lon'), np.random.rand(n_time2, n_lat2, n_lon2)),
        'v10': (('time', 'lat', 'lon'), np.random.rand(n_time2, n_lat2, n_lon2)),
        'blh': (('time', 'lat', 'lon'), np.random.rand(n_time2, n_lat2, n_lon2)),
        'sp': (('time', 'lat', 'lon'), np.random.rand(n_time2, n_lat2, n_lon2)),
        'skt': (('time', 'lat', 'lon'), np.random.rand(n_time2, n_lat2, n_lon2)),
        't2m': (('time', 'lat', 'lon'), np.random.rand(n_time2, n_lat2, n_lon2)),
        'ssrd': (('time', 'lat', 'lon'), np.random.rand(n_time2, n_lat2, n_lon2)),
        'lsm': (('time', 'lat', 'lon'), np.random.rand(n_time2, n_lat2, n_lon2)),
    },
    coords={
        'time': time_arr2,
        'lat': np.linspace(-90, 90, n_lat2),
        'lon': np.linspace(-180, 180, n_lon2),
    }
)

def test_x_or_y_var():
    """Test the x_or_y_var function."""
    # Make lists of valid inputs
    valid_x_vars = []
    valid_y_vars = []
    for key in uin.input_vars_dict.keys():
        valid_x_vars += uin.input_vars_dict[key]['x_vars']
        valid_y_vars += uin.input_vars_dict[key]['y_vars']
    # Test valid x variables
    for var in valid_x_vars:
        assert uin.x_or_y_var(var) == 'x', f"x_or_y_var did not return 'x' for valid x variable '{var}'"
    # Test valid y variables
    for var in valid_y_vars:
        assert uin.x_or_y_var(var) == 'y', f"x_or_y_var did not return 'y' for valid y variable '{var}'"
    # Make lists of invalid inputs
    invalid_vars = [None, '', 'not_a_var', 123, True, False, [], {}]
    # Test invalid variables
    for var in invalid_vars:
        try:
            uin.x_or_y_var(var)
        except (TypeError, ValueError) as e:
            assert True, f"x_or_y_var raised an exception on invalid input '{var}': {e}"
        else:
            assert False, f"x_or_y_var did not raise an exception on invalid input '{var}'"

def test_get_input_index():
    """Test the get_input_index function."""
    # Loop across the keys in the input variable dictionary
    for key in uin.input_vars_dict.keys():
        valid_x_vars = uin.input_vars_dict[key]['x_vars']
        valid_y_vars = uin.input_vars_dict[key]['y_vars']
        # Test valid x variables
        for i in range(len(valid_x_vars)):
            var = valid_x_vars[i]
            index = uin.get_input_index(var)
            assert index == i, f"get_input_index returned {index} instead of {i} for valid x variable '{var}'"
        # Test valid y variables
        for i in range(len(valid_y_vars)):
            var = valid_y_vars[i]
            index = uin.get_input_index(var)
            assert index == i, f"get_input_index returned {index} instead of {i} for valid y variable '{var}'"
    # Make lists of invalid inputs
    invalid_vars = [None, '', 'not_a_var', 123, True, False, [], {}]
    # Test invalid variables
    for var in invalid_vars:
        try:
            uin.get_input_index(var)
        except (TypeError, ValueError) as e:
            assert True, f"get_input_index raised an exception on invalid input '{var}': {e}"
        else:
            assert False, f"get_input_index did not raise an exception on invalid input '{var}'"

def test_make_y_input_file():
    """Test the make_y_input_file function."""
    # Set the arguments for a test run
    datadir='/data/high_res/emacdonald/unet/datafiles/t106'
    verifydir='inputfiles/no2_input_test1/'
    this_year=2019
    # Assemble file path to verification array
    verify_filepath = f"{verifydir}stage1/y/Y_{this_year}.npy"
    # Verify that file path
    verify_filepath = verify_path(verify_filepath)
    # Load the verification array
    verify_array = np.load(verify_filepath)
    # Call the function to create the y input file
    y_data = uin.make_y_input_file(
        year=this_year, 
        var='nox',
        emiss_dir=datadir,
        emiss_pre='nox_',
        emiss_post='_t106_US.nc',
        scale_factor=1e12,
        nan_fill=0,
        stage_2_cutoff=2022,
        output_dir=None
    )
    # Verify that the output is a numpy array
    assert isinstance(y_data, np.ndarray), "make_y_input_file did not return a numpy array."
    # Verify that the shape of the output matches the verification array
    assert y_data.shape == verify_array.shape, f"make_y_input_file output shape {y_data.shape} does not match verification array shape {verify_array.shape}"
    # Verify that the output matches the verification array
    assert np.array_equal(y_data, verify_array), f"make_y_input_file output does not match array from {verify_filepath}"

def test_set_global_attrs():
    """Test the set_global_attrs function."""
    # Define global attributes
    g_attrs = {
        'title': 'Test Dataset',
        'institution': 'Test Institution',
    }
    # Call the function to set global attributes
    actual = uin.set_global_attrs(example_xr, g_attrs)
    # Get the time stamp
    modification_date = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    # Verify that the output is an xarray Dataset
    assert isinstance(actual, xr.Dataset), "set_global_attrs did not return an xarray Dataset."
    # Verify that the global attributes were set correctly
    for attr, value in g_attrs.items():
        assert actual.attrs.get(attr) == value, f"set_global_attrs did not set attribute '{attr}' correctly."
    # Verify that the modification_date is within a minute
    actual_mod_date = pd.to_datetime(actual.attrs.get('modification_date'))
    expected_mod_date = pd.to_datetime(modification_date)
    time_diff = abs((actual_mod_date - expected_mod_date).total_seconds())
    assert time_diff < 60, f"set_global_attrs did not set modification_date correctly. Expected {modification_date}, got {actual.attrs.get('modification_date')}"

    # Create a copy of the example dataset to avoid modifying the original
    actual = example_xr.copy()
    # Test invalid inputs
    invalid_inputs = [None, 'not_a_dataset', 123, True, False, []]
    for invalid in invalid_inputs:
        try:
            uin.set_global_attrs(invalid, g_attrs)
        except (TypeError, ValueError) as e:
            assert True, f"set_global_attrs raised an exception on invalid dataset input '{invalid}': {e}"
        else:
            assert False, f"set_global_attrs did not raise an exception on invalid dataset input '{invalid}'"
        try:
            uin.set_global_attrs(actual, invalid)
        except (TypeError, ValueError) as e:
            assert True, f"set_global_attrs raised an exception on invalid g_attrs input '{invalid}': {e}"
        else:
            assert False, f"set_global_attrs did not raise an exception on invalid g_attrs input '{invalid}'"

def test_set_var_attrs():
    """Test the set_var_attrs function."""
    # Define variable attributes
    var_attrs = {
        'nox': {
            'long_name': 'Surface NOx emissions',
            'units': 'kgN/m2/s',
        },
        'u10': {
            'long_name': '10m U Wind',
            'units': 'm/s',
        },
    }
    # Create a copy of the example dataset to avoid modifying the original
    actual = example_xr.copy()
    # Call the function to set variable attributes
    for var in var_attrs.keys():
        if var not in actual.data_vars:
            raise ValueError(f"Variable '{var}' not found in actual Dataset.")
        if not isinstance(var_attrs[var], dict):
            raise TypeError(f"Attributes for variable '{var}' must be a dictionary.")
        actual = uin.set_var_attrs(actual, var, var_attrs[var])
    # Verify that the output is an xarray Dataset
    assert isinstance(actual, xr.Dataset), "set_var_attrs did not return an xarray Dataset."
    # Verify that the variable attributes were set correctly
    for var, attrs in var_attrs.items():
        for attr, value in attrs.items():
            actual_attr = actual[var].attrs.get(attr)
            assert actual_attr == value, f"set_var_attrs did not set attribute '{attr}' for variable '{var}' correctly. Expected {value}, got {actual_attr}"

    # Create a copy of the example dataset to avoid modifying the original
    actual = example_xr.copy()
    # Test invalid inputs
    invalid_inputs = [None, 'not_a_dataset', 123, True, False, []]
    for invalid in invalid_inputs:
        try:
            uin.set_var_attrs(invalid, var_attrs)
        except (TypeError, ValueError) as e:
            assert True, f"set_var_attrs raised an exception on invalid dataset input '{invalid}': {e}"
        else:
            assert False, f"set_var_attrs did not raise an exception on invalid dataset input '{invalid}'"
        try:
            uin.set_var_attrs(actual, invalid)
        except (TypeError, ValueError) as e:
            assert True, f"set_var_attrs raised an exception on invalid var_attrs input '{invalid}': {e}"
        else:
            assert False, f"set_var_attrs did not raise an exception on invalid var_attrs input '{invalid}'"

def test_scale_xr_var():
    """Test the scale_xr_var function."""
    # Create a copy of the example dataset to avoid modifying the original
    actual = example_xr.copy()
    # Define scale factors
    scale_factors = {
        'nox': 1e12,
        'u10': 1,
    }
    # Call the function to scale variables
    for var, factor in scale_factors.items():
        if var not in actual.data_vars:
            raise ValueError(f"Variable '{var}' not found in actual Dataset.")
        if not isinstance(factor, (int, float)):
            raise TypeError(f"Scale factor for variable '{var}' must be a number.")
        actual = uin.scale_xr_var(actual, var, factor)
    # Verify that the output is an xarray Dataset
    assert isinstance(actual, xr.Dataset), "scale_xr_var did not return an xarray Dataset."
    # Verify that the variables were scaled correctly
    for var, factor in scale_factors.items():
        expected = example_xr[var] * factor
        actual_data = actual[var].data
        assert np.array_equal(actual_data, expected.data), f"scale_xr_var did not scale variable '{var}' correctly."

    # Create a copy of the example dataset to avoid modifying the original
    actual = example_xr.copy()
    # Test invalid inputs
    invalid_inputs = [None, 'not_a_dataset', 123, True, False, []]
    for invalid in invalid_inputs:
        try:
            uin.scale_xr_var(invalid, 'nox', 1e12)
        except (TypeError, ValueError) as e:
            assert True, f"scale_xr_var raised an exception on invalid dataset input '{invalid}': {e}"
        else:
            assert False, f"scale_xr_var did not raise an exception on invalid dataset input '{invalid}'"
        try:
            uin.scale_xr_var(actual, invalid, 1e12)
        except (TypeError, ValueError) as e:
            assert True, f"scale_xr_var raised an exception on invalid var input '{invalid}': {e}"
        else:
            assert False, f"scale_xr_var did not raise an exception on invalid var input '{invalid}'"
        try:
            uin.scale_xr_var(actual, 'nox', invalid)
        except (TypeError, ValueError) as e:
            assert True

def test_make_x_input_file():
    """Test the make_x_input_file function."""
    # Set the arguments for a test run
    datadir='/data/high_res/emacdonald/unet/datafiles/'
    verifydir='inputfiles/no2_input_test1/'
    this_year=2019
    for this_stage in [1, 2]:
        # Assemble file path to verification array
        verify_filepath = f"{verifydir}stage{this_stage}/x/X_{this_year}.npy"
        # Verify that file path
        verify_filepath = verify_path(verify_filepath)
        # Load the verification array
        verify_array = np.load(verify_filepath)
        # Call the function to create the x input file
        x_data = uin.make_x_input_file(
            year=this_year, 
            stage=this_stage,
            data_dir=datadir,
            chemra_path='TROPESS/TROPESS_reanalysis_2hr_no2_sfc_',
            insitu_path='US_EPA/daily_42602_',
            era5_path='ERA5concatenated/',
            scale_factors={
                'chemra': 1000,
                'sp': 100000,
                'ssrd': 1000000,
                'blh': 1000},
            output_dir=None
        )
        # Verify that the output is a numpy array
        assert isinstance(x_data, np.ndarray), "make_x_input_file did not return a numpy array."
        # Verify that the shape of the output matches the verification array
        assert x_data.shape == verify_array.shape, f"make_x_input_file output shape {x_data.shape} does not match verification array shape {verify_array.shape}"
        # Verify that the output matches the verification array
        assert np.array_equal(x_data, verify_array), f"make_x_input_file output does not match array from {verify_filepath}"

def test_make_input_metadata_file():
    """Test the make_input_metadata_file function."""
    # Load the verification metadata
    verify_file = 'tests/data_for_tests/input_metadata.json'
    with open(verify_file, 'r') as f:
        verify_dict = json.load(f)
    # Get the x variables from the example xarray Dataset
    x_var_list = list(example_xr2.data_vars.keys())
    # Remove `lsm` from the variable list
    x_var_list.remove('lsm')
    # Make the attribute dictionaries
    g_attrs = {
        'x_vars': x_var_list,
        'y_var': 'nox',
        'emiss_dir': '/data/high_res/emacdonald/unet/datafiles/t106',
        'emiss_pre': 'nox_',
        'emiss_post': '_t106_US.nc',
        'nan_fill': 0,
        'stage_2_cutoff': 2013,
        'lsm': 'True',
        'data_dir': '/data/high_res',
        'chemra_path': 'emacdonald/unet/datafiles/TROPESS/TROPESS_reanalysis_2hr_no2_sfc_',
        'insitu_path': 'US_EPA/NO2/daily_NO2/daily_42602_',
        'era5_path': 'ERA5concatenated',
        'stages': [1, 2],
    }
    # Create metadata file
    meta_dict = uin.make_input_metadata_file(
        example_xr2,
        output_dir=None,
        g_attrs=g_attrs,
    )
    # Verify that the created metadata matches the verification metadata
    assert meta_dict == verify_dict, "`make_input_metadata_file` output does not match verification metadata."
    
    # Test invalid inputs
    for invalid_xr in [None, '2019', True, 1, 1.0, [], {}]:
        try:
            uin.make_input_metadata_file(
                invalid_xr,
                output_dir=None,
                g_attrs=g_attrs,
            )
        except (TypeError, FileNotFoundError) as e:
            assert True, f"`make_input_metadata_file` raised an exception on invalid xarray {invalid_xr}: {e}"
        else:
            assert False, f"`make_input_metadata_file` did not raise an exception on invalid xarray {invalid_xr}"
    for invalid_output_dir in [True, 1, 1.0, [], {}]:
        try:
            uin.make_input_metadata_file(
                example_xr2,
                output_dir=invalid_output_dir,
                g_attrs=g_attrs,
            )
        except TypeError as e:
            assert True, f"`make_input_metadata_file` raised an exception on invalid output directory {invalid_output_dir}: {e}"
        else:
            assert False, f"`make_input_metadata_file` did not raise an exception on invalid output directory {invalid_output_dir}"
    for invalid_g_attr in ['2019', True, 1, 1.0, []]:
        try:
            uin.make_input_metadata_file(
                example_xr2,
                output_dir=None,
                g_attrs=invalid_g_attr,
            )
        except TypeError as e:
            assert True, f"`make_input_metadata_file` raised an exception on invalid global attribute dictionary {invalid_g_attr}: {e}"
        else:
            assert False, f"`make_input_metadata_file` did not raise an exception on invalid global attribute dictionary {invalid_g_attr}"

def test_make_input_config():
    """Test the make_input_config function."""
    # Test with valid parameters
    actual = uin.make_input_config(
        'test_make_input_config',
        input_set='no2_lsm6',
        grid_size=[30,40],
        x_vars=[
            'no2',
            'no2_tm1',
            'u10',
            'v10',
            'blh',
            'sp',
            'skt',
            't2m',
            'ssrd'
        ],
        stage_2=True,
        stage_2_cutoff=2013,
        lsm_vars=[
            'no2',
            'no2_tm1'
        ],
        zfi_vars=[
            't2m',
        ],
    )
    expected = {
        "input_set": "no2_lsm6",
        "grid_size": [30, 40],
        "x_vars": [
            "no2",
            "no2_tm1",
            "u10",
            "v10",
            "blh",
            "sp",
            "skt",
            "t2m",
            "ssrd"
        ],
        "stage_2": True,
        "stage_2_cutoff": 2013,
        "lsm_vars": [
            "no2",
            "no2_tm1"
        ],
        "zfi_vars": [
            "t2m"
        ]
    }
    assert actual == expected, "make_input_config did not return the expected configuration dictionary."
    # Clean up generated json file
    if os.path.exists('inputfiles/_input_configs/test_make_input_config.json'):
        os.remove('inputfiles/_input_configs/test_make_input_config.json')
    # Test with invalid inputs for config name
    for invalid_input in [None, 123, True, [], {}]:
        try:
            uin.make_input_config(
                invalid_input,
                input_set=expected['input_set'],
                grid_size=expected['grid_size'],
                x_vars=expected['x_vars'],
                stage_2=expected['stage_2'],
                stage_2_cutoff=expected['stage_2_cutoff'],
                lsm_vars=expected['lsm_vars'],
                zfi_vars=expected['zfi_vars'],
            )
        except TypeError as e:
            assert True, f"make_input_config raised an exception on invalid config_name {invalid_input}: {e}"
        else:
            assert False, f"make_input_config did not raise an exception on invalid config_name {invalid_input}"
    # Test with invalid inputs for input_set
    for invalid_input in [None, '', 123, True, [], {}]:
        try:
            uin.make_input_config(
                'test_make_input_config',
                input_set=invalid_input,
                grid_size=expected['grid_size'],
                x_vars=expected['x_vars'],
                stage_2=expected['stage_2'],
                stage_2_cutoff=expected['stage_2_cutoff'],
                lsm_vars=expected['lsm_vars'],
                zfi_vars=expected['zfi_vars'],
            )
        except (TypeError, ValueError) as e:
            assert True, f"make_input_config raised an exception on invalid input_set {invalid_input}: {e}"
        else:
            assert False, f"make_input_config did not raise an exception on invalid input_set {invalid_input}"
    # Test with invalid inputs for grid_size
    for invalid_input in [None, 'not_a_list', 123, True, {}, ['invalid_x_var'], [10000, 10000]]:
        try:
            uin.make_input_config(
                'test_make_input_config',
                input_set=expected['input_set'],
                grid_size=invalid_input,
                x_vars=expected['x_vars'],
                stage_2=expected['stage_2'],
                stage_2_cutoff=expected['stage_2_cutoff'],
                lsm_vars=expected['lsm_vars'],
                zfi_vars=expected['zfi_vars'],
            )
        except (TypeError, ValueError) as e:
            assert True, f"make_input_config raised an exception on invalid x_vars {invalid_input}: {e}"
        else:
            assert False, f"make_input_config did not raise an exception on invalid x_vars {invalid_input}"
    # Test with invalid inputs for x_vars
    for invalid_input in [None, 'not_a_list', 123, True, {}, ['invalid_x_var']]:
        try:
            uin.make_input_config(
                'test_make_input_config',
                input_set=expected['input_set'],
                grid_size=expected['grid_size'],
                x_vars=invalid_input,
                stage_2=expected['stage_2'],
                stage_2_cutoff=expected['stage_2_cutoff'],
                lsm_vars=expected['lsm_vars'],
                zfi_vars=expected['zfi_vars'],
            )
        except (TypeError, ValueError) as e:
            assert True, f"make_input_config raised an exception on invalid x_vars {invalid_input}: {e}"
        else:
            assert False, f"make_input_config did not raise an exception on invalid x_vars {invalid_input}"
    # Test with invalid inputs for stage_2
    for invalid_input in [None, 'not_a_bool', 123, [], {}]:
        try:
            uin.make_input_config(
                'test_make_input_config',
                input_set=expected['input_set'],
                grid_size=expected['grid_size'],
                x_vars=expected['x_vars'],
                stage_2=invalid_input,
                stage_2_cutoff=expected['stage_2_cutoff'],
                lsm_vars=expected['lsm_vars'],
                zfi_vars=expected['zfi_vars'],
            )
        except TypeError as e:
            assert True, f"make_input_config raised an exception on invalid stage_2 {invalid_input}: {e}"
        else:
            assert False, f"make_input_config did not raise an exception on invalid stage_2 {invalid_input}"
    # Test with invalid inputs for stage_2_cutoff
    for invalid_input in [None, 'not_an_int', True, [], {}, 1800, 123]:
        try:
            uin.make_input_config(
                'test_make_input_config',
                input_set=expected['input_set'],
                grid_size=expected['grid_size'],
                x_vars=expected['x_vars'],
                stage_2=expected['stage_2'],
                stage_2_cutoff=invalid_input,
                lsm_vars=expected['lsm_vars'],
                zfi_vars=expected['zfi_vars'],
            )
        except (TypeError, ValueError) as e:
            assert True, f"make_input_config raised an exception on invalid stage_2_cutoff {invalid_input}: {e}"
        else:
            assert False, f"make_input_config did not raise an exception on invalid stage_2_cutoff {invalid_input}"
    # Test with invalid inputs for lsm_vars
    for invalid_input in [None, 'not_a_list', 123, True, {}, ['invalid_lsm_var']]:
        try:
            uin.make_input_config(
                'test_make_input_config',
                input_set=expected['input_set'],
                grid_size=expected['grid_size'],
                x_vars=expected['x_vars'],
                stage_2=expected['stage_2'],
                stage_2_cutoff=expected['stage_2_cutoff'],
                lsm_vars=invalid_input,
            )
        except (TypeError, ValueError) as e:
            assert True, f"make_input_config raised an exception on invalid lsm_vars {invalid_input}: {e}"
        else:
            assert False, f"make_input_config did not raise an exception on invalid lsm_vars {invalid_input}"
    # Test with invalid inputs for zfi_vars
    for invalid_input in [None, 'not_a_list', 123, True, {}, ['invalid_zfi_var']]:
        try:
            uin.make_input_config(
                'test_make_input_config',
                input_set=expected['input_set'],
                grid_size=expected['grid_size'],
                x_vars=expected['x_vars'],
                stage_2=expected['stage_2'],
                stage_2_cutoff=expected['stage_2_cutoff'],
                lsm_vars=['lsm_vars'],
                zfi_vars=invalid_input,
            )
        except (TypeError, ValueError) as e:
            assert True, f"make_input_config raised an exception on invalid zfi_vars {invalid_input}: {e}"
        else:
            assert False, f"make_input_config did not raise an exception on invalid zfi_vars {invalid_input}"
    # Test with invalid inputs for overwrite
    for invalid_input in [None, 'not_a_bool', 123, [], {}]:
        try:
            uin.make_input_config(
                'test_make_input_config',
                input_set=expected['input_set'],
                grid_size=expected['grid_size'],
                x_vars=expected['x_vars'],
                stage_2=expected['stage_2'],
                stage_2_cutoff=expected['stage_2_cutoff'],
                lsm_vars=expected['lsm_vars'],
                overwrite=invalid_input,
            )
        except TypeError as e:
            assert True, f"make_input_config raised an exception on invalid stage_2 {invalid_input}: {e}"
        else:
            assert False, f"make_input_config did not raise an exception on invalid stage_2 {invalid_input}"

def test_copy_input_files():
    """Test the copy_input_files function."""
    # Define default inputs
    default_inputs = {
        'source_input_set': 'no2_2019_JFM',
        'output_dir': 'test_copy_input_files',
        'keep_vars': 'all',
        'start_date': None,
        'end_date': None,
    }
    # Test different valid values of `keep_vars`
    valid_keep_vars = [
        'all',
        'nox',
        ['no2', 'no2_tm1'],
    ]
    for this_keep_vars in valid_keep_vars:
        # Create a copy of the input file
        uin.copy_input_files(
            source_input_set=default_inputs['source_input_set'],
            output_dir=default_inputs['output_dir'],
            keep_vars=this_keep_vars,
            start_date=default_inputs['start_date'],
            end_date=default_inputs['end_date'],
        )
        # Load the copied input netCDF file
        this_new_netCDF = uarray(default_inputs['output_dir'], is_input_set=True)
        # Load the metadata file
        input_metadata = this_new_netCDF._get_metadata()
        # Verify that the variables in the copied file match the expected variables
        if this_keep_vars == 'all':
            # Assemble the list of all variables
            expected_vars = list(set(input_metadata['x_vars'] + input_metadata['x1_vars'] + input_metadata['x2_vars'] + [input_metadata['y_var']]))
            if input_metadata['lsm'] == 'True':
                expected_vars.append('lsm')
        else: 
            expected_vars = list(set(this_keep_vars))
        actual_vars = list(set(this_new_netCDF.xr.data_vars.keys()))
        assert actual_vars.sort() == expected_vars.sort(), f"`copy_input_files()` did not copy the expected variables. \nGot: {actual_vars} \nExpected: {expected_vars}"
        # Release the loaded file
        this_new_netCDF = 'None'
    
    # Test different valid values of `start_date` and `end_date`
    valid_date_ranges = [
        {
            'start': '2019-01-02',
            'end': '2019-03-31',
            'exp_start': '2019-01-02',
            'exp_end': '2019-03-31',
        },
        {
            'start': '2019-01-02',
            'end': '2019-01-31',
            'exp_start': '2019-01-02',
            'exp_end': '2019-01-31',
        },
        {
            'start': None,
            'end': '2019-02-15',
            'exp_start': '2019-01-02',
            'exp_end': '2019-02-15',
        },
        {
            'start': '2019-02-02',
            'end': None,
            'exp_start': '2019-02-02',
            'exp_end': '2019-03-31',
        },
    ]
    for this_date_range in valid_date_ranges:
        # Create a copy of the input file
        uin.copy_input_files(
            source_input_set=default_inputs['source_input_set'],
            output_dir=default_inputs['output_dir'],
            keep_vars=default_inputs['keep_vars'],
            start_date=this_date_range['start'],
            end_date=this_date_range['end'],
        )
        # Load the copied input netCDF file
        this_new_netCDF = uarray(default_inputs['output_dir'], is_input_set=True)
        # Get the actual start and end dates from the copied file as strings
        this_start = this_new_netCDF.xr['time'].values[0]
        actual_start_date = f"{this_start.year:04d}-{this_start.month:02d}-{this_start.day:02d}"
        this_end = this_new_netCDF.xr['time'].values[-1]
        actual_end_date = f"{this_end.year:04d}-{this_end.month:02d}-{this_end.day:02d}"
        # Verify that the date range in the copied file matches the expected date range
        assert actual_start_date == this_date_range['exp_start'], f"`copy_input_files()` did not copy the expected start date. Got: {actual_start_date}, Expected: {this_date_range['exp_start']}"
        assert actual_end_date == this_date_range['exp_end'], f"`copy_input_files()` did not copy the expected end date. Got: {actual_end_date}, Expected: {this_date_range['exp_end']}"
        # Release the loaded file
        this_new_netCDF = 'None'

    # Clean up test directory
    remove_non_empty_directory(f"inputfiles/{default_inputs['output_dir']}/")