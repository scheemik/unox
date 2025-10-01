from unox import input as uin
import unox.unox as unox
import numpy as np
import os
import json

def test_x_or_y_var():
    """Test the x_or_y_var function."""
    # Make lists of valid inputs
    valid_x_vars = []
    valid_y_vars = []
    for key in uin.input_vars_dict.keys():
        valid_x_vars += uin.input_vars_dict[key]['x_vars']
        valid_y_vars += uin.input_vars_dict[key]['y_vars']
    # Test valid x variables
    for var in valid_x_vars:
        assert uin.x_or_y_var(var) == 'x', f"x_or_y_var did not return 'x' for valid x variable '{var}'"
    # Test valid y variables
    for var in valid_y_vars:
        assert uin.x_or_y_var(var) == 'y', f"x_or_y_var did not return 'y' for valid y variable '{var}'"
    # Make lists of invalid inputs
    invalid_vars = [None, '', 'not_a_var', 123, True, False, [], {}]
    # Test invalid variables
    for var in invalid_vars:
        try:
            uin.x_or_y_var(var)
        except (TypeError, ValueError) as e:
            assert True, f"x_or_y_var raised an exception on invalid input '{var}': {e}"
        else:
            assert False, f"x_or_y_var did not raise an exception on invalid input '{var}'"


def test_make_y_input_file():
    """Test the make_y_input_file function."""
    # Set the arguments for a test run
    datadir='/data/high_res/emacdonald/unet/datafiles/t106'
    verifydir='inputfiles/no2_input_test1/'
    this_year=2019
    # Assemble file path to verification array
    verify_filepath = f"{verifydir}stage1/y/Y_{this_year}.npy"
    # Verify that file path
    verify_filepath = unox.verify_path(verify_filepath)
    # Load the verification array
    verify_array = np.load(verify_filepath)
    # Call the function to create the y input file
    y_data = uin.make_y_input_file(
        year=this_year, 
        var='nox',
        emiss_dir=datadir,
        emiss_pre='nox_',
        emiss_post='_t106_US.nc',
        scale_factor=1e12,
        nan_fill=0,
        stage_2_cutoff=2022,
        output_dir=None
    )
    # Verify that the output is a numpy array
    assert isinstance(y_data, np.ndarray), "make_y_input_file did not return a numpy array."
    # Verify that the shape of the output matches the verification array
    assert y_data.shape == verify_array.shape, f"make_y_input_file output shape {y_data.shape} does not match verification array shape {verify_array.shape}"
    # Verify that the output matches the verification array
    assert np.array_equal(y_data, verify_array), f"make_y_input_file output does not match array from {verify_filepath}"

def test_make_x_input_file():
    """Test the make_x_input_file function."""
    # Set the arguments for a test run
    datadir='/data/high_res/emacdonald/unet/datafiles/'
    verifydir='inputfiles/no2_input_test1/'
    this_year=2019
    for this_stage in [1, 2]:
        # Assemble file path to verification array
        verify_filepath = f"{verifydir}stage{this_stage}/x/X_{this_year}.npy"
        # Verify that file path
        verify_filepath = unox.verify_path(verify_filepath)
        # Load the verification array
        verify_array = np.load(verify_filepath)
        # Call the function to create the x input file
        x_data = uin.make_x_input_file(
            year=this_year, 
            stage=this_stage,
            data_dir=datadir,
            chemra_path='TROPESS/TROPESS_reanalysis_2hr_no2_sfc_',
            insitu_path='US_EPA/daily_42602_',
            era5_path='ERA5concatenated/',
            scale_factors={
                'chemra': 1000,
                'sp': 100000,
                'ssrd': 1000000,
                'blh': 1000},
            output_dir=None
        )
        # Verify that the output is a numpy array
        assert isinstance(x_data, np.ndarray), "make_x_input_file did not return a numpy array."
        # Verify that the shape of the output matches the verification array
        assert x_data.shape == verify_array.shape, f"make_x_input_file output shape {x_data.shape} does not match verification array shape {verify_array.shape}"
        # Verify that the output matches the verification array
        assert np.array_equal(x_data, verify_array), f"make_x_input_file output does not match array from {verify_filepath}"

