import numpy as np

import unox.HPC.data0.verify_dtype as vfyd

def test_verify_number():
    """Test the verify_number function."""
    # Test valid number values
    valid_numbers = [0, 1, -1, 1.5, -1.5, 1e-15]
    for num in valid_numbers:
        assert vfyd.verify_number(num) == True, f"verify_number failed on valid number {num}"
    # Test invalid number values
    invalid_numbers = [np.nan, np.inf, -np.inf, '1', 'abc', None, True, False]
    for num in invalid_numbers:
        assert vfyd.verify_number(num) == False, f"verify_number failed on invalid number {num}"
