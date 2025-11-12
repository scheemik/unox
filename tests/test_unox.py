from unox import unox
import os
import numpy as np

def test_make_file_path():
    """Test the make_file_path function."""
    # Test with valid input
    valid_path = 'test_make_file_path/path/to/file.txt'
    actual = unox.make_file_path(valid_path)
    expected = 'test_make_file_path/path/to'
    assert actual == expected, f"Expected {expected}, but got {actual}"
    # Delete the created directory for cleanup
    base_dir = valid_path.split('/')[0]
    unox.remove_non_empty_directory(base_dir)
    # Test with valid input that already exists
    # Remove everything after the second to last `/` in the valid path
    partial_path = '/'.join(valid_path.split('/')[:-2])
    print(f"Partial path: {partial_path}")
    print(f"Valid path: {valid_path}")
    os.makedirs(partial_path)
    actual = unox.make_file_path(valid_path)
    assert actual == expected, f"Expected {expected}, but got {actual}"
    # Delete the created directory for cleanup
    unox.remove_non_empty_directory(base_dir)
    # Test with invalid input
    invalid_path = 12345
    try:
        unox.make_file_path(invalid_path)
    except (TypeError) as e:
        assert True, f"make_file_path raised an exception on invalid input: {e}"
    else:
        assert False, f"make_file_path did not raise an exception on invalid input {invalid_path}"

def test_remove_non_empty_directory():
    """Test the remove_non_empty_directory function."""
    # Create a temporary directory with some files and subdirectories
    temp_dir = 'test_remove_non_empty_directory'
    os.makedirs(temp_dir, exist_ok=True)
    with open(os.path.join(temp_dir, 'file1.txt'), 'w') as f:
        f.write('This is a test file.')
    os.makedirs(os.path.join(temp_dir, 'subdir'), exist_ok=True)
    with open(os.path.join(temp_dir, 'subdir', 'file2.txt'), 'w') as f:
        f.write('This is another test file.')
    
    # Remove the non-empty directory
    unox.remove_non_empty_directory(temp_dir)
    
    # Check if the directory has been removed
    assert not os.path.exists(temp_dir), f"Directory {temp_dir} was not removed."
    
    # Test with a non-directory path
    try:
        unox.remove_non_empty_directory('file1.txt')
    except FileNotFoundError as e:
        assert True, f"remove_non_empty_directory raised an exception on non-directory path: {e}"
    else:
        assert False, "remove_non_empty_directory did not raise an exception on non-directory path."

def test_show_available_data():
    """Test the show_available_data function and,
    as a result, also test the recursive_paths function."""
    expected = ['inputfiles/original_sample_data/stage1/x/X_2005.npy', 
                'inputfiles/original_sample_data/stage1/y/Y_2005.npy', 
                'inputfiles/original_sample_data/stage2/x/X_2014.npy', 
                'inputfiles/original_sample_data/stage2/y/Y_2014.npy']
    actual = unox.show_available_data('inputfiles/original_sample_data/')
    assert actual == expected, f"Expected file list (length {len(expected)}) does not match actual file list (length {len(actual)})"

def test_get_input_data():
    """Test the get_input_data function."""
    # Test with valid parameters
    expected = 'inputfiles/no2_sample_input/stage1/y/Y_2019.npy'
    valid_params = [
        {'stage': 1, 'x_or_y': 'y', 'year': 2019, 'input_set': 'no2_sample_input'},
        {'stage': 1, 'x_or_y': 'y', 'year': 2019},
        {'stage': 1, 'x_or_y': 'y', 'input_set': 'no2_sample_input'},
        {'stage': 1, 'year': 2019, 'input_set': 'no2_sample_input'},
        {'x_or_y': 'y', 'year': 2019, 'input_set': 'no2_sample_input'}
        ]
    for params in valid_params:
        actual = unox.get_input_data(**params)
        assert actual == expected, f"Expected {expected}, but got {actual} with params {params}"
    
    # Test with invalid parameters
    invalid_params = [
        {'stage': 3, 'x_or_y': 'y', 'year': 2019, 'input_set': 'no2_sample_input'},
        {'stage': 1, 'x_or_y': 'z', 'year': 2019, 'input_set': 'no2_sample_input'},
        {'stage': 1, 'x_or_y': 'y', 'year': -1, 'input_set': 'no2_sample_input'},
        {'stage': 1, 'x_or_y': 'y', 'year': 2019, 'input_set': 'not_a_valid_path'}
        ]
    for params in invalid_params:
        try:
            unox.get_input_data(**params)
        except (ValueError, FileNotFoundError) as e:
            assert True, f"get_input_data raised an exception on invalid parameters {params}: {e}"
        else:
            assert False, f"get_input_data did not raise an exception on invalid parameters {params}"

