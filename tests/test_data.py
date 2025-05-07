from unox import data as unox_data
import xarray as xr
import numpy as np

minimal_xr = xr.DataArray(
        data=[[[1], [2]], [[3], [4]]],
        coords={
            "lat": [-90, 90],
            "lon": [-180, 180],
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
    # Test with minimal xarray DataArray
    expected = (-90.0, 90.0, -180.0, 180.0)
    actual = unox_data.get_extent(minimal_xr)
    assert actual == expected, f"Expected extent {expected} does not match actual extent {actual}"

def test_get_lats_lons(path='datafiles/TROPESS_reanalysis_mon_emi_nox_anth_2021.nc'):
    """Test the get_lats_lons function."""
    # Load a sample xarray dataset for testing
    expected_lats = np.load('tests/lats_TROPESS_reanalysis_mon_emi_nox_anth_2021.npy')
    expected_lons = np.load('tests/lons_TROPESS_reanalysis_mon_emi_nox_anth_2021.npy')
    actual_lats, actual_lons = unox_data.get_lats_lons(xr_dataset=xr.open_dataset(path))
    assert np.array_equal(actual_lats, expected_lats), f"Expected lats {expected_lats} do not match actual lats {actual_lats}"
    assert np.array_equal(actual_lons, expected_lons), f"Expected lons {expected_lons} do not match actual lons {actual_lons}"

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

def test_verify_number():
    """Test the verify_number function."""
    # Test valid number values
    valid_numbers = [0, 1, -1, 1.5, -1.5, 1e-15]
    for num in valid_numbers:
        assert unox_data.verify_number(num) == True, f"verify_number failed on valid number {num}"
    # Test invalid number values
    invalid_numbers = [np.nan, np.inf, -np.inf, '1', None]
    for num in invalid_numbers:
        assert unox_data.verify_number(num) == False, f"verify_number failed on invalid number {num}"

def test_verify_lat():
    """Test the verify_lat function."""
    # Test valid latitude values
    valid_lats = [0, 45, -45, 90, -90, 41.7]
    for lat in valid_lats:
        assert unox_data.verify_lat(lat) == lat, f"verify_lat failed on valid latitude {lat}"
    # Test invalid latitude values
    invalid_lats = [91, -91, 100, -100, np.nan, '45']
    for lat in invalid_lats:
        try:
            unox_data.verify_lat(lat)
        except ValueError as e:
            assert True, f"verify_lat raised an exception on invalid latitude {lat}: {e}"
        else:
            assert False, f"verify_lat did not raise an exception on invalid latitude {lat}"

def test_verify_lon():
    """Test the verify_lon function."""
    # Test valid longitude values
    valid_lons = [0, 45, -45, 180, -180]
    for lon in valid_lons:
        assert unox_data.verify_lon(lon) == lon, f"verify_lon failed on valid longitude {lon}"
    # Test invalid longitude values
    invalid_lons = [181, -181, 360, -360, 400, -400, np.nan, '45']
    for lon in invalid_lons:
        try:
            unox_data.verify_lon(lon)
        except ValueError as e:
            assert True, f"verify_lon raised an exception on invalid longitude {lon}: {e}"
        else:
            assert False, f"verify_lon did not raise an exception on invalid longitude {lon}"

def test_shift_lon():
    """Test the shift_lon function."""
    # Create a sample array of longitude values to shift
    input = np.array([0, 45.3, 200, 360])
    expected = np.array([-180, -134.7, 20, 180])
    actual = np.array(list(map(unox_data.shift_lon, input)))
    assert np.array_equal(actual, expected), f"Expected {expected}, but shift_lon gave {actual}"
    # Test with invalid values
    invalid_values = [np.nan, '45', None]
    for val in invalid_values:
        try:
            unox_data.shift_lon(val)
        except ValueError as e:
            assert True, f"shift_lon raised an exception on invalid value {val}: {e}"
        else:
            assert False, f"shift_lon did not raise an exception on invalid value {val}"