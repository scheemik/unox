from unox import evaluate as ueval
import xarray as xr
import numpy as np

minimal_xr0 = xr.Dataset(
    data_vars={
        "var1": (("lat", "lon", "time"), [[[1,2], [3,4]], [[5,6], [7,8]]]),
        "var2": (("lat", "lon", "time"), [[[1,2], [3,4]], [[4,3], [2,1]]]),
        "var3": (("lat", "lon", "time"), [[[1,2], [3,4]], [[1,2], [3,4]]]),
    },
    coords={
        "lat": [-90, 90],
        "lon": [-180, 180],
        "time": [np.datetime64("2019-01-01"), np.datetime64("2019-01-02")],
    },
)

invalid_datasets = [
    "invalid_string",
    12345,
    None,
    True,
    [],
    {}
]

def test_compare_arrs():
    """Test the compare_arrs function."""
    # Define expected values and data sources
    test_cases = [
        {
            'a_arr': minimal_xr0['var1'],
            'b_arr': minimal_xr0['var1'],
            'expected_R2': 1.0,
            'expected_RMSE': 0.0,
        },
        {
            'a_arr': minimal_xr0['var1'],
            'b_arr': minimal_xr0['var1']*2,
            'expected_R2': 1.0,
            'expected_RMSE': 5.0497524,
        },
        {
            'a_arr': minimal_xr0['var1'],
            'b_arr': minimal_xr0['var1'].values,
            'expected_R2': 1.0,
            'expected_RMSE': 0.0,
        },
        {
            'a_arr': minimal_xr0['var1'].values,
            'b_arr': minimal_xr0['var1'],
            'expected_R2': 1.0,
            'expected_RMSE': 0.0,
        },
        {
            'a_arr': minimal_xr0['var1'].values,
            'b_arr': minimal_xr0['var1'].values,
            'expected_R2': 1.0,
            'expected_RMSE': 0.0,
        },
        {
            'a_arr': minimal_xr0['var1'],
            'b_arr': minimal_xr0['var2'],
            'expected_R2': 0.0,
            'expected_RMSE': 3.2403703,
        },
        {
            'a_arr': minimal_xr0['var1'],
            'b_arr': minimal_xr0['var3'],
            'expected_R2': 0.238095,
            'expected_RMSE': 2.8284271,
        },
        {
            'a_arr': np.array([14,19,17,13,12,7,24,23,17,18,14,16,16,17,22,25,26,21,14,15]),
            'b_arr': np.array([17,18,18,15,18,11,20,20,15,18,15,16,17,18,25,21,28,22,16,12]),
            'expected_R2': 0.6921643,
            'expected_RMSE': 2.6645825,
        },
    ]
    # Define tolerance for floating point comparison
    tolerance = 1e-6
    # Test each case
    for case in test_cases:
        # Calculate actual R^2
        actual_R2 = ueval.compare_arrs(case['a_arr'], case['b_arr'], 'R2')
        # Compare to the expected value
        assert np.isclose(actual_R2, case['expected_R2'], atol=tolerance), f"Expected R^2: {case['expected_R2']}, got: {actual_R2}"
        # Calculate actual RMSE
        actual_RMSE = ueval.compare_arrs(case['a_arr'], case['b_arr'], 'RMSE')
        # Compare to the expected value
        assert np.isclose(actual_RMSE, case['expected_RMSE'], atol=tolerance), f"Expected RMSE: {case['expected_RMSE']}, got: {actual_RMSE}"
    # Test invalid inputs
    for invalid_input in invalid_datasets:
        try:
            ueval.compare_arrs(invalid_input, minimal_xr0['var1'])
            assert False, f"Expected TypeError for `a_xr_arr` input: {invalid_input}"
        except TypeError:
            pass
        try:
            ueval.compare_arrs(minimal_xr0['var1'], invalid_input)
            assert False, f"Expected TypeError for `b_xr_arr` input: {invalid_input}"
        except TypeError:
            pass