def test_make_input_metadata_file():
    """Test the make_input_metadata_file function."""
    # Load the verification metadata
    verify_file = 'tests/data_for_tests/input_metadata.json'
    with open(verify_file, 'r') as f:
        verify_dict = json.load(f)
    # Make the attribute dictionaries
    x_attrs = {
        'data_dir': '/data/high_res/emacdonald/unet/datafiles/',
        'chemra_path': 'TROPESS/TROPESS_reanalysis_2hr_no2_sfc_',
        'insitu_path': 'US_EPA/daily_42602_',
        'era5_path': 'ERA5concatenated/',
        'var_scale_factors': {
            'chemra': 1000,
            'u10': 1,
            'v10': 1,
            'blh': 1000,
            'sp': 100000,
            'skt': 1,
            't2m': 1,
            'ssrd': 1000000,
        },
        'stage_2_cutoff': 2013,
    }
    y_attrs = {
        'var': 'nox',
        'emiss_dir': '/data/high_res/emacdonald/unet/datafiles/t106',
        'emiss_pre': 'nox_',
        'emiss_post': '_t106_US.nc',
        'scale_factor': 1e12,
        'nan_fill': 0,
        'stage_2_cutoff': 2013,
    }
    # Call the function to create the metadata file
    for year in [2005, 2008, 2009, 2012, 2013, 2014, 2015]:
        uin.make_input_metadata_file(
            year,
            'x',
            x_attrs,
            stage=None,
            output_dir='test_make_input_metadata_file',
        )
        uin.make_input_metadata_file(
            year,
            'y',
            y_attrs,
            stage=None,
            output_dir='test_make_input_metadata_file',
        )
    # Load the created metadata file
    test_file = 'inputfiles/test_make_input_metadata_file/input_metadata.json'
    with open(test_file, 'r') as f:
        test_dict = json.load(f)
    # Verify that the created metadata matches the verification metadata
    assert test_dict == verify_dict, "make_input_metadata_file output does not match verification metadata."
    # Clean up the test directory
    if os.path.exists("inputfiles/test_make_input_metadata_file"):
        for file in os.listdir("inputfiles/test_make_input_metadata_file"):
            file_path = os.path.join("inputfiles/test_make_input_metadata_file", file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir("inputfiles/test_make_input_metadata_file")
    
    # Test invalid inputs
    for year in [None, '2019', True, False]:
        try:
            uin.make_input_metadata_file(
                year,
                'x',
                x_attrs,
                stage=None,
                output_dir=None,
            )
        except TypeError as e:
            assert True, f"make_input_metadata_file raised an exception on invalid year {year}: {e}"
        else:
            assert False, f"make_input_metadata_file did not raise an exception on invalid year {year}"
    for x_or_y in [None, 'z', True, False, 1]:
        try:
            uin.make_input_metadata_file(
                2019,
                x_or_y,
                x_attrs,
                stage=None,
                output_dir=None,
            )
        except (ValueError, TypeError) as e:
            assert True, f"make_input_metadata_file raised an exception on invalid x_or_y {x_or_y}: {e}"
        else:
            assert False, f"make_input_metadata_file did not raise an exception on invalid x_or_y {x_or_y}"
    for attrs in [None, 'not_a_dict', True, False, 123]:
        try:
            uin.make_input_metadata_file(
                2019,
                'x',
                attrs,
                stage=None,
                output_dir=None,
            )
        except TypeError as e:
            assert True, f"make_input_metadata_file raised an exception on invalid attrs {attrs}: {e}"
        else:
            assert False, f"make_input_metadata_file did not raise an exception on invalid attrs {attrs}"
    for stage in ['1', True, False, 3]:
        try:
            uin.make_input_metadata_file(
                2019,
                'x',
                x_attrs,
                stage=stage,
                output_dir=None,
            )
        except ValueError as e:
            assert True, f"make_input_metadata_file raised an exception on invalid stage {stage}: {e}"
        else:
            assert False, f"make_input_metadata_file did not raise an exception on invalid stage {stage}"
    for output_dir in [True, False, 123]:
        try:
            uin.make_input_metadata_file(
                2019,
                'x',
                x_attrs,
                stage=None,
                output_dir=output_dir,
            )
        except TypeError as e:
            assert True, f"make_input_metadata_file raised an exception on invalid output_dir {output_dir}: {e}"
        else:
            assert False, f"make_input_metadata_file did not raise an exception on invalid output_dir {output_dir}"