from unox import unox

def test_verify_path():
    """Test the verify_path function."""
    # Test with a valid path
    valid_path = 'original_sample_data/stage1/x/X_2005.npy'
    actual = unox.verify_path(valid_path)
    print(f"Actual path: {actual}")
    assert type(unox.verify_path(valid_path)) == type('str'), f"verify_path failed on valid path: {valid_path}"
    # Test with an invalid path
    invalid_path = 'invalid/path/to/file.npy'
    try:
        unox.verify_path(invalid_path)
    except (FileNotFoundError) as e:
        assert True, f"verify_path raised an exception on invalid path: {e}"
    else:
        assert False, f"verify_path did not raise an exception on invalid path {invalid_path}"

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
