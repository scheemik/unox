import json

from .paths import verify_path

def get_config(
    config_file
):
    """Load the configuration from a JSON file.

        Parameters
        ----------
        config_file : str or dict
            The name or path to the configuration JSON file, 
            or a dictionary in the format of a configuration file.

        Returns
        -------
        config_dict : dict
            The configuration as a dictionary.
    """
    # Verify argument types
    if isinstance(config_file, dict):
        return config_file
    elif isinstance(config_file, str):
        # Check whether that path exists
        try:
            config_path = verify_path(config_file)
        except:
            config_path = f"inputfiles/_input_configs/{config_file}.json"
            try:
                config_path = verify_path(config_path)
            except:
                raise FileNotFoundError(f"(get_config) No file found at {config_file} or {config_path}.")
        # Load the config file
        with open(f"{config_path}", 'r') as file:
            config_dict = json.load(file)
            return config_dict
    else:
        raise TypeError(f"(get_config) `config_file` must be a string or dictionary. Got type: {type(config_file)}.")