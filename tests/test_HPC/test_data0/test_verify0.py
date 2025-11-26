import xarray as xr
import numpy as np

from unox.HPC.data0.data import load_dataset
import unox.HPC.data0.verify as vfy

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

def test_verify_dataset():
    """Test the verify_dataset function."""
    # Test with sample datafiles
    for datafile in sample_datafiles:
        xr_dataset = load_dataset(datafile)
        try:
            vfy.verify_dataset(xr_dataset, check_time=True)
        except Exception as e:
            assert False, f"verify_dataset raised an exception on {datafile}: {e}"
    # Verify minimal xarray DataArrays
    for minimal_xr in [minimal_xr0, minimal_xr1]:
        try:
            vfy.verify_dataset(minimal_xr0, check_time=True)
        except Exception as e:
            assert False, f"verify_dataset raised an exception on minimal example: {e}"
    # Try to verify minimal xarray DataArray with each coordinate missing
    for coord in ['lat', 'lon', 'time']:
        minimal_xr0_missing_coord = minimal_xr0.copy()
        minimal_xr0_missing_coord = minimal_xr0_missing_coord.drop_vars(coord)
        try:
            vfy.verify_dataset(minimal_xr0_missing_coord, check_time=True)
        except ValueError as e:
            assert True, f"verify_dataset raised an exception on minimal example with missing {coord} coordinate: {e}"
        else:
            assert False, f"verify_dataset did not raise an exception on minimal example with missing {coord} coordinate"
    # Verify minimal xarray DataArray without time coordinate
    # Assumes that 'time' was the last coordinate tested in above for-loop
    try:
        vfy.verify_dataset(minimal_xr0_missing_coord, check_time=False)
    except Exception as e:
        assert False, f"verify_dataset raised an exception on minimal example with check_time=False: {e}"
    # Test with invalid inputs
    invalid_inputs = [
        # Invalid type
        "invalid_string",
        # xarray DataArray with missing lat coordinate
        xr.DataArray(data=[[1], [3]], coords={"lon": [-180, -180], "time": [np.datetime64("2019-01-01")]}, dims=["lon", "time"]),
        # xarray DataArray with missing lon coordinate
        xr.DataArray(data=[[1], [3]], coords={"lat": [-90, 90], "time": [np.datetime64("2019-01-01")]}, dims=["lat", "time"]),
        # xarray DataArray with missing time coordinate
        xr.DataArray(data=[[1, 2], [3, 4]], coords={"lat": [-90, 90], "lon": [-180, -180]}, dims=["lat", "lon"]),
    ]
    # Concatenate with invalid_datasets list
    invalid_inputs.extend(invalid_datasets)
    # Test invalid inputs to xr_dataset argument
    for invalid_dataset in invalid_datasets:
        try:
            vfy.verify_dataset(invalid_dataset, check_time=False)
        except (TypeError, ValueError) as e:
            assert True, f"verify_dataset raised an exception on invalid dataset: {e}"
        else:
            assert False, f"verify_dataset did not raise an exception on invalid dataset: {invalid_dataset}"
    # Create invalid inputs list for check_time argument
    invalid_inputs = ['invalid_string', 1234, None, 1.5, [], {}]
    # Test invalid inputs to check_time argument
    for invalid_check_time in invalid_inputs:
        try:
            vfy.verify_dataset(minimal_xr0, check_time=invalid_check_time)
        except TypeError as e:
            assert True, f"verify_dataset raised an exception on invalid check_time argument: {e}"
        else:
            assert False, f"verify_dataset did not raise an exception on invalid check_time argument: {invalid_check_time}"
    # Test invalid inputs to shift_lons argument
    for invalid_shift_lons in invalid_inputs:
        try:
            vfy.verify_dataset(minimal_xr0, shift_lons=invalid_shift_lons)
        except TypeError as e:
            assert True, f"verify_dataset raised an exception on invalid shift_lons argument: {e}"
        else:
            assert False, f"verify_dataset did not raise an exception on invalid shift_lons argument: {invalid_shift_lons}"