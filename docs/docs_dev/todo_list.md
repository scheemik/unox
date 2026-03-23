<a id='top'></a>
# To-do List

This describes the parts of the code under development, the goals for implementing new features, bugs to be fixed, and elements to optimize. 
The sections below should be expected to be constantly changing. 
If a particular point becomes resolved, it should be deleted from this document and moved to a relevant location.

## Contents

- [Features](#feat)
    - [Regularization](#reg)
        - Implementing a regularizer
        - Update examples that I use in the Analysis and Example notebooks to use regularizers
            - Include more documentation to show the difference between using a regularizer or not (perhaps in a section about ensemble runs?)
    - Generating input files
        - Can I do this not by year? I would like to be able to specify the start and end date, to allow for more granular control of what time span the input files cover.
        - Generating the CO input files
            - Look into the `cdo` command line tool's usage in `merge_CO.sh` and how it is used to merge a bunch of daily HEMCO files
            - See: https://code.mpimet.mpg.de/projects/cdo/wiki/Cdo#Documentation
- [Documentation](#docs)
    - Installation and setup
        - Configuring the test environment
            - Need to show how to set up and run tests that I've made in the `tests` directory
        - Generating / copying the ERA5 files
            - Am I currently having the `input.py` functions pull from Evelyn's directory? Make sure I document where the files are that are being used by default. 
        - Generating CO input files
            - Document how to change the `**kwargs` given to the `input.py` functions to create input files for other than NOx.
        - References to `Workflow` in a lot of the setup documentation should probably actually reference `run_model`
    - Documenting how to update the documentation
        - How did I set up the way it auto updates?
        - Links between internal pages.
        - Auto API and why writing good docstrings is important.
    - Documentation of stuff I've figured out, kinda like some results?
        - Results of using a regularizer
        - Results from running ZFI across the different input variables
        - Results from investigating the match outside where input values of `nox` are available
            - Do the spatial patterns of `nox_pred` match up with the spatial patterns of `no2`?
- To be categorized
    - Explaining `**kwargs` and how they're used in functions.
    - `input_metadata.json` files, created only just to be able to look more easily, not to be used by code.
    - Scale factors in input files: when are they applied? Upon creating input file or upon plotting?
        - Should we be shifting just the mean of the values? Or also the standard deviation?
    - `plot_var_maps()` bug in choosing the start and end date for averaging over, the title is wrong.
    - Emphasize that changing part of `unox` requires restarting the kernel when testing new plotting functions in a jupyter notebook.
    - Explaining ensemble runs
        - Will this be either:
            - A jupyter notebook, in which case I would need to add an example prediction set that is an ensemble run
            - A markdown file, in which case I would need to figure out a system for adding images so I can show plots. I might need to do that anyway if I want to have some explanation of results
        - The following sections should take an example ensemble and show how I would run it
        - How to submit the jobs
        - How do they interact with ZFI sweeps?
        - Need to wait until all members (which run as separate jobs) complete
        - Bringing them to Animus automatically consolidates the outputs to one `.nc` file
        - Plotting one ensemble member for maps and correlation plots
        - Plotting box and whisker plots
            - All the different variations
    - ZFI runs
        - Don't actually use the `zfi_vars` attribute of configuration `.json` files


---
<a id='feat'></a>
[back to top](#top)

## Features

Notes on the new features I am developing in the code.

<a id='reg'></a>
[back to top](#top)

### Regularization

My hope is that, by implementing a regularizer in the u-net model, I will be able to reduce the erroneous non-zero values that are predicted over the ocean for NO2. 

#### Implementing a regularizer

I have started implementing a regularizer, adding it to the `build_Unet()` function in `src/unox/HPC/model/core.py`.
There are many things to consider about the implementation.
You can add a regularizer to each individual layer, including these types:
- `Conv2D`
- `LSTM`
- `Conv2DTranspose`

You cannot add a regularizer to the `MaxPooling` layer type. 
The following layer types have `**kwargs`, which means they could accept a regularizer, but probably doesn't make sense for them to:
- `Permute`
- `Reshape`
- `Lambda`
- `concatenate`

The [`keras.regularizers` source code](https://github.com/keras-team/keras/blob/v3.13.2/keras/src/regularizers/regularizers.py#L213) lists four pre-made regularizers:
- `L1L2`
- `L1`
- `L2`
- `OrthogonalRegularizer`

It also leaves the possibility of defining a custom regularizer. 
Each of these regularizers takes in a `float` parameter which is the "regularization factor." 
In examples, I see most often this is a value like `0.01` or `0.03`, but I've also seen up to `2.0`. 

This means there are many different parameters and combinations to try to see the effect:
- Which of the layers do I add a regularizer to?
- Do I add the same regularizer to each layer?
- Do I use different regularization factors for each layer?

To keep things simple, I'm starting off by using the same regularizer in all layers that accept one, all with the same regularization factor. 

So far, I've used the `L1` regularizer with the following factors:
- 0.01
- 1e-05

All of them have resulted in predictions that appear completely blank on the comparison maps.

I've sent in jobs using the `L1` regularizer with the following factors:
- 0.0
- 1.0
- 0.0000001
- 0.00000001
- 0.000000001
- 0.0000000001

Once those complete, I will evaluate whether they made a noticeable difference in the predictions.

---
<a id='docs'></a>
[back to top](#top)

## Documentation

### Documenting how to update the documentation

I have the `docs_dev/write_docs.md` file where I am trying to document how I update these docs.

