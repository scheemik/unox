def verify_number(
    value,
    ):
    """Verify that the given value is a number.

    If the given value is a number that can be converted to an integer
    but is not a string, character, or bool, return True. 
    Otherwise, return False.

    Parameters
    ----------
    value : any
        The value to verify.

    Returns
    -------
    bool
        True if the value is a number, False otherwise.

    Examples
    --------
    >>> value = verify_number(5)
    True
    >>> value = verify_number("5")
    False
    >>> value = verify_number(np.nan)
    False
    """
    if isinstance(value, str) or isinstance(value, bytes) or isinstance(value, type(True)):
        return False
    try:
        foo = int(value)
        return True
    except:
        return False