import xarray as xr

from unox.HPC.data0 import data as udata

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

def test_get_dataset():
    """Test the get_dataset function."""
    # Test with sample data files
    for datafile in sample_datafiles:
        xr_dataset = udata.get_dataset(datafile)
        assert isinstance(xr_dataset, xr.Dataset), f"get_dataset did not return an xarray Dataset from '{datafile}'"
        # Check if the dataset contains expected variables
        expected_vars = ['lat', 'lon', 'time']
        for var in expected_vars:
            assert var in xr_dataset.variables, f"Variable '{var}' not found in loaded dataset from '{datafile}'"
    # Test with invalid file paths
    invalid_inputs = [
        'datafiles/sample_data/non_existent_file.nc',
        'tests/data_for_tests/sample.csv',
        'tests/data_for_tests/lats_TROPESS_reanalysis_mon_emi_nox_anth_2021.npy',
        'tests/data_for_tests/lons_TROPESS_reanalysis_mon_emi_nox_anth_2021.npy',
    ]
    # Concatenate with invalid_datasets list
    invalid_inputs.extend(invalid_datasets)
    for invalid_path in invalid_inputs:
        try:
            xr_dataset = udata.get_dataset(invalid_path)
        except Exception as e:
            assert True, f"get_dataset raised an exception on invalid file path: {e}"
        else:
            assert False, f"get_dataset did not raise an exception on invalid file path: {invalid_path}"

def test_load_dataset():
    """Test the load_dataset function."""
    # Test with sample data files
    for datafile in sample_datafiles:
        xr_dataset = udata.load_dataset(datafile)
        assert isinstance(xr_dataset, xr.Dataset), f"load_dataset did not return an xarray Dataset from '{datafile}'"
        # Check if the dataset contains expected variables
        expected_vars = ['lat', 'lon', 'time']
        for var in expected_vars:
            assert var in xr_dataset.variables, f"Variable '{var}' not found in loaded dataset from '{datafile}'"
    # Test with invalid file paths
    invalid_inputs = [
        'datafiles/sample_data/non_existent_file.nc',
        'tests/data_for_tests/sample.csv',
        'tests/data_for_tests/lats_TROPESS_reanalysis_mon_emi_nox_anth_2021.npy',
        'tests/data_for_tests/lons_TROPESS_reanalysis_mon_emi_nox_anth_2021.npy',
    ]
    # Concatenate with invalid_datasets list
    invalid_inputs.extend(invalid_datasets)
    for invalid_path in invalid_inputs:
        try:
            xr_dataset = udata.load_dataset(invalid_path)
        except Exception as e:
            assert True, f"load_dataset raised an exception on invalid file path: {e}"
        else:
            assert False, f"load_dataset did not raise an exception on invalid file path: {invalid_path}"