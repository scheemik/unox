from unox import unox

def test_show_available_data():
    """Test the show_available_data function."""
    expected = ['../original_sample_data/stage1/x/X_2005.npy', 
                '../original_sample_data/stage1/y/Y_2005.npy', 
                '../original_sample_data/stage2/x/X_2014.npy', 
                '../original_sample_data/stage2/y/Y_2014.npy']
    actual = unox.show_available_data('original_sample_data/')
    assert actual == expected, f"Expected file list (length {len(expected)}) does not match actual file list (length {len(actual)})"