def test_get_one_input_var_array():
    """Test the get_one_input_var_array function."""
    # Get the input variable dictionary
    from unox.input import input_vars_dict
    # Set parameters for test
    this_stage = 1
    this_year = 2019
    this_input_set = 'no2_sample_input'
    # Test across all 'no2' variables in the input variable dictionary
    key = 'no2'
    for x_or_y_key in input_vars_dict[key].keys():
        x_or_y = x_or_y_key[0]
        list_of_vars = input_vars_dict[key][x_or_y_key]
        for i in range(len(list_of_vars)):
            var = list_of_vars[i]
            actual = unox.get_one_input_var_array(
                var,
                stage=this_stage,
                year=this_year,
                input_set=this_input_set,
            )
            expected = np.load(unox.get_input_data(stage=this_stage, x_or_y=x_or_y, year=this_year, input_set=this_input_set))[:, :, :, i]
            assert np.array_equal(actual, expected), f"get_one_input_var_array did not return expected array for {key}, {x_or_y_key}[{i}]={var}"
    # Test invalid variables
    invalid_vars = [None, '', 'not_a_var', 123, True, False, [], {}]
    for var in invalid_vars:
        try:
            unox.get_one_input_var_array(
                var,
                stage=this_stage,
                year=this_year,
                input_set=this_input_set,
            )
        except (TypeError, ValueError) as e:
            assert True, f"get_one_input_var_array raised an exception on invalid variable '{var}': {e}"
        else:
            assert False, f"get_one_input_var_array did not raise an exception on invalid variable '{var}'"

def test_get_one_t_input_var_array():
    """Test the get_one_t_input_var_array function."""
    # Get the input variable dictionary
    from unox.input import input_vars_dict
    # Set the parameters for the test
    this_stage = 1
    this_year = 2019
    this_input_set = 'no2_sample_input'
    # Create a list of dates and DOYs to test in this_year
    valid_dates_doys = [
        ('2019-01-01', 0),
        ('2019-06-15', 165),
        ('2019-12-31', 364),
        ('2019-02-28', 58),
        ('2019-03-01', 59),
    ]
    # Test across all 'no2' variables in the input variable dictionary
    key = 'no2'
    for x_or_y_key in input_vars_dict[key].keys():
        x_or_y = x_or_y_key[0]
        list_of_vars = input_vars_dict[key][x_or_y_key]
        for i in range(len(list_of_vars)):
            var = list_of_vars[i]
            for this_date, this_doy in valid_dates_doys:
                actual = unox.get_one_t_input_var_array(
                    var,
                    this_date,
                    stage=this_stage,
                    input_set=this_input_set,
                )
                expected = np.load(unox.get_input_data(stage=this_stage, x_or_y=x_or_y, year=this_year, input_set=this_input_set))[this_doy, :, :, i]
                assert actual.shape == expected.shape, f"get_one_t_input_var_array returned array with shape {actual.shape} instead of expected shape {expected.shape} for {key}, {x_or_y_key}[{i}]={var} on {this_date}"
                assert np.array_equal(actual, expected), f"get_one_t_input_var_array did not return expected array for {key}, {x_or_y_key}[{i}]={var} on {this_date}"


def test_get_pred_data():
    """Test the get_pred_data function."""
    # Test with valid parameters
    params = {'stage': 1, 'HPC_run': 'no2_example_run', 'year': 2019}
    actual = unox.get_pred_data(**params)
    expected = 'HPC_runs/no2_example_run/stage1_output/pred_X_2019.npy'
    assert actual == expected, f"Expected {expected}, but got {actual}"
    
    # Test with invalid parameters
    invalid_params = [{'stage': 3, 'HPC_run': 'no2_example_run', 'year': 2019},
                      {'stage': 1, 'HPC_run': '', 'year': 2019},
                      {'stage': 1, 'HPC_run': 'no2_example_run', 'year': -1}]
    for params in invalid_params:
        try:
            unox.get_pred_data(**params)
        except (ValueError, FileNotFoundError) as e:
            assert True, f"get_pred_data raised an exception on invalid parameters {params}: {e}"
        else:
            assert False, f"get_pred_data did not raise an exception on invalid parameters {params}"

def test_interpret_user_input():
    """Test the interpret_user_input function."""
    # Test with valid parameters
    valid_inputs = ['y', 'yes', 'Y', 'Yes', 'YES', 
                    'n', 'no', 'N', 'No', 'NO']
    expected_outputs = [True, True, True, True, True,
                        False, False, False, False, False]
    for i in range(len(valid_inputs)):
        user_input = valid_inputs[i]
        expected = expected_outputs[i]
        actual = unox.interpret_user_input(user_input)
        assert actual == expected, f"Expected {expected} for input '{user_input}', but got {actual}"
    # Test with invalid parameters
    invalid_inputs = [123, None, '', 'maybe', True, False, [], {}]
    for user_input in invalid_inputs:
        try:
            unox.interpret_user_input(user_input)
        except (TypeError, ValueError) as e:
            assert True, f"interpret_user_input raised an exception on invalid input '{user_input}': {e}"
        else:
            assert False, f"interpret_user_input did not raise an exception on invalid input '{user_input}'"