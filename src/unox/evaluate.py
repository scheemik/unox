import numpy as np
import xarray as xr
from scipy.stats import linregress

def get_corr_R2(
    a_xr_arr,
    b_xr_arr,
    **kwargs,
):
    """ Get the correlation R^2 of two arrays.

        Calculates a correlation between the values of the two given arrays and returns the R^2 value.

        Parameters
        ----------
        a_xr_arr : `xarray.DataArray`, `numpy.ndarray`
            The first xarray DataArray or numpy array to compare.
        b_xr_arr : `xarray.DataArray`, `numpy.ndarray`
            The second xarray DataArray or numpy array to compare.
        **kwargs : keyword arguments
            Additional keyword arguments accepted to facilitate wrapper functions.
        
        Returns
        -------
        R2 : `float`
            The R^2 value of the correlation between the two arrays.
    """
    # Verify argument types
    if isinstance(a_xr_arr, xr.DataArray):
        a_xr_arr = a_xr_arr.values
    elif not isinstance(a_xr_arr, np.ndarray):
        raise TypeError(f"(get_corr_R2) `a_xr_arr` must be an xarray DataArray or numpy array. Got type: {type(a_xr_arr)}")
    if isinstance(b_xr_arr, xr.DataArray):
        b_xr_arr = b_xr_arr.values
    elif not isinstance(b_xr_arr, np.ndarray):
        raise TypeError(f"(get_corr_R2) `b_xr_arr` must be an xarray DataArray or numpy array. Got type: {type(b_xr_arr)}")

    # Convert the xarray DataArrays to numpy arrays above, 
    # then squeeze and flatten to get one dimensional arrays
    npy_a = np.squeeze(a_xr_arr).flatten()
    npy_b = np.squeeze(b_xr_arr).flatten()
    # Verify these arrays are the same length
    if len(npy_a) != len(npy_b) or len(npy_a) <= 1 or len(npy_b) <= 1:
        raise ValueError(f"(plot_comparison) `a_xr_arr` and `b_xr_arr` must have the same number of elements, <= 1. Got lengths {len(npy_a)} and {len(npy_b)} respectively.")
    # Verify that neither array has all the same values
    if np.all(npy_a == npy_a[0]):
        raise ValueError("(get_corr_R2) `a_xr_arr` has all the same values. Cannot compute R^2.")
    if np.all(npy_b == npy_b[0]):
        raise ValueError("(get_corr_R2) `b_xr_arr` has all the same values. Cannot compute R^2.")
    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = linregress(npy_a, npy_b)
    return r_value**2