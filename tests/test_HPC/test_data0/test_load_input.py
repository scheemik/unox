import numpy as np

import unox.HPC.data0.load_input as uload
# from unox.HPC.data0.config import get_config

input_config = {
    "input_set": "no2_2005-2020",
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
    ],
    "grid_size": [56, 120]
}

def test_get_npy_from_netcdf():
    """Test the get_npy_from_netcdf function."""
    # Define valid input parameters
    input_file = 'inputfiles/no2_2019_JFM/no2_2019_JFM.nc'
    # Define valid test cases
    test_cases = [
        {   # Test for just one variable
            'netcdf_file': input_file,
            'year': 2019,
            'config': input_config,
            'type': 'var',
            'data_select': 'u10',
            'expected_shape': (89, 56, 120),
        },
        {   # Test for y variable
            'netcdf_file': input_file,
            'year': 2019,
            'config': input_config,
            'type': 'x_or_y',
            'data_select': 'y',
            'expected_shape': (89, 56, 120, 1),
        },
        {   # Test for x variables (stage 1)
            'netcdf_file': input_file,
            'year': 2019,
            'config': input_config,
            'type': 'x_or_y',
            'data_select': 'x',
            'expected_shape': (89, 56, 120, 9),
        },
        {   # Test for x variables (stage 2)
            'netcdf_file': input_file,
            'year': 2019,
            'config': input_config,
            'type': 'x_or_y',
            'data_select': 'x2',
            'expected_shape': (89, 56, 120, 9),
        },
    ]
    # Test each case
    for case in test_cases:
        if case['type'] == 'var':
            npy_arr, lats, lons = uload.get_npy_from_netcdf(
                case['netcdf_file'],
                case['year'],
                case['config'],
                var=case['data_select'],
            )
        elif case['type'] == 'x_or_y':
            npy_arr, lats, lons = uload.get_npy_from_netcdf(
                case['netcdf_file'],
                case['year'],
                case['config'],
                x_or_y=case['data_select'],
            )
        else:
            raise ValueError(f"Invalid test case type: {case['type']}")
        assert isinstance(npy_arr, np.ndarray), f"get_npy_from_netcdf did not return a numpy array. Got type: {type(npy_arr)}) for case: {case}"
        assert npy_arr.shape == case['expected_shape'], f"get_npy_from_netcdf returned array with incorrect shape. Expected {case['expected_shape']}, got {npy_arr.shape} for case: {case}"
    
    ## Invalid test cases
    # Test invalid netcdf file paths
    for invalid_netcdf in [
        1234,
        None,
        'invalid_path/to/netcdf.nc',
        True,
        [],
        {},
    ]:
        # Try for `var` mode
        try:
            npy_arr, lats, lons = uload.get_npy_from_netcdf(
                invalid_netcdf,
                2019,
                input_config,
                var='u10',
            )
        except Exception as e:
            assert True, f"get_npy_from_netcdf raised an exception on invalid netcdf input: {e}"
        else:
            assert False, f"get_npy_from_netcdf(var) did not raise an exception on invalid netcdf input: {invalid_netcdf}"
        # Try for `x_or_y` mode
        try:
            npy_arr, lats, lons = uload.get_npy_from_netcdf(
                invalid_netcdf,
                2019,
                input_config,
                x_or_y='y',
            )
        except Exception as e:
            assert True, f"get_npy_from_netcdf raised an exception on invalid netcdf input: {e}"
        else:
            assert False, f"get_npy_from_netcdf(x_or_y) did not raise an exception on invalid netcdf input: {invalid_netcdf}"
    # Test invalid years
    for invalid_year in [
        1234,
        None,
        'abcd',
        True,
        [],
        {},
    ]:
        # Try for `var` mode
        try:
            npy_arr, lats, lons = uload.get_npy_from_netcdf(
                input_file,
                invalid_year,
                input_config,
                var='u10',
            )
        except Exception as e:
            assert True, f"get_npy_from_netcdf raised an exception on invalid year input: {e}"
        else:
            assert False, f"get_npy_from_netcdf(var) did not raise an exception on invalid year input: {invalid_year}"
        # Try for `x_or_y` mode
        try:
            npy_arr, lats, lons = uload.get_npy_from_netcdf(
                input_file,
                invalid_year,
                input_config,
                x_or_y='y',
            )
        except Exception as e:
            assert True, f"get_npy_from_netcdf raised an exception on invalid year input: {e}"
        else:
            assert False, f"get_npy_from_netcdf(x_or_y) did not raise an exception on invalid year input: {invalid_year}"
    # Test invalid config files
    for invalid_config in [
        1234,
        None,
        'invalid_path/to/netcdf.nc',
        True,
        [],
    ]:
        # Try for `var` mode
        try:
            npy_arr, lats, lons = uload.get_npy_from_netcdf(
                input_file,
                2019,
                invalid_config,
                var='u10',
            )
        except Exception as e:
            assert True, f"get_npy_from_netcdf raised an exception on invalid input config: {e}"
        else:
            assert False, f"get_npy_from_netcdf(var) did not raise an exception on invalid input config: {invalid_config}"
        # Try for `x_or_y` mode
        try:
            npy_arr, lats, lons = uload.get_npy_from_netcdf(
                input_file,
                2019,
                invalid_config,
                x_or_y='y',
            )
        except Exception as e:
            assert True, f"get_npy_from_netcdf raised an exception on invalid input config: {e}"
        else:
            assert False, f"get_npy_from_netcdf(x_or_y) did not raise an exception on invalid input config: {invalid_config}"
    # Test invalid variables
    for invalid_var in [
        1234,
        None,
        'invalid_var',
        True,
        [],
        {},
    ]:
        try:
            npy_arr, lats, lons = uload.get_npy_from_netcdf(
                input_file,
                2019,
                input_config,
                var=invalid_var,
            )
        except Exception as e:
            assert True, f"get_npy_from_netcdf raised an exception on invalid var: {e}"
        else:
            assert False, f"get_npy_from_netcdf(var) did not raise an exception on invalid var: {invalid_var}"
    # Test invalid x_or_y
    for invalid_x_or_y in [
        1234,
        None,
        'invalid_x_or_y',
        True,
        [],
        {},
    ]:
        try:
            npy_arr, lats, lons = uload.get_npy_from_netcdf(
                input_file,
                2019,
                input_config,
                x_or_y=invalid_x_or_y,
            )
        except Exception as e:
            assert True, f"get_npy_from_netcdf raised an exception on invalid x_or_y: {e}"
        else:
            assert False, f"get_npy_from_netcdf(x_or_y) did not raise an exception on invalid x_or_y: {invalid_x_or_y}"