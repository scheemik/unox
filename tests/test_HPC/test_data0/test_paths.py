import os

import unox.HPC.data0.paths as upath

def test_verify_path():
    """Test the verify_path function."""
    # Test with valid path
    valid_path = 'inputfiles/no2_sample_input/stage1/x/X_2005.npy'
    actual = upath.verify_path(valid_path)
    print(f"Actual path: {actual}")
    assert type(upath.verify_path(valid_path)) == type('str'), f"verify_path failed on valid path: {valid_path}"
    # Test with invalid path
    invalid_path = 'invalid/path/to/file.npy'
    try:
        upath.verify_path(invalid_path)
    except (FileNotFoundError) as e:
        assert True, f"verify_path raised an exception on invalid path: {e}"
    else:
        assert False, f"verify_path did not raise an exception on invalid path {invalid_path}"
    # Test with invalid path
    invalid_path = 12345
    try:
        upath.verify_path(invalid_path)
    except (TypeError) as e:
        assert True, f"verify_path raised an exception on invalid path: {e}"
    else:
        assert False, f"verify_path did not raise an exception on invalid path {invalid_path}"

def test_remove_non_empty_directory():
    """Test the remove_non_empty_directory function."""
    # Create a temporary directory with some files and subdirectories
    temp_dir = 'test_remove_non_empty_directory'
    os.makedirs(temp_dir, exist_ok=False)
    with open(f"{temp_dir}/file1.txt", 'w') as f:
        f.write('This is a test file.')
    os.makedirs(f"{temp_dir}/subdir", exist_ok=False)
    with open(f"{temp_dir}/subdir/file2.txt", 'w') as f:
        f.write('This is another test file.')
    
    # Remove the non-empty directory
    upath.remove_non_empty_directory(temp_dir)
    
    # Check if the directory has been removed
    assert not os.path.exists(temp_dir), f"Directory {temp_dir} was not removed."

    # Create nested directory structure
    nested_dirs = ['a/', 'b/', 'c/', 'd/']
    # Make the nested directories
    full_nested_dirs = ''.join(nested_dirs)
    os.makedirs(full_nested_dirs, exist_ok=False)
    # Remove each directory from the deepest to the top
    dir_to_remove = full_nested_dirs
    for i in range(len(nested_dirs)-1, -1, -1):
        # Remove the deepest directory
        upath.remove_non_empty_directory(dir_to_remove)
        # Confirm that the directory has been removed
        assert not os.path.exists(dir_to_remove), f"Directory {dir_to_remove} was not removed."
        # Set the directory to remove for next iteration
        dir_to_remove = dir_to_remove.replace(nested_dirs[i], '')
        # Confirm the rest of the directory structure exists
        if not i == 0:
            assert os.path.exists(dir_to_remove), f"Directory {dir_to_remove} was removed too soon."
    
    # Test with a non-directory path
    try:
        upath.remove_non_empty_directory('file1.txt')
    except FileNotFoundError as e:
        assert True, f"remove_non_empty_directory raised an exception on non-directory path: {e}"
    else:
        assert False, "remove_non_empty_directory did not raise an exception on non-directory path."

def test_make_file_path():
    """Test the make_file_path function."""
    # Test with valid inputs
    test_cases = [
        {
            'input': 'test_make_file_path/path/to/file.txt',
            'expected': 'test_make_file_path/path/to',
        },
        {
            'input': 'test_make_file_path/path',
            'expected': 'test_make_file_path/path',
        },
        {
            'input': 'test_dir',
            'expected': 'test_dir',
        },
    ]
    for case in test_cases:
        actual = upath.make_file_path(case['input'])
        assert actual == case['expected'], f"Expected {case['expected']}, but got {actual}"
        # Confirm the directory actually exists
        assert os.path.exists(case['expected']), f"Directory {case['expected']} was not found."
        # Clean up by removing the created directory
        base_dir = case['input'].split('/')[0]
        upath.remove_non_empty_directory(base_dir)
    # Test with invalid inputs
    invalid_paths = [
        12345, 
        None,
        True,
        [],
        {},
    ]
    for invalid_path in invalid_paths:
        try:
            upath.make_file_path(invalid_path)
        except (TypeError) as e:
            assert True, f"make_file_path raised an exception on invalid input: {e}"
        else:
            assert False, f"make_file_path did not raise an exception on invalid input {invalid_path}"