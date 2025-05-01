# unox

Use machine learning to make NOx predictions.

This is an application of the U-net deep learning model for North American NOx emission estimates.

![](model_diagram.png)

## Installation

Installation instructions to be added.
<!-- ```bash
$ pip install unox
``` -->

The following software dependencies are required.

Package     | Version
---------   | -----------
Python      | 3.8.13
TensorFlow  | 2.9.2
CUDA        | 11.4.4
cuDNN       | 8.3.0_11.4
Keras       | 2.9.0

A detailed list of packages installed while while testing and validating the model is provided in `packagelist.txt`.

## Usage

`unox` makes use of the `tensorflow` package to run a U-net deep learning model to make estimates of NOx emissions.

Examples of usage of the code are provided in `test_unet.py`, based on the notebook `example_code.ipynb`. A sample script for running on Mist is `test_unet.sh`.

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

The `unox` package was created by Mikhail Schee. It is licensed under the terms of the MIT license.

## Credits

- The U-net model is based on Tailong He's version for Chinese NOx emissions[^1].
- Initial transition from China region to North America by Evelyn MacDonald.
- The `unox` package was based off the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter) using [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/).

### Source of data

- Training stage 1 involves TCR-2 surface NO2 concentrations and NOx emissions. Both could be found from [the JPL TCR-2 website](https://tes.jpl.nasa.gov/tes/chemical-reanalysis/products/monthly-mean). Last access was on 12 March 2025. 
- Training stage 2 involves *in situ* daily NO2 measurements from the US Environmental Protection Agency (EPA), accessible at https://aqs.epa.gov/aqsweb/airdata/download_files.html. Canadian data will also be needed. 
- Both stages require meteorological fields from ERA5 on [single levels](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview) and on [pressure levels](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels?tab=overview).
- Scripts for downloading ERA5 data and creating Unet input files and more information about the input file format are in the `datafiles/` directory. Data are currently stored on animus-c.

[^1]: He, T.-L.; Jones, D. B. A.; Miyazaki, K; Bowman, K. W.; Jiang, Z.; Chen, X; Li, R.; Zhang, Y; Li, K. [Inverse modeling of Chinese NOx emissions using deep learning: Integrating in situ observations with a satellite-based chemical reanalysis](https://acp.copernicus.org/preprints/acp-2022-251/). *Atmospheric Chemistry and Physics*, 2022. 
Source code is available at https://github.com/tailonghe/Unet_Chinese_NOx.