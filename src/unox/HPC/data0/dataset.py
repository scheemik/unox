import xarray as xr
import pandas as pd

# Necessary to use relative imports (starting with a dot) to avoid
# errors when running on HPC as the `unox` package is not available
from .paths import verify_path
from .verify_dataset import verify_dataset
from .latlon import shift_lon_arr

# Note: Subclassing from xarray is not currently supported
# so here, the xarray is an attribute rather than the parent class
class uarray():
    """A wrapper class for an xarray Dataset.

    A class that wraps an xarray Dataset of a format specified by `verify_dataset()`.
    All method names start with an underscore (_) to avoid conflicts.

    Attributes
    ----------
    xr : xarray.Dataset or xarray.DataArray
        The xarray dataset. Expected to have lat and lon coordinates, and optionally 
        a time coordinate.
    years : list of int
        A list of unique years present in the time coordinate of the dataset.

    Methods
    -------
    _verify(**kwargs)
        Verify specified aspects of the dataset using `verify_dataset()`.
    _get_years()
        Get a list of unique years present in the time coordinate of the dataset.
    _select_year(year)
        Select data for the specified year from the dataset.
    _shift_lons(**kwargs)
        Shift the longitude coordinates of the dataset using `shift_lon_arr()`.

    """
    # Initialize the uarray object
    def __init__(self, xr_array, **kwargs):
        self.xr = get_dataset(xr_array, **kwargs)
        self.years = None
    # Verify aspects of the dataset
    def _verify(self, **kwargs):
        self.xr = verify_dataset(self.xr, **kwargs)
    # Get aspects of the dataset
    def _get_years(self):
        # Check whether years have already been computed
        if isinstance(self.years, type(None)):
            # Get the years
            ## Note: this also verifies the dataset time coordinate
            self.years = get_years(self.xr)
        return self.years
    def _select_year(self, year):
        self._verify(check_time=True)
        return self.xr.sel(time=slice(f"{year}-01-01", f"{year}-12-31"))
    # Modify aspects of the dataset
    def _shift_lons(self, **kwargs):
        self.xr = shift_lon_arr(self.xr, **kwargs)

def get_dataset(
    set_to_get,
    is_input_set=False,
    is_predict=False,
    **kwargs,
):
    """Get the given dataset.

    Parameters
    ----------
    set_to_get : str
        The name of the dataset to get.
    is_input_set : bool, optional
        If True, treat the dataset as an input set.
    is_predict : bool, optional
        If True, treat the dataset as a model output prediction set.
    **kwargs : keyword arguments

    Returns
    -------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The loaded and verified xarray dataset.
    """
    # If set_to_get is a string, load the dataset
    if isinstance(set_to_get, str):
        if is_input_set:
            # Check whether a file path in the `inputfiles` directory was given
            if 'inputfiles/' not in set_to_get:
                # Assemble the file path
                file_path = f'inputfiles/{set_to_get}/{set_to_get}.nc'
        elif is_predict:
            # Check whether a file path in the `HPC_runs` directory was given
            if 'HPC_runs/' not in set_to_get:
                # Assemble the file path
                file_path = f'HPC_runs/{set_to_get}/predictions.nc'
        else:
            file_path = set_to_get
        # Load (and verify) the dataset
        xr_dataset = load_dataset(file_path, **kwargs)
    # If set_to_get is a xarray Dataset or DataArray, verify it
    elif isinstance(set_to_get, xr.Dataset) or isinstance(set_to_get, xr.DataArray):
        xr_dataset = verify_dataset(set_to_get, **kwargs)
    else:
        raise TypeError(f"(get_dataset) `set_to_get` must be string, xr.Dataset, or xr.DataArray. Got {type(set_to_get)}.")
    return xr_dataset

def load_dataset(
    file_path,
    **kwargs,
):
    """Load the data from the given filepath into an xarray dataset.

    Verifies the given filepath, ensures the file contains an applicable format,
    and loads the data into an xarray dataset.

    Parameters
    ----------
    file_path : str
        The filepath to the data file to load.
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `csv_to_xr()` and `verify_dataset()`.

    Returns
    -------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The loaded xarray dataset.
    """
    # Verify the filepath
    file_path = verify_path(file_path)
    # If it is a csv, use custom function to load
    if file_path.endswith('.csv'):
        xr_dataset = csv_to_xr(file_path, **kwargs)
    else:
        xr_dataset = xr.open_dataset(file_path)
    # Verify the dataset
    xr_dataset = verify_dataset(xr_dataset, **kwargs)
    return xr_dataset

