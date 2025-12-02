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
    os.makedirs(temp_dir, exist_ok=True)
    with open(f"{temp_dir}/file1.txt", 'w') as f:
        f.write('This is a test file.')
    os.makedirs(f"{temp_dir}/subdir", exist_ok=True)
    with open(f"{temp_dir}/subdir/file2.txt", 'w') as f:
        f.write('This is another test file.')
    
    # Remove the non-empty directory
    upath.remove_non_empty_directory(temp_dir)
    
    # Check if the directory has been removed
    assert not os.path.exists(temp_dir), f"Directory {temp_dir} was not removed."
    
    # Test with a non-directory path
    try:
        upath.remove_non_empty_directory('file1.txt')
    except FileNotFoundError as e:
        assert True, f"remove_non_empty_directory raised an exception on non-directory path: {e}"
    else:
        assert False, "remove_non_empty_directory did not raise an exception on non-directory path."

def test_make_file_path():
    """Test the make_file_path function."""
    # Test with valid input
    valid_path = 'test_make_file_path/path/to/file.txt'
    actual = upath.make_file_path(valid_path)
    expected = 'test_make_file_path/path/to'
    assert actual == expected, f"Expected {expected}, but got {actual}"
    # Delete the created directory for cleanup
    base_dir = valid_path.split('/')[0]
    upath.remove_non_empty_directory(base_dir)
    # Test with valid input that already exists
    # Remove everything after the second to last `/` in the valid path
    partial_path = f"/".join(valid_path.split('/')[:-2])
    print(f"Partial path: {partial_path}")
    print(f"Valid path: {valid_path}")
    os.makedirs(partial_path)
    actual = upath.make_file_path(valid_path)
    assert actual == expected, f"Expected {expected}, but got {actual}"
    # Delete the created directory for cleanup
    upath.remove_non_empty_directory(base_dir)
    # Test with invalid input
    invalid_path = 12345
    try:
        upath.make_file_path(invalid_path)
    except (TypeError) as e:
        assert True, f"make_file_path raised an exception on invalid input: {e}"
    else:
        assert False, f"make_file_path did not raise an exception on invalid input {invalid_path}"