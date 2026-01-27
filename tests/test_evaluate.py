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

def test_get_corr_R2():
    """Test the get_corr_R2 function."""
    # Define expected R^2 values and data sources
    test_cases = [
        (minimal_xr0['var1'], minimal_xr0['var1'], 1.0),
        (minimal_xr0['var1'], minimal_xr0['var1']*2, 1.0),
        (minimal_xr0['var1'], minimal_xr0['var1'].values, 1.0),
        (minimal_xr0['var1'].values, minimal_xr0['var1'], 1.0),
        (minimal_xr0['var1'].values, minimal_xr0['var1'].values, 1.0),
        (minimal_xr0['var1'], minimal_xr0['var2'], 0.0),
        (minimal_xr0['var1'], minimal_xr0['var3'], 0.238095),
    ]
    # Define tolerance for floating point comparison
    tolerance = 1e-6
    # Test each case
    for case in test_cases:
        # Unpack the case
        a_arr, b_arr, expected_R2 = case
        # Calculate actual R^2
        actual_R2 = ueval.get_corr_R2(a_arr, b_arr)
        # Compare to the expected value
        assert np.isclose(actual_R2, expected_R2, atol=tolerance), f"Expected R^2: {expected_R2}, got: {actual_R2}"
    # Test invalid inputs
    for invalid_input in invalid_datasets:
        try:
            ueval.get_corr_R2(invalid_input, minimal_xr0['var1'])
            assert False, f"Expected TypeError for `a_xr_arr` input: {invalid_input}"
        except TypeError:
            pass
        try:
            ueval.get_corr_R2(minimal_xr0['var1'], invalid_input)
            assert False, f"Expected TypeError for `b_xr_arr` input: {invalid_input}"
        except TypeError:
            pass