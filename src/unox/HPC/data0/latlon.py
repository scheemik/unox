import xarray as xr
import numpy as np

from .verify_dtype import verify_number

def shift_lon(
    lon_value,
    PM_centered=True,
):
    """ Shift the given longitude value between ranges [0, 360] and [-180, 180].

        If the Prime Meridian is centered and the longitude value is in the range [0, 360], shift it to the range [-180, 180]. 
        If the Prime Meridian is not centered (i.e. the International Date Line is centered) and the longitude value is in the range [-180, 180], shift it to the range [0, 360]. 
        Otherwise, return the same value.
        If the longitude value is not a number or is NaN, or is outside the relevant range for the specified PM_centered, raise a ValueError.

        Parameters
        ----------
        lon_value : `float`
            The longitude value to shift.
        PM_centered : `bool`, optional
            If True, shift the longitude value from the range [0, 360] to [-180, 180].
            If False, shift from [-180, 180] to [0, 360]. Defaults to True.

        Returns
        -------
        lon_value : `float`
            The shifted longitude value.

        Examples
        --------
        >>> lon_value = shift_lon(45.0, PM_centered=True)
        45.0
        >>> lon_value = shift_lon(270.0, PM_centered=True)
        -90.0
        >>> lon_value = shift_lon(-70.0, PM_centered=False)
        290.0
        >>> lon_value = shift_lon(200.0, PM_centered=False)
        200.0
    """
    if not verify_number(lon_value):
        raise ValueError(f"(shift_lon) `lon_value` value must be a number. Got type: {type(lon_value)}")
    if np.isnan(lon_value):
        raise ValueError(f"(shift_lon) `lon_value` value must not be NaN. Got: {lon_value}")
    # Check overall range
    if lon_value < -180 or lon_value > 360:
        raise ValueError(f"(shift_lon) `lon_value` value must be in the range [-180, 360]. Got: {lon_value}.")
    # If using PM-centered convention
    if PM_centered==True:
        # Check if the value is in the range [180, 360]
        if lon_value > 180 and lon_value <= 360:
            # Shift to [-180, 180]
            return (lon_value + 180) % 360 - 180
    # If using IDL-centered convention
    elif PM_centered==False:
        # Check if the value is in the range [-180, 0]
        if lon_value >= -180 and lon_value <= 0:
            # Shift to [0, 360]
            return (lon_value + 360) % 360
    else:
        raise ValueError(f"(shift_lon) `PM_centered` must be True or False. Got: {PM_centered}.")
    return lon_value

def shift_lon_arr(
    in_array,
    **kwargs,
):
    """ Shift the given array of longitude values between ranges [0, 360] and [-180, 180].

        Map the `shift_lon` function to shift each value in the array.

        Parameters
        ----------
        in_array : `numpy.ndarray` or `xarray.Dataset`
            The array of longitude values to shift.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to `shift_lon()`.

        Returns
        -------
        numpy.ndarray or xarray.Dataset
            The shifted longitude values in the range [-180, 180].

        Examples
        --------
        >>> in_array = np.array([0, 90, 180, 270, 360])
        >>> shifted_lon = shift_lon_arr(in_array)
        array([0, 90, 180, -90, 0])

        >>> xarray_dataset.coords['lon'].values
        array([  0.   ,   1.125,   2.25 , ... 357.75 , 358.875], dtype=float32)
        >>> xarray_dataset = shift_lon_arr(xarray_dataset)
        >>> xarray_dataset.coords['lon'].values
        array([  0.   ,   1.125,   2.25 , ...  -2.25 ,  -1.125], dtype=float32)
    """
    # Ensure the input is a numpy array or xarray Dataset
    if isinstance(in_array, np.ndarray):
        lon_array = in_array
    elif isinstance(in_array, xr.Dataset):
        lon_array = in_array.coords['lon']
        lon_attrs = lon_array.attrs
    else:
        raise TypeError(f"(shift_lon_arr) `in_array` must be a numpy.ndarray or xarray.Dataset. Got type: {type(in_array)}")
    # Map the shift_lon function to each element in the array
    shifted_lon = np.vectorize(shift_lon, excluded={1})(lon_array, **kwargs)
    # If it is an xarray Dataset, save the variable attributes
    if isinstance(in_array, xr.Dataset):
        in_array = in_array.assign_coords({'lon':shifted_lon})
        in_array.lon.attrs = lon_attrs
        return in_array
    else:
        return shifted_lon