from unox import data as unox_data
import xarray as xr
import numpy as np

minimal_xr = xr.DataArray(
        data=[[[1], [2]], [[3], [4]]],
        coords={
            "lat": [-90, 90],
            "lon": [-180, -180],
            "time": [np.datetime64("2019-01-01")],
        },
        dims=["lat", "lon", "time"]
    )

def test_get_extent(xr_dataset=xr.open_dataset('datafiles/nox_2019_t106_US.nc')):
    """Test the get_extent function."""
    # Load a sample xarray dataset for testing
    expected = (24.112, 58.878, -126.0, -59.625)
    actual = unox_data.get_extent(xr_dataset)
    assert actual == expected, f"Expected extent {expected} does not match actual extent {actual}"

def test_verify_dataset(xr_dataset=xr.open_dataset('datafiles/nox_2019_t106_US.nc')):
    """Test the verify_dataset function."""
    # Verify minimal xarray DataArray
    try:
        unox_data.verify_dataset(minimal_xr)
    except Exception as e:
        assert False, f"verify_dataset raised an exception on minimal example: {e}"
    # Load a sample xarray dataset for testing
    try:
        unox_data.verify_dataset(xr_dataset)
    except Exception as e:
        assert False, f"verify_dataset raised an exception on nox_2019_t106_US.nc: {e}"

def test_verify_dataset_invalid():
    """Test the verify_dataset function with invalid datasets."""
    # Create several invalid datasets
    invalid_datasets = [
        # Invalid type
        "invalid_string",
        # xarray DataArray with missing lat coordinate
        xr.DataArray(data=[[1], [3]], coords={"lon": [-180, -180], "time": [np.datetime64("2019-01-01")]}, dims=["lon", "time"]),
        # xarray DataArray with missing lon coordinate
        xr.DataArray(data=[[1], [3]], coords={"lat": [-90, 90], "time": [np.datetime64("2019-01-01")]}, dims=["lat", "time"]),
        # xarray DataArray with missing time coordinate
        xr.DataArray(data=[[1, 2], [3, 4]], coords={"lat": [-90, 90], "lon": [-180, -180]}, dims=["lat", "lon"]),
    ]
    # Test each invalid dataset
    for invalid_dataset in invalid_datasets:
        try:
            unox_data.verify_dataset(invalid_dataset)
        except (TypeError, ValueError) as e:
            assert True, f"verify_dataset raised an exception on invalid dataset: {e}"
        else:
            assert False, "verify_dataset did not raise an exception on invalid dataset"