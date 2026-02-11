import xarray as xr
import pandas as pd
import json

from unox.HPC.data0 import dataset as udata

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

def test_csv_to_pd():
    """Test the csv_to_pd function."""
    
    # Test valid CSV file
    csv_file = 'tests/data_for_tests/sample.csv'
    expected_df = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })
    actual_df = udata.csv_to_pd(csv_file, is_US_EPA=False)
    pd.testing.assert_frame_equal(actual_df, expected_df, check_dtype=True)

    # Test US EPA csv file
    epa_csv_file = 'datafiles/sample_data/daily_42602_2019.csv'
    expected_cols = ['Latitude', 'Longitude', 'no2']
    actual_cols = udata.csv_to_pd(epa_csv_file, is_US_EPA=True).columns
    assert list(actual_cols) == expected_cols, f"Expected columns {expected_cols}, but got {list(actual_cols)}"

    # Test invalid CSV file
    invalid_csv_file = 'tests/data_for_tests/invalid.csv'
    try:
        udata.csv_to_pd(invalid_csv_file)
    except FileNotFoundError as e:
        assert True, f"csv_to_pd raised an exception on invalid input: {e}"
    else:
        assert False, f"csv_to_pd did not raise an exception on invalid input: {invalid_csv_file}"

    # Test non-CSV file
    non_csv_file = 12345
    try:
        udata.csv_to_pd(non_csv_file)
    except TypeError as e:
        assert True, f"csv_to_pd raised an exception on non-CSV file: {e}"
    else:
        assert False, f"csv_to_pd did not raise an exception on non-CSV file: {non_csv_file}"
    
def test_get_US_EPA_species_name():
    """Test the get_US_EPA_species_name function."""
    
    # Test valid species IDs
    valid_ids = ['44201', '42401', '88101', '42602']
    expected_names = ['o3', 'so2', 'pm25', 'no2']
    for id, expected_name in zip(valid_ids, expected_names):
        actual_name = udata.get_US_EPA_species_name(id)
        assert actual_name == expected_name, f"Expected {expected_name}, but got {actual_name}"
    
    # Test invalid species name
    invalid_species = 'not_a_species'
    try:
        udata.get_US_EPA_species_name(invalid_species)
    except ValueError as e:
        assert True, f"get_US_EPA_species_name raised an exception on invalid input: {e}"
    else:
        assert False, f"get_US_EPA_species_name did not raise an exception on invalid input: {invalid_species}"

def test_get_years():
    """Test the get_years function."""
    # Test with sample data files
    expected_years = {
        'datafiles/sample_data/2019u10.nc': [2019],
        'datafiles/sample_data/daily_42602_2019.csv': [2019],
        'datafiles/sample_data/nox_2019_t106_US.nc': [2019],
        'datafiles/sample_data/TROPESS_reanalysis_mon_emi_nox_anth_2021.nc': [2021],
    }
    for datafile, expected in expected_years.items():
        # Pass datafile as string
        actual_years = udata.get_years(datafile)
        assert actual_years == expected, f"Expected years {expected} from '{datafile}' as string, but got {actual_years}"
        # Pass datafile as xarray Dataset
        xr_dataset = udata.load_dataset(datafile)
        actual_years = udata.get_years(xr_dataset)
        assert actual_years == expected, f"Expected years {expected} from '{datafile}' as xarray, but got {actual_years}"
        # Pass datafile as uarray
        this_uarr = udata.uarray(datafile)
        actual_years = udata.get_years(this_uarr)
        assert actual_years == expected, f"Expected years {expected} from '{datafile}' as uarray, but got {actual_years}"
        
    
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
            udata.get_years(invalid_path)
        except Exception as e:
            assert True, f"get_years raised an exception on invalid file path: {e}"
        else:
            assert False, f"get_years did not raise an exception on invalid file path: {invalid_path}"

def test_get_metadata():
    """Test the get_metadata function."""
    # Define the example input set
    input_set = 'no2_2019_JFM'
    # Load the input set as a uarray
    this_uarr = udata.uarray(input_set, is_input_set=True)
    # Get metadata
    metadata = this_uarr._get_metadata()
    # Load the expected metadata from a known source
    with open(f"inputfiles/{input_set}/input_metadata.json", 'r') as f:
        expected_metadata = json.load(f)
    # Compare the metadata
    assert metadata == expected_metadata, f"Expected metadata: \n{expected_metadata}\n Got: \n{metadata}"

def test_is_ensemble():
    """Test the is_ensemble function."""
    # Define valid test cases
    test_cases = [
        {
            'dataset': 'no2_2019_JFM',
            'is_input_set': True,
            'is_predict': False,
            'expected_result': False,
        },
        {
            'dataset': 'no2_example_run',
            'is_input_set': False,
            'is_predict': True,
            'expected_result': False,
        },
        {
            'dataset': 'test_ens0',
            'is_input_set': False,
            'is_predict': True,
            'expected_result': True,
        },
    ]
    # Test each case
    for case in test_cases:
        # Get the actual result
        actual_result = udata.is_ensemble(case['dataset'], is_input_set=case['is_input_set'], is_predict=case['is_predict'])
        # Compare to the expected result
        assert actual_result == case['expected_result'], f"For dataset '{case['dataset']}', expected is_ensemble: {case['expected_result']}, got: {actual_result}"

def test_get_epochs_logs():
    """Test the get_epochs_logs function."""
    # Define valid test cases
    test_cases = [
        {
            'dataset': 'no2_example_run',
            'is_input_set': False,
            'is_predict': True,
            'expected_result': False,
        },
        # {
        #     'dataset': 'test_ens0',
        #     'is_input_set': False,
        #     'is_predict': True,
        #     'expected_result': True,
        # },
    ]
    # Test each case
    for case in test_cases:
        # Get the `uarray` object
        this_uarr = udata.uarray(case['dataset'], is_predict=True)
        # Get the actual result
        actual_logs = udata.get_epochs_logs(this_uarr)
        # Get the stages of this prediction set
        stages = this_uarr.xr.attrs['stages']
        # Loop across the stages of this prediction set
        for stage in stages:
            # Assemble the file name of the CSV 
            csv_filename = f"HPC_runs/{this_uarr.name}/unet_stage{stage}_log.csv"
            # Load the CSV into a Pandas Data Frame
            this_df = pd.read_csv(csv_filename, delimiter=';')
            # Get just this stage from the actual logs
            this_stage = actual_logs.sel(stage=1)
            # Compare to the expected result
            assert this_stage == this_df.to_xarray(), f"For dataset '{case['dataset']}', epoch logs from `get_epochs_logs()` does not match the expected for stage {stage}."
