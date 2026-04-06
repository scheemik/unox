<a id='top'></a>
# To-do List

This describes the parts of the code under development, the goals for implementing new features, bugs to be fixed, and elements to optimize. 
The sections below should be expected to be constantly changing. 
If a particular point becomes resolved, it should be deleted from this document and moved to a relevant location.

## Items

- Features
    - Regularization
        - Update examples that I use in the Analysis and Example notebooks to use model runs that utilized regularizers
    - Generating input files
        - Can I do this not by year? I would like to be able to specify the start and end date, to allow for more granular control of what time span the input files cover.
        - I made an attempt at this in the defunct / dead branch `refactor_input0`
            - I started by changing the input files, and then couldn't get stage 2 to work, but couldn't figure out where I went wrong
            - That branch still has a bunch of useful bits of code, but should not be used in its entirety
        - Here's the plan:
            - Make a new branch in which to test this functionality
            - Make a new function in `load_input` called `load_input()`
                - Base this off the `get_npy_from_netcdf()`, but implement using date ranges
                - Use arguments `start_date` and `end_date` instead of `year`
            - In `HPC.training.make_predictions()`, use `load_input()`
                - Keep the same structure, that is, going year-by-year
                    - But, now I don't just specify the year, I specify the start and end dates
                - If that works, then try running the predictions over the whole verification period (2019 and 2020) using the `load_input()` with different start and end dates
            - Repeat the above process, replacing `get_npy_from_netcdf()` with `load_input()` in `HPC.data0.run_functions.prepare_input()`
                - Go year-by-year first
                - Then try across the whole time period at once
            - If both of those work, then restructure how I make input files
                - Generate the input files over the whole time period, not year by year
                - Don't use the `noleap` calendar
    - Making time series plots
        - If I can get rid of the `noleap` calendar in both the input file and prediction file data, I should be able to 
- Build
    - Add `dask` package to allow loading multiple files as a dataset using `xarray.open_mfdataset()`
        - See dead branch `refactor_input0` to see how I did that 
        - Make sure to try recreating an environment from scratch following the installation instructions
    - Update the Animus environment from Python 3.9 to Python 3.12
        - The environment on Trillium uses Python 3.12
        - Make a new test environment to try this out first
        - Make sure you can run all the parts of the code including the tests in the new environment
- Documentation
    - Formatting
        - LaTeX formatting
            - When the documentation is in VSCodium, the preview of markdown renders LaTeX syntax between dollar signs `$`
            - However, on Read the Docs, that doesn't get rendered
            - Most of what I'm using that syntax for is to make super script and sub script characters
                - Ex: NOx, R^2, 1x10^{-5}
            - I had made all the changes for this on the `refactor_input0` branch, on [commit abe906b](https://github.com/scheemik/unox/commit/abe906b6f88ac1936847809c1530a500ccaff59e)
                - I would need to look through those changes and make them again in a branch that isn't dead
    - Installation and setup
        - Configuring the test environment
            - Need to show how to set up and run tests that I've made in the `tests` directory
        - Generating / copying the ERA5 files
            - Am I currently having the `input.py` functions pull from Evelyn's directory? Make sure I document where the files are that are being used by default. 
        - Generating CO input files
            - Document how to change the `**kwargs` given to the `input.py` functions to create input files for other than NOx.
            - Look into the `cdo` command line tool's usage in `merge_CO.sh` and how it is used to merge a bunch of daily HEMCO files
            - See: https://code.mpimet.mpg.de/projects/cdo/wiki/Cdo#Documentation
        - References to `Workflow` in a lot of the setup documentation should probably actually reference `run_model`
    - Documenting how to update the documentation
        - How did I set up the way it auto updates?
        - Links between internal pages.
        - Auto API and why writing good docstrings is important.
        - I have the `docs_dev/write_docs.md` file where I am trying to document how I update these docs.
    - Documentation of stuff I've figured out, kinda like some results?
        - Results of using a regularizer
        - Results from running ZFI across the different input variables
        - Results from investigating the match outside where input values of `nox` are available
            - Do the spatial patterns of `nox_pred` match up with the spatial patterns of `no2`?
    - The Example Usage notebook `docs/example.ipynb`
        - I refer to this throughout the documentation, but pretty much all of the code in it is not up to date
        - I think I could rethink this notebook
            - It could be used as a very short, brief demonstration of what the code can do, like the "Basic Analysis" notebook `docs/analysis.ipynb`, but just the flashy stuff to show off.
- Cleaning up the repository
    - There are many items which are probably not needed any more that are in the repository
    - Here are some which I believe could be just deleted, but should probably be reviewed beforehand:
        - All the notebooks in the `analysis_examples/` directory. I believe none of these are still relevant as they were mostly from before I (Mikhail) took over the project
        - The code inside `src/unox/HPC/legacy/` directory. I believe all the functions in there are from when the input / output files were `.npy`
            - Would also need to remove the option to use these functions within `run_model.py`
- To be categorized
    - Explaining `**kwargs` and how they're used in functions.
    - `input_metadata.json` files, created only just to be able to look more easily, not to be used by code.
    - Scale factors in input files: when are they applied? Upon creating input file or upon plotting?
        - Should we be shifting just the mean of the values? Or also the standard deviation?
    - `plot_var_maps()` bug in choosing the start and end date for averaging over, the title is wrong.
    - Emphasize that changing part of `unox` requires restarting the kernel when testing new plotting functions in a jupyter notebook.
    - ZFI runs
        - Don't actually use the `zfi_vars` attribute of configuration `.json` files


