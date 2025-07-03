from unox import input as uin
import unox.unox as unox
import numpy as np

def test_make_y_input_file(datadir='/data/high_res/emacdonald/unet/datafiles/t106', 
                           verifydir='inputfiles/',
                           this_year=2019
                           ):
    """Test the make_y_input_file function."""
    # Assemble file path to verification array
    verify_filepath = f"{verifydir}stage1/y/Y_{this_year}.npy"
    # Verify that file path
    verify_filepath = unox.verify_path(verify_filepath)
    # Load the verification array
    verify_array = np.load(verify_filepath)
    # Call the function to create the y input file
    y_data = uin.make_y_input_file(year=this_year, 
                                   var='nox',
                                   datadir=datadir,
                                   fileprefix='nox_',
                                   fileextension='_t106_US.nc',
                                   scale_factor=1e12,
                                   nan_fill=0,
                                   stage_2_cutoff=2022,
                                   outputdir=None
                                   )
    # Verify that the output is a numpy array
    assert isinstance(y_data, np.ndarray), "make_y_input_file did not return a numpy array."
    # Verify that the shape of the output matches the verification array
    assert y_data.shape == verify_array.shape, f"make_y_input_file output shape {y_data.shape} does not match verification array shape {verify_array.shape}"
    # Verify that the output matches the verification array
    assert np.array_equal(y_data, verify_array), f"make_y_input_file output does not match array from {verify_filepath}"