import numpy as np

from unox.HPC.data0.latlon import shift_lon, shift_lon_arr

def test_shift_lon():
    """Test the shift_lon and shift_lon_arr functions."""
    # Select a tolerance for comparisons
    selected_tol = 1e-15
    ## Test the Prime Meridian centered shift
    # Create a sample array of longitude values to shift
    input = np.array([0, 45.3, 200, 359])
    expected = np.array([0, 45.3, -160.0, -1.0])
    actual = shift_lon_arr(input, PM_centered=True)
    assert np.allclose(actual, expected, atol=selected_tol, rtol=selected_tol), f"Expected {expected}, but shift_lon gave {actual}"
    # Create a sample array of longitude values to shift
    input = np.array([0, 45.3, -160.0, -1.0])
    expected = np.array([0, 45.3, -160.0, -1.0])
    actual = shift_lon_arr(input, PM_centered=True)
    assert np.allclose(actual, expected, atol=selected_tol, rtol=selected_tol), f"Expected {expected}, but shift_lon gave {actual}"
    ## Test the International Date Line centered shift
    # Create a sample array of longitude values to shift
    input = np.array([0, 45.3, -57.5, -179])
    expected = np.array([0, 45.3, 302.5, 181.0])
    actual = np.array(shift_lon_arr(input, PM_centered=False))
    assert np.allclose(actual, expected, atol=selected_tol, rtol=selected_tol), f"Expected {expected}, but shift_lon gave {actual}"
    # Test with invalid longitudes
    invalid_values = [np.nan, '45', None, -200, 400]
    for val in invalid_values:
        try:
            shift_lon(val)
        except ValueError as e:
            assert True, f"shift_lon raised an exception on invalid value {val}: {e}"
        else:
            assert False, f"shift_lon did not raise an exception on invalid value {val}"
    # Test with invalid PM_centered argument
    try:
        shift_lon_arr(input, PM_centered='invalid')
    except ValueError as e:
        assert True, f"shift_lon raised an exception on invalid PM_centered argument: {e}"
    else:
        assert False, "shift_lon did not raise an exception on invalid PM_centered argument"

def test_match_domains():
    """Test the match_domains function."""