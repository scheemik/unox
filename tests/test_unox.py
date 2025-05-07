from unox import unox

def test_show_available_data():
    """Test the show_available_data function."""
    expected = ['original_sample_data/stage1/x/X_2005.npy', 
                'original_sample_data/stage1/y/Y_2005.npy', 
                'original_sample_data/stage2/x/X_2014.npy', 
                'original_sample_data/stage2/y/Y_2014.npy']
    actual = unox.show_available_data('original_sample_data/')
    assert actual == expected, f"Expected file list (length {len(expected)}) does not match actual file list (length {len(actual)})"

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