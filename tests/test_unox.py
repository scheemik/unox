from unox import unox
import os

def test_verify_path():
    """Test the verify_path function."""
    # Test with valid path
    valid_path = 'original_sample_data/stage1/x/X_2005.npy'
    actual = unox.verify_path(valid_path)
    print(f"Actual path: {actual}")
    assert type(unox.verify_path(valid_path)) == type('str'), f"verify_path failed on valid path: {valid_path}"
    # Test with invalid path
    invalid_path = 'invalid/path/to/file.npy'
    try:
        unox.verify_path(invalid_path)
    except (FileNotFoundError) as e:
        assert True, f"verify_path raised an exception on invalid path: {e}"
    else:
        assert False, f"verify_path did not raise an exception on invalid path {invalid_path}"
    # Test with invalid path
    invalid_path = 12345
    try:
        unox.verify_path(invalid_path)
    except (TypeError) as e:
        assert True, f"verify_path raised an exception on invalid path: {e}"
    else:
        assert False, f"verify_path did not raise an exception on invalid path {invalid_path}"

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
    expected = ['original_sample_data/stage1/x/X_2005.npy', 
                'original_sample_data/stage1/y/Y_2005.npy', 
                'original_sample_data/stage2/x/X_2014.npy', 
                'original_sample_data/stage2/y/Y_2014.npy']
    actual = unox.show_available_data('original_sample_data/')
    assert actual == expected, f"Expected file list (length {len(expected)}) does not match actual file list (length {len(actual)})"

def test_get_sample_data():
    """Test the get_sample_data function."""
    # Test with valid parameters
    params = {'stage': 1, 'x_or_y': 'y', 'year': 2019}
    actual = unox.get_sample_data(**params)
    expected = 'sample_data/stage1/y/Y_2019.npy'
    assert actual == expected, f"Expected {expected}, but got {actual}"
    
    # Test with invalid parameters
    invalid_params = [{'stage': 3, 'x_or_y': 'y', 'year': 2019},
                      {'stage': 1, 'x_or_y': 'z', 'year': 2019},
                      {'stage': 1, 'x_or_y': 'y', 'year': -1}]
    for params in invalid_params:
        try:
            unox.get_sample_data(**params)
        except (ValueError, FileNotFoundError) as e:
            assert True, f"get_sample_data raised an exception on invalid parameters {params}: {e}"
        else:
            assert False, f"get_sample_data did not raise an exception on invalid parameters {params}"

def test_get_pred_data():
    """Test the get_pred_data function."""
    # Test with valid parameters
    params = {'stage': 1, 'HPC_run': 'test_unet_601760', 'year': 2019}
    actual = unox.get_pred_data(**params)
    expected = 'HPC_runs/test_unet_601760/stage1_output/pred_X_2019.npy'
    assert actual == expected, f"Expected {expected}, but got {actual}"
    
    # Test with invalid parameters
    invalid_params = [{'stage': 3, 'HPC_run': 'test_unet_601760', 'year': 2019},
                      {'stage': 1, 'HPC_run': '', 'year': 2019},
                      {'stage': 1, 'HPC_run': 'test_unet_601760', 'year': -1}]
    for params in invalid_params:
        try:
            unox.get_pred_data(**params)
        except (ValueError, FileNotFoundError) as e:
            assert True, f"get_pred_data raised an exception on invalid parameters {params}: {e}"
        else:
            assert False, f"get_pred_data did not raise an exception on invalid parameters {params}"
