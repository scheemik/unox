<a id='top'></a>
# Running the model

The documentation below describes how to run the U-net model and retrieve the results. 
This guide assumes you have followed the instructions on the {doc}`Installation <installation>` and {doc}`Data <data>` pages.
<!-- Note: for linking between documents, use the `doc` role defined in the [Sphinx documentation](https://docs.readthedocs.com/platform/stable/guides/cross-referencing-with-sphinx.html#the-doc-role). 
TLDR: Create a link to a different document by typing `{doc}`, followed by the name of the file surrounded by backticks, excluding the extension. If you would like to change the rendered text of the link, surround the desired link text in backticks, then add the name of the file in angle brackets, in the format: "{doc}`Click here <filename>`".  -->

## Contents

- [Introduction](#intro)
- [Preparing a model run](#prep_model_run)
    - [From Animus to HPC](#from_animus_to_HPC)
    - [Input configuration files](#config_files)

---
<a id='intro'></a>
[back to top](#top)

## Introduction

As was mentioned under "Creating virtual environments" on the {doc}`Installation <installation>` page, the two remote machines, Trillium and Animus, are used for different parts of this project. 
Trillium has GPU resources which allow the U-net model to run quickly and efficiently. 
However, as Trillium is an Alliance Canada system, it can make it fairly restrictive and difficult to perform plotting and analysis tasks. 
Therefore, after running the model on Trillium, I transfer the output to Animus to do the analysis.
Animus also holds the data used to create the inputs for the model. 
Generally, I use Animus for all tasks related to this project except for running the model itself. 

This guide details how to prepare a model run on Animus, transfer that preparation to Trillium and run the model, then transfer the model output back to Animus. 
A demonstration of how to use the analysis tools can be found in the {doc}`Example usage <example>`.

---
<a id='prep_model_run'></a>
[back to top](#top)

## Preparing a model run

The preparation for a model run starts on Animus. 
In principle, you could use your local machine, avoiding Animus all together. 
However, in order to do so, you would need to download the relevant data and some are currently not publicly available.

<a id='from_animus_to_HPC'></a>
[back to top](#top)

### From Animus to HPC

The process of creating an input netCDF is explained on the {doc}`Data <data>` page. 
Below is an explanation of the command used to transfer input files from Animus to HPC. 
You only need to do this once per different input file.
If you plan on running many jobs with the same input file, you do not need to repeat this step every time.

The script `HPC_from_animus.sh` is set up to facilitate the transfer so you do not need to remember how to format a `scp` command and works by taking in the following arguments:
- `-f`: Filename
    - The name of the file to transfer.
    - Can be used individually, adding a `-f` flag for each file to transfer.
- `-i`: Inputfile
    - If specified, it will look for an input file with the name given in the `-f` flag.
    - This flag does not accept any input, it is just a binary.
- `-c`: Cluster
    - The name of the cluster to transfer to, the default being `trillium`.

Here is an example of transferring the `no2_sample_input` input file from Animus to Trillium:

```console
username@animus-c:~/unox$ bash HPC_from_animus.sh -f no2_sample_input -i 
-c, No cluster specified, defaulting to trillium
-i, Copying full input file directory for no2_sample_input to trillium from Animus
Enter passphrase for key '/home/<username>/.ssh/<GH_id>': 
(<username>@trillium.alliancecan.ca) Duo two-factor login for <username>

Enter a passcode or select one of the following options:

 1. Duo Push to <mobile device>

Passcode or option (1-1): 1
Success. Logging you in...
input_metadata.json         100% 1307    90.1KB/s   00:00    
Y_2005.npy                  100%   19MB  24.6MB/s   00:00    
Y_2006.npy                  100%   19MB  61.1MB/s   00:00
...
X_2019.npy                  100%  168MB  84.3MB/s   00:01    
X_2020.npy                  100%  168MB  89.4MB/s   00:01    
no2_sample_input.nc         100% 3882MB  91.9MB/s   00:42
```

Note that the `.npy` files are now deprecated. 

<a id='config_files'></a>
[back to top](#top)

### Input configuration files

The parameters that a model run will use are defined in "input configuration" files. 
These are `.json` files stored in `inputfiles/_input_configs/` and follow the following format:

```json
{
    "input_set": "no2_lsm6",
    "x_vars": [
        "no2",
        "no2_tm1",
        "u10",
        "v10",
        "blh",
        "sp",
        "skt",
        "t2m",
        "ssrd"
    ],
    "stage_2": true,
    "stage_2_cutoff": 2013,
    "lsm_vars": [
    ],
    "grid_size": [35, 46]
}
```

The attributes of this file are explained below:
- `input_set`: The name of the input netCDF to use.
- `x_vars`: The list of variables to use as input to the model.
    - See the {doc}`Data <data>` page for documentation of these variables.
- `stage_2`: A boolean as to whether to run Stage 2 of training.
- `stage_2_cutoff`: The cutoff year for Stage 2 training.
    - Stage 2 training will start the year after the one specified here.
- `lsm_vars`: A list of variables on which to apply the land-sea mask (`lsm`).
- `grid_size`: A list of the number of grid cells to use in latitude and longitude.

When preparing for a model run, make sure the configuration file you wish to use is present on the HPC cluster in the `inputfiles/_input_configs/` directory. 
This can be accomplished by creating a configuration file on Animus, then using the `HPC_from_animus.sh` script to transfer it. 
Or, one can simply create a new configuration file on HPC directly, which is what I usually do.

