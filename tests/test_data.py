from unox import data as unox_data
import xarray as xr

def test_get_extent(xr_dataset=xr.open_dataset('datafiles/nox_2019_t106_US.nc')):
    """Test the get_extent function."""
    # Load a sample xarray dataset for testing
    expected = (24.112, 58.878, -126.0, -59.625)
    actual = unox_data.get_extent(xr_dataset)
    assert actual == expected, f"Expected extent {expected} does not match actual extent {actual}"