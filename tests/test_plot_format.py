from unox import plot_format as uplt_fmt
from unox import data as udata
import xarray as xr

def test_pad_extent():
    """Test the pad_extent function."""
    # Get extent from sample netcdf
    nox = xr.open_dataset('datafiles/sample_data/nox_2019_t106_US.nc')
    nox_extent = udata.get_extent(nox)
    # Define valid and expected outputs
    inputs_pad_expected = [
        (nox_extent, 0.1, (20.635399999999997, 62.3546, -132.6375, -52.9875)),
        ((20.0, 60.0, -130.0, -50.0), 0.1, (16.0, 64.0, -138.0, -42.0)),
        ((20.0, 60.0, -130.0, -50.0), 0.01, (19.6, 60.4, -130.8, -49.2)),
        ((-90.0, 90.0, -180.0, 180.0), 0.1, (-90.0, 90.0, -180.0, 180.0)),
    ]
    for extent, pad, expected in inputs_pad_expected:
        padded_extent = uplt_fmt.pad_extent(extent, padding=pad)
        assert padded_extent == expected, f"Expected {expected}, but got {padded_extent} for extent {extent} with padding {pad}"
    # Define invalid inputs
    invalid_inputs_pad = [
        (None, 0.1),
        (nox_extent, None),
        (nox_extent, '0.1'),
        ((20.0, 60.0, -130.0), 0.1),
        ((20.0, 60.0, -130.0, -50.0, 10.0), 0.1),
        ('not_a_tuple', 0.1),
    ]
    for extent, pad in invalid_inputs_pad:
        try:
            uplt_fmt.pad_extent(extent, padding=pad)
        except (ValueError, TypeError) as e:
            assert True, f"pad_extent raised an exception on invalid input {extent} with padding {pad}: {e}"
        else:
            assert False, f"pad_extent did not raise an exception on invalid input {extent} with padding {pad}"

def test_get_var_label_and_units():
    """Test the get_var_label_and_units function."""
    # Define valid inputs and expected outputs
    inputs_expected = {
        'blh': ('Boundary layer height', 'm'),
        'sp':  ('Surface pressure', 'Pa'),
        'skt': ('Skin temperature', 'K'),
    }
    for var, (label, units) in inputs_expected.items():
        actual_label, actual_units = uplt_fmt.get_var_label_and_units(var)
        assert actual_label == label, f"Expected label '{label}', but got '{actual_label}' for variable '{var}'"
        assert actual_units == units, f"Expected units '{units}', but got '{actual_units}' for variable '{var}'"
    
    # Test with invalid variables
    invalid_vars = [
        'invalid_var',
        1999
    ]
    for invalid_var in invalid_vars:
        try:
            label, units = uplt_fmt.get_var_label_and_units(invalid_var)
        except ValueError as e:
            assert True, f"get_var_label_and_units raised an exception on invalid input {invalid_var}: {e}"
        else:
            assert False, f"get_var_label_and_units did not raise an exception for invalid variable {invalid_var}."