def csv_to_pd(
    csv_filepath,
    is_US_EPA=True,
):
    """Load a CSV file into a pandas DataFrame.

    Loads a CSV file into a pandas DataFrame, ensuring that the
    required columns are present if the file is from the US EPA.

    Parameters
    ----------
    csv_filepath : str
        The path to the CSV file to load.
    is_US_EPA : bool, optional
        If True, verify that the CSV file has the required columns
        for US EPA data. Defaults to True.

    Returns
    -------
    df : pandas.DataFrame
        The loaded DataFrame.

    Examples
    --------
    >>> df = csv_to_pd('datafiles/US_EPA/daily_42602_2019.csv')
    >>> df.head()   
                Latitude	Longitude	Arithmetic Mean
    Date			
    2019-01-01	33.553056	-86.815	    4.314286
    2019-01-08	33.553056	-86.815	    6.263636
    2019-01-09	33.553056	-86.815	    4.957143
    2019-01-10	33.553056	-86.815	    5.891667
    2019-01-11	33.553056	-86.815	    14.500000
    """
    # Verify the filepath
    csv_filepath = verify_path(csv_filepath)
    # Verify the file is a CSV
    if not csv_filepath.lower().endswith('.csv'):
        raise ValueError(f"(csv_to_pd) File at `csv_filepath` must be a CSV. Got: {csv_filepath}")
    # If it is from the US EPA
    if is_US_EPA:
        try:
            df = pd.read_csv(csv_filepath, parse_dates={'Date':['Date Local']}, index_col=['Date'], usecols=['Date Local', 'Latitude', 'Longitude', 'Arithmetic Mean'])
            # Rename 'Arithmetic Mean' to match the US EPA species ID name
            ## Get the ID from the file path
            file_name = csv_filepath.split('/')[-1]
            species_id = file_name.split('_')[1]
            ## Get the species name
            species_name = get_US_EPA_species_name(species_id)
            ## Rename the 'Arithmetic Mean' column
            df.rename(columns={'Arithmetic Mean': species_name}, inplace=True)
        except Exception as e:
            raise ValueError(f"(csv_to_pd) Error loading US EPA CSV file: {e}. Ensure the file has the required columns: 'Date Local', 'Latitude', 'Longitude', 'Arithmetic Mean'.")
    else:
        try:
            df = pd.read_csv(csv_filepath)
        except Exception as e:
            raise ValueError(f"(csv_to_pd) Error loading CSV file: {e}.")
    return df

def csv_to_xr(
    csv_filepath,
    is_US_EPA=True,
):
    """Load a CSV file into an xarray Dataset.

    Loads a CSV file into an xarray Dataset, ensuring that the
    required columns are present if the file is from the US EPA.

    Parameters
    ----------
    csv_filepath : str
        The path to the CSV file to load.
    is_US_EPA : bool, optional
        If True, verify that the CSV file has the required columns
        for US EPA data. Defaults to True.

    Returns
    -------
    xr_dataset : xarray.Dataset
        The loaded Dataset.

    Examples
    --------
    >>> xr_dataset = csv_to_xr('datafiles/US_EPA/daily_42602_2019.csv')
    >>> xr_dataset
    """
    # Load the CSV into a pandas DataFrame
    df = csv_to_pd(csv_filepath, is_US_EPA)
    # Convert the DataFrame to an xarray Dataset
    xr_dataset = df.to_xarray()
    # If it is from the US EPA, set the coordinates
    if is_US_EPA:
        xr_dataset = xr_dataset.set_coords(['Latitude', 'Longitude'])
        xr_dataset = verify_dataset(xr_dataset, shift_lons=False)
    return xr_dataset

def get_US_EPA_species_name(
    ID
):
    """Get the US EPA species name from the ID.

    Maps the US EPA species ID to the corresponding species name.

    Parameters
    ----------
    ID : str
        The US EPA species ID to map.

    Returns
    -------
    species_name : str
        The corresponding US EPA species name.

    Examples
    --------
    >>> species_name = get_US_EPA_species_name('42602')
    'no2'
    >>> species_name = get_US_EPA_species_name('42101')
    'co'
    """
    # Define a mapping of US EPA species IDs to species names
    species_mapping = {
        # Criteria gases
        '44201': 'o3',
        '42401': 'so2',
        '42101': 'co',
        '42602': 'no2',
        # Particulate matter
        '88101': 'pm25',
        '88502': 'pm25n',
        '81102': 'pm10',
        '86101': 'pmc',
        'SPEC': 'pm25spec',
        'PM10SPEC': 'pm10spec',
        # Meteorological
        'WIND': 'wind',
        'TEMP': 'temp',
        'PRESS': 'press',
        'RH_DP': 'rh_and_dp',
        # Toxics, Precursors, and Lead
        'HAPS': 'haps',
        'VOCS': 'vocs',
        'NONOxNOy': 'nonoxnoy',
        'LEAD': 'lead',
    }
    # Check if the ID is in the mapping
    if ID in species_mapping:
        return species_mapping[ID]
    else:
        raise ValueError(f"(get_US_EPA_species_name) Invalid US EPA species ID: {ID}.")

def get_years(
    dataset,
):
    """Get a list of unique years from the time coordinate of the given dataset.

    Parameters
    ----------
    dataset : xarray.Dataset, xarray.DataArray
        The dataset from which to extract the years.

    Returns
    -------
    years : list of int
        A list of unique years in the dataset.
    """
    # Verify argument types
    if isinstance(dataset, xr.Dataset) or isinstance(dataset, xr.DataArray):
        xr_dataset = verify_dataset(dataset, check_time=True)
    else:
        raise TypeError(f"(get_years) `dataset` must be an xarray Dataset or DataArray. Got type: {type(dataset)}.")
    # Get a list of years present in the dataset
    years = xr_dataset['time'].dt.year.values
    # Sort and get unique years
    years = sorted(list(set(years)))
    # Convert years to list of ints
    ## to avoid TypeError: Object of type int64 is not JSON serializable
    years = [int(year) for year in years]
    return years