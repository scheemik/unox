import numpy as np
import xarray as xr
from scipy.stats import linregress

def compare_arrs(
    a_xr_arr,
    b_xr_arr,
    val_type,
    **kwargs,
):
    """ Get a measure of similarity between two arrays.

        If selecting the `'R2'` type: Calculates a correlation between the values of the two given arrays and returns the R^2 value.
        If selecting the `'RMSE'` type: Calculates the root mean square error between the two given arrays and returns the RMSE value.

        Parameters
        ----------
        a_xr_arr : `xarray.DataArray`, `numpy.ndarray`
            The first xarray DataArray or numpy array to compare.
        b_xr_arr : `xarray.DataArray`, `numpy.ndarray`
            The second xarray DataArray or numpy array to compare.
        val_type : `str`
            The type of comparison to perform. Options are `'R2'` for R-squared correlation (default) or `'RMSE'` for root mean squared error.
        **kwargs : keyword arguments
            Additional keyword arguments accepted to facilitate wrapper functions.
        
        Returns
        -------
        comp_value : `float`
            The numeric value comparing the two arrays. Will either be R^2 or RMSE depending on the selected type. 
    """
    # Verify argument types
    if isinstance(a_xr_arr, xr.DataArray):
        a_xr_arr = a_xr_arr.values
    elif not isinstance(a_xr_arr, np.ndarray):
        raise TypeError(f"(compare_arrs) `a_xr_arr` must be an xarray DataArray or numpy array. Got type: {type(a_xr_arr)}")
    if isinstance(b_xr_arr, xr.DataArray):
        b_xr_arr = b_xr_arr.values
    elif not isinstance(b_xr_arr, np.ndarray):
        raise TypeError(f"(compare_arrs) `b_xr_arr` must be an xarray DataArray or numpy array. Got type: {type(b_xr_arr)}")
    if val_type not in ['R2', 'RMSE']:
        raise ValueError(f"(compare_arrs) `val_type` must be either 'R2' or 'RMSE'. Got: {val_type}")

    # Convert the xarray DataArrays to numpy arrays above, 
    # then squeeze and flatten to get one dimensional arrays
    npy_a = np.squeeze(a_xr_arr).flatten()
    npy_b = np.squeeze(b_xr_arr).flatten()
    # Verify these arrays are the same length
    if len(npy_a) != len(npy_b) or len(npy_a) <= 1 or len(npy_b) <= 1:
        raise ValueError(f"(compare_arrs) `a_xr_arr` and `b_xr_arr` must have the same number of elements, <= 1. Got lengths {len(npy_a)} and {len(npy_b)} respectively.")
    # Check which indices, if any, contain NaN values in both arrays
    nan_idx_a = np.argwhere(np.isnan(npy_a))
    nan_idx_b = np.argwhere(np.isnan(npy_b))
    # Check if there are any NaN indices
    if len(nan_idx_a) > 0 or len(nan_idx_b) > 0:
        # Check whether the NaN indices match between the two arrays
        if not np.array_equal(nan_idx_a, nan_idx_b):
            raise ValueError("(compare_arrs) `a_xr_arr` and `b_xr_arr` have mismatched NaN values. Cannot compare arrays with differing NaN indices.")
        # Remove NaN values from both arrays
        npy_a = np.delete(npy_a, nan_idx_a)
        npy_b = np.delete(npy_b, nan_idx_b)
        # Verify these arrays are the same length
        if len(npy_a) <= 1 or len(npy_b) <= 1:
            raise ValueError(f"(compare_arrs) `a_xr_arr` and `b_xr_arr` must both have more than 1 non-NaN value.")

    # Calculate the comparison value
    if val_type == 'R2':
        # Verify that neither array has all the same values
        if np.all(npy_a == npy_a[0]):
            raise ValueError("(compare_arrs) `a_xr_arr` has all the same values. Cannot compute R^2.")
        if np.all(npy_b == npy_b[0]):
            raise ValueError("(compare_arrs) `b_xr_arr` has all the same values. Cannot compute R^2.")
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = linregress(npy_a, npy_b)
        comp_value = r_value**2
    elif val_type == 'RMSE':
        # Calculate the root mean squared error
        comp_value = np.sqrt(np.mean((npy_a - npy_b) **2))
    return comp_value