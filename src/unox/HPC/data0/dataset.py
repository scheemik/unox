import xarray as xr
import numpy as np
import pandas as pd
import json
import warnings

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
        name : `str`
            The name of the dataset, matching the string given to load the dataset, if applicable.
        xr : `xr.Dataset` or `xr.DataArray`
            The xarray dataset. Expected to have lat and lon coordinates, and optionally 
            a time coordinate.
        years : list of `int`
            A list of unique years present in the time coordinate of the dataset.
        metadata_file : `str`
            The file path to the metadata file for the dataset, if it is an input or prediction set.
        metadata : `dict`
            A dictionary of metadata for the dataset, coming from `metadata_file`.
        epochs_logs : `xr.Dataset`
            An xarray Dataset of the epochs logs for the dataset, if it is a prediction set.
        is_input_set : `bool`
            Whether the dataset is an input set. If this is `True`, then `is_predict` must be `False`.
        is_predict : `bool`
            Whether the dataset is a prediction set. If this is `True`, then `is_input_set` must be `False`.
        is_ensemble : `bool`
            Whether the dataset has ensemble members. Only applicable for prediction sets.

        Methods
        -------
        _verify(**kwargs)
            Verify specified aspects of the dataset using `verify_dataset()`.
        _get_years()
            Get a list of unique years present in the time coordinate of the dataset using `get_years()`.
        _select_year(year)
            Select data for the specified year from the dataset.
        _get_metadata()
            Get the metadata dictionary if the dataset is an input or prediction set using `get_metadata()`.
        _get_epochs_logs()
            Get the epochs csv logs if the dataset is a prediction set using `get_epochs_logs()`.
        _shift_lons(**kwargs)
            Shift the longitude coordinates of the dataset using `shift_lon_arr()`.

    """
    # Initialize the uarray object
    def __init__(self, 
        dataset, 
        is_input_set=False,
        is_predict=False,
        **kwargs,
    ):
        # If a `uarray` object is passed `dataset`, copy all attributes
        if isinstance(dataset, uarray):
            self.name = dataset.name
            self.xr = dataset.xr 
            self.years = dataset.years
            self.metadata_file = dataset.metadata_file
            self.metadata = dataset.metadata
            self.epochs_logs = dataset.epochs_logs 
            self.is_input_set = dataset.is_input_set
            self.is_predict = dataset.is_predict
            self.is_ensemble = dataset.is_ensemble
        else:
            self.xr = get_dataset(
                dataset, 
                is_input_set,
                is_predict,
                **kwargs,
            )
            # Define other attributes, which are filled later by methods
            self.years = None
            self.metadata = None
            self.epochs_logs = None
            self.is_ensemble = None
            # Add name if `dataset` is a string
            if isinstance(dataset, str):
                self.name = dataset
                # Set input / prediction attributes
                if is_input_set:
                    try:
                        self.metadata_file = verify_path(f'inputfiles/{dataset}/input_metadata.json')
                    except:
                        self.metadata_file = verify_path(f'inputfiles/{dataset}/{dataset}.json')
                    self.is_input_set = True
                    self.is_predict = False
                    self.is_ensemble = False
                elif is_predict:
                    self.metadata_file = verify_path(f'HPC_runs/{dataset}/predictions_metadata.json')
                    self.is_input_set = False
                    self.is_predict = True
                else:
                    self.metadata_file = None
                    self.is_input_set = False
                    self.is_predict = False
            else:
                self.name = 'xarray dataset'
                self.metadata_file = None
                self.is_input_set = False
                self.is_predict = False
    # Verify aspects of the dataset
    def _verify(self, **kwargs):
        self.xr = verify_dataset(self.xr, **kwargs)
    def _is_ensemble(self):
        self.is_ensemble = is_ensemble(self)
        return self.is_ensemble
    # Get aspects of the dataset
    def _get_years(self):
        # Check whether years have already been computed
        if isinstance(self.years, type(None)):
            # Get the years
            ## Note: this also verifies the dataset time coordinate
            self.years = get_years(self.xr)
        return self.years
    def _select_year(self, year):
        # Ensure that the dataset has a time coordinate
        self._verify(check_time=True)
        # Get just the data for the specified year
        return self.xr.sel(time=slice(f"{year}-01-01", f"{year}-12-31"))
    def _get_metadata(self):
        # Check whether metadata has already been loaded
        if isinstance(self.metadata, type(None)):
            # Get the metadata dictionary
            self.metadata = get_metadata(self)
        return self.metadata
    def _get_epochs_logs(self):
        # Check whether the epochs logs have already been loaded
        if isinstance(self.epochs_logs, type(None)):
            # Get the epochs logs
            self.epochs_logs = get_epochs_logs(self)
        return self.epochs_logs
    # Modify aspects of the dataset
    def _shift_lons(self, **kwargs):
        self.xr = shift_lon_arr(self.xr, **kwargs)

def get_dataset(
    dataset,
    is_input_set=False,
    is_predict=False,
    **kwargs,
):
    """ Get the given dataset.

        Parameters
        ----------
        dataset : `str`, `uarray`, `xarray.Dataset`, `xarray.DataArray`
            The name of the dataset to get.
        is_input_set : `bool`, optional
            If True, treat the dataset as an input set.
        is_predict : `bool`, optional
            If True, treat the dataset as a model output prediction set.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to `load_dataset()` and `verify_dataset()`.

        Returns
        -------
        xr_dataset : `xarray.Dataset` or `xarray.DataArray`
            The loaded and verified xarray dataset.
    """
    # If dataset is a string, load the dataset
    if isinstance(dataset, str):
        if is_input_set:
            # Check whether a file path in the `inputfiles` directory was given
            if 'inputfiles/' not in dataset:
                # Assemble the file path
                file_path = f'inputfiles/{dataset}/{dataset}.nc'
        elif is_predict:
            # Check whether a file path in the `HPC_runs` directory was given
            if 'HPC_runs/' not in dataset:
                # Assemble the file path
                file_path = f'HPC_runs/{dataset}/predictions.nc'
        else:
            file_path = dataset
        # Load (and verify) the dataset
        xr_dataset = load_dataset(file_path, **kwargs)
    # If dataset is a xarray Dataset or DataArray, verify it
    elif isinstance(dataset, xr.Dataset) or isinstance(dataset, xr.DataArray):
        xr_dataset = verify_dataset(dataset, **kwargs)
    # If dataset is already a uarray, return it
    elif isinstance(dataset, uarray):
        return dataset.xr
    else:
        raise TypeError(f"(get_dataset) `dataset` must be string, xr.Dataset, or xr.DataArray. Got {type(dataset)}.")
    return xr_dataset

def load_dataset(
    file_path,
    **kwargs,
):
    """ Load the data from the given filepath into an xarray dataset.

        Verifies the given filepath, ensures the file contains an applicable format, and loads the data into an xarray dataset.

        Parameters
        ----------
        file_path : `str`
            The filepath to the data file to load.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to `csv_to_xr()` and `verify_dataset()`.

        Returns
        -------
        xr_dataset : `xarray.Dataset` or `xarray.DataArray`
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
    **kwargs,
):
    """ Load a CSV file into a pandas DataFrame.

        Loads a CSV file into a pandas DataFrame, ensuring that the required columns are present if the file is from the US EPA.

        Parameters
        ----------
        csv_filepath : `str`
            The path to the CSV file to load.
        is_US_EPA : `bool`, optional
            If True, verify that the CSV file has the required columns
            for US EPA data. Defaults to True.
        **kwargs : keyword arguments
            Additional keyword arguments to accommodate wrapper functions.

        Returns
        -------
        df : `pandas.DataFrame`
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
    **kwargs,
):
    """ Load a CSV file into an xarray Dataset.

        Load a CSV file into an xarray Dataset, ensuring that the required columns are present if the file is from the US EPA.

        Parameters
        ----------
        csv_filepath : `str`
            The path to the CSV file to load.
        is_US_EPA : `bool`, optional
            If True, verify that the CSV file has the required columns
            for US EPA data. Defaults to True.
        **kwargs : keyword arguments
            Additional keyword arguments to accommodate wrapper functions.

        Returns
        -------
        xr_dataset : `xarray.Dataset`
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
    """ Get the US EPA species name from the ID.

        Map the US EPA species ID to the corresponding species name.

        Parameters
        ----------
        ID : `str`
            The US EPA species ID to map.

        Returns
        -------
        species_name : `str`
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
    """ Get the years present in the dataset.
    
        Get a list of unique years from the time coordinate of the given dataset.

        Parameters
        ----------
        dataset : `str`, `uarray`, `xarray.Dataset`, `xarray.DataArray`
            The dataset from which to extract the years.

        Returns
        -------
        years : `list` of `int`
            A list of unique years in the dataset.
    """
    # Verify argument types
    if isinstance(dataset, xr.Dataset) or isinstance(dataset, xr.DataArray):
        xr_dataset = verify_dataset(dataset, check_time=True)
    elif isinstance(dataset, str):
        xr_dataset = load_dataset(dataset, check_time=True)
    elif isinstance(dataset, uarray):
        xr_dataset = verify_dataset(dataset.xr, check_time=True)
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

def get_metadata(
    this_uarr,
):
    """ Find and load the relevant metadata dictionary for the given uarray.

        Parameters
        ----------
        this_uarr : `uarray`
            The uarray object for which to load the metadata.

        Returns
        -------
        metadata : `dict`
            The metadata dictionary for this uarray.
    """
    # Verify argument types
    if not isinstance(this_uarr, uarray):
        raise TypeError(f"(get_metadata) `this_uarr` must be a uarray. Got type: {type(this_uarr)}.")

    # Check whether the uarray is an input or prediction set
    if this_uarr.is_input_set and this_uarr.is_predict:
        raise ValueError(f"(get_metadata) `uarray` cannot be both an input set and a prediction set.")
    elif this_uarr.is_input_set or this_uarr.is_predict:
        # Verify the path to the metadata file
        this_uarr.metadata_file = verify_path(this_uarr.metadata_file)
        # Load metadata file as a dictionary
        with open(this_uarr.metadata_file, 'r') as f:
            metadata = json.load(f)
        return metadata
    else:
        raise ValueError(f"(get_metadata) `uarray` must be either an input set or a prediction set to load metadata.")

def is_ensemble(
    dataset,
    **kwargs,
):
    """ Check whether the given dataset has ensemble members.

        Parameters
        ----------
        dataset : `str`, `uarray`, `xarray.Dataset`, `xarray.DataArray`
            The name of the dataset to get.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to `load_dataset()` and `verify_dataset()`.

        Returns
        -------
        is_ensemble : `bool`
            Whether the given dataset has ensemble members.
    """
    # Verify argument types
    # Making `uarray` object verifies `dataset`
    if not isinstance(dataset, uarray):
        dataset = uarray(dataset, **kwargs)
    # Check whether the dataset is a prediction set
    if not dataset.is_predict:
        warnings.warn(f"(is_ensemble) `dataset` must be a prediction set to check for ensemble members.")
        return False
    # Check for the `ensemble_size` attribute
    g_attrs = dataset.xr.attrs
    if 'ensemble_size' in g_attrs:
        ensemble_size = g_attrs['ensemble_size']
        if isinstance(ensemble_size, (int, np.int64)) and ensemble_size > 1:
            return True
    return False

def get_epochs_logs(
    dataset,
    **kwargs,
):
    """ Find and load the relevant epochs csv logs for the given `uarray`.

        Parameters
        ----------
        dataset : `uarray`
            The `uarray` object for which to load the epochs logs.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to `uarray()`.

        Returns
        -------
        epochs_logs : `xr.Dataset`
            The dataset of epochs logs for this `uarray`.
    """
    # Verify argument types
    # Making `uarray` object verifies `dataset`
    if not isinstance(dataset, uarray):
        dataset = uarray(dataset, **kwargs)
    # Check whether the dataset is a prediction set
    if not dataset.is_predict:
        ValueError(f"(get_epochs_logs) `dataset` must be a prediction set to load epochs logs.")

    # Get the stages of this prediction set
    stages = dataset.xr.attrs['stages']
    # Make a blank list to add each stage of epoch logs
    logs_per_stage = []
    # Loop across the stages
    for stage in stages:
        # Format the path to the epoch log CSV file
        this_csv = f"HPC_runs/{dataset.name}/unet_stage{stage}_log.csv"
        # Verify that this file exists
        this_csv = verify_path(this_csv)
        # Load the CSV into a Pandas Data Frame
        this_df = pd.read_csv(this_csv, delimiter=';')
        # Set `epoch` as the index
        this_df = this_df.set_index('epoch')
        # Turn the Data Frame into a DataArray
        this_xr = this_df.to_xarray()
        # Add that DataArray to the list
        logs_per_stage.append(this_xr)
    
    # Create an xr.Dataset to hold the epochs data
    epochs_log_xr = xr.concat(logs_per_stage, dim="stage", coords="all")
    # Set the values for the `stage` coordinate
    epochs_log_xr.coords['stage'] = stages

    return epochs_log_xr