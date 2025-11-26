from unox.HPC.data0.verify_path import verify_path

def test_verify_path():
    """Test the verify_path function."""
    # Test with valid path
    valid_path = 'inputfiles/no2_sample_input/stage1/x/X_2005.npy'
    actual = verify_path(valid_path)
    print(f"Actual path: {actual}")
    assert type(verify_path(valid_path)) == type('str'), f"verify_path failed on valid path: {valid_path}"
    # Test with invalid path
    invalid_path = 'invalid/path/to/file.npy'
    try:
        verify_path(invalid_path)
    except (FileNotFoundError) as e:
        assert True, f"verify_path raised an exception on invalid path: {e}"
    else:
        assert False, f"verify_path did not raise an exception on invalid path {invalid_path}"
    # Test with invalid path
    invalid_path = 12345
    try:
        verify_path(invalid_path)
    except (TypeError) as e:
        assert True, f"verify_path raised an exception on invalid path: {e}"
    else:
        assert False, f"verify_path did not raise an exception on invalid path {invalid_path}"