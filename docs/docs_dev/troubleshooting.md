<a id='top'></a>
# Troubleshooting common errors

## Cannot connect to host in VSCodium

Sometimes the VSCodium server on a remove machine will get corrupted, causing you to be unable to connect to the remote via VSCodium, but you will still be able to log in via terminal just fine.
This can happen when logging out without saving a file or if you lose internet connection suddenly and don't restore it within a few minutes.
I highly recommend closing the remote connection in VSCodium every time you are done working on the remote. 

To fix the corrupted server, log into the remote via terminal and find the `.vscodium-server/` directory.
It is usually in your home directory.
Rename that directory.

```console
username@<remote_machine>:~/$ mv .vscodium-server/ .vscodium-server_old/
```

This will keep the contents of your old setup, just in case. 
However, since now there is no `.vscodium-server/` directory, when you now log in to the remote via VSCodium, it will reconstruct a new server directory, which should solve the issue with connecting. 

If that works, you can then delete the old server directory and it's contents.

```console
username@<remote_machine>:~/$ rm -rf .vscodium-server_old/
```

Be sure to reinstall all your extensions on this new version of the remote VSCodium server.

### Is the virtual environment activated?

When trying to regenerate the documentation `html` files, you may encounter this error:

```console
username@animus-c:~/$ make clean html
/home/mschee/miniconda3/bin/python: No module named sphinx
make: *** [Makefile:19: clean] Error 1
```

To fix this, activate the `conda` environment.

## Order of the imports matters on Trillium

The error:
```console
2025-10-20 15:32:03.597518: I tensorflow/core/util/port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
2025-10-20 15:32:03.611818: E external/local_xla/xla/stream_executor/cuda/cuda_fft.cc:485] Unable to register cuFFT factory: Attempting to register factory for plugin cuFFT when one has already been registered
2025-10-20 15:32:03.625403: E external/local_xla/xla/stream_executor/cuda/cuda_dnn.cc:8454] Unable to register cuDNN factory: Attempting to register factory for plugin cuDNN when one has already been registered
2025-10-20 15:32:03.629447: E external/local_xla/xla/stream_executor/cuda/cuda_blas.cc:1452] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
2025-10-20 15:32:03.641665: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F AVX512_VNNI AVX512_BF16 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
```

This happens when you try to import `tensorflow` or `keras` before using `xarray` to load the data that will be used by the model.

<!-- see GPBS log 19, Monday 2025/10/20 -->

## Directory not empty

The error: 

```console
OSError: [Errno 39] Directory not empty: 'inputfiles/no2_2019_JFM/'
```

This happens when I try to overwrite a directory or data file where any file to be overwritten is loaded into a data structure in an active Jupyter notebook cell. 
This most often happens when I'm testing out functions which write input files or metadata files and I've loaded that file in another cell to test whether it works.
The solution to this is to restart the kernel in that notebook.

Example: executing these two cells in a row:

```python
from unox.HPC.data0.dataset import uarray

input_u_arr = uarray('no2_2019_JFM', is_input_set=True)
input_u_arr.xr
```

```python
from unox.input import copy_input_files 

this_output = copy_input_files(
    source_input_set = 'no2_2019',
    output_dir = 'no2_2019_JFM',
    keep_vars = 'all',
    # keep_vars = ['no2'],
    start_date = '2019-01-01',
    end_date = '2019-03-31',
    overwrite=True,
)
this_output.xr
```

## Errors running tests from VSCodium

<!-- See GPBS_Log_20 on Tuesday 2026-01-20 -->

Error when running a test using the GUI in VSCodium, clicking on the "run" button next to the test definition:
```console
Test result not found for: ./tests/test_input.py::test_make_input_metadata_file
```

<!-- I found a way to get useful output in `GPBS_Log_19`, on Tuesday 2025/11/25:

> I started trying to reorganize the modules and ran into some issues trying to set up corresponding test directories. I found a useful command `pytest --collect-only` which can just go through and try to find all the tests. It gave some helpful error outputs to figure out what was going on. -->

After running `pytest --collect-only`, I got the output 
```console
E   ValueError: conflicting sizes for dimension 'time': length 192 on 'time' and length 30 on {'time': 'no2', 'lat': 'no2', 'lon': 'no2'}
```
which told me that I'd incorrectly set the length of the time dimension on a new example dataset.

## `NaN` values

If encountering `NaN` values, take a look at the time interval over which data is being used. 
For the `nox` variable, all values past 2020-04-24 are `NaN`, therefore, correlation plots between `nox` (or `truth`) over intervals which include dates past 2020-04-24 will produce the error:
```console
ValueError: autodetected range of [nan, nan] is not finite
```

## Matplotlib has no attribute `__version_info__`

Here is the error I was encountering:

```console
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[5], line 1
----> 1 from unox.plotting import plot_extent 
      3 extent_plot = plot_extent(sample_dataset)

File ~/checkouts/readthedocs.org/user_builds/unox/checkouts/latest/src/unox/plotting.py:1
----> 1 import matplotlib.pyplot as plt
      2 import matplotlib as mpl
      3 import numpy as np

File ~/checkouts/readthedocs.org/user_builds/unox/envs/latest/lib/python3.9/site-packages/matplotlib/pyplot.py:2500
   2498     dict.__setitem__(rcParams, "backend", rcsetup._auto_backend_sentinel)
   2499 # Set up the backend.
-> 2500 switch_backend(rcParams["backend"])
   2502 # Just to be safe.  Interactive mode can be turned on without
   2503 # calling `plt.ion()` so register it again here.
   2504 # This is safe because multiple calls to `install_repl_displayhook`
   2505 # are no-ops and the registered function respect `mpl.is_interactive()`
   2506 # to determine if they should trigger a draw.
   2507 install_repl_displayhook()

File ~/checkouts/readthedocs.org/user_builds/unox/envs/latest/lib/python3.9/site-packages/matplotlib/pyplot.py:277, in switch_backend(newbackend)
    270 # Backends are implemented as modules, but "inherit" default method
    271 # implementations from backend_bases._Backend.  This is achieved by
    272 # creating a "class" that inherits from backend_bases._Backend and whose
    273 # body is filled with the module's globals.
    275 backend_name = cbook._backend_module_name(newbackend)
--> 277 class backend_mod(matplotlib.backend_bases._Backend):
    278     locals().update(vars(importlib.import_module(backend_name)))
    280 required_framework = _get_required_interactive_framework(backend_mod)

File ~/checkouts/readthedocs.org/user_builds/unox/envs/latest/lib/python3.9/site-packages/matplotlib/pyplot.py:278, in switch_backend.<locals>.backend_mod()
    277 class backend_mod(matplotlib.backend_bases._Backend):
--> 278     locals().update(vars(importlib.import_module(backend_name)))

File ~/.asdf/installs/python/3.9.22/lib/python3.9/importlib/__init__.py:127, in import_module(name, package)
    125             break
    126         level += 1
--> 127 return _bootstrap._gcd_import(name[level:], package, level)

File ~/checkouts/readthedocs.org/user_builds/unox/envs/latest/lib/python3.9/site-packages/matplotlib_inline/__init__.py:1
----> 1 from . import backend_inline, config  # noqa
      3 __version__ = "0.2.1"
      5 # we can't ''.join(...) otherwise finding the version number at build time requires
      6 # import which introduces IPython and matplotlib at build time, and thus circular
      7 # dependencies.

File ~/checkouts/readthedocs.org/user_builds/unox/envs/latest/lib/python3.9/site-packages/matplotlib_inline/backend_inline.py:236
    231                 ip.events.unregister("post_run_cell", configure_once)
    233             ip.events.register("post_run_cell", configure_once)
--> 236 _enable_matplotlib_integration()
    239 def _fetch_figure_metadata(fig):
    240     """Get some metadata to help with displaying a figure."""

File ~/checkouts/readthedocs.org/user_builds/unox/envs/latest/lib/python3.9/site-packages/matplotlib_inline/backend_inline.py:215, in _enable_matplotlib_integration()
    211 ip = get_ipython()
    213 import matplotlib
--> 215 if matplotlib.__version_info__ >= (3, 10):
    216     backend = matplotlib.get_backend(auto_select=False)
    217 else:

AttributeError: module 'matplotlib' has no attribute '__version_info__'
```

This was happening in the {doc}`Analysis <../analysis>` notebook, but only when it was pushed to the Read the Docs site. 
It was also occurring when someone else was trying to run a function which imported `matplotlib.pyplot` in a Jupyter notebook.
They were able to import just `matplotlib` without error. 
That notebook was running fine on my Animus environment and it was also running fine when that other person imported `matplotlib` in the Python interpreter using the same environment. 

```console
<username>@animus-c:unox$ conda activate uplt
(uplt) <username>@animus-c:unox$ python
Python 3.9.25 (main, Nov 3 2025, 22:33:05)
[GCC 11.2.0] :: Anaconda, Inc. on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import matplotlib.pyplot
>>>
```

Looking through the error message, I saw that the error was occurring in the `backend_inline.py` script in the `matplotlib-inline` package. 
That explains why it was only occurring when running in a Jupyter notebook and not in the interpreter. 
The reason it was running fine on my environment and not in Read the Docs or the other person's notebooks is that we had [different versions of `matplotlib-inline`](https://github.com/ipython/matplotlib-inline/tags). 
My environment was using `v0.1.7`, which was released on 2024-04-15. 
The other environments were using `v0.2.1`, which was released on 2025-10-23.
I created my environment between those two dates, so it installed `v0.1.7`, the most up-to-date release at the time. 

I made a post  about this on the `matplotlib-inline` GitHub, [GitHub - Matplotlib-Inline Issue #60: AttributeError: module 'matplotlib' has no attribute '__version_info__'](https://github.com/ipython/matplotlib-inline/issues/60).

I encountered this error in the Analysis Notebook when it gets pushed to the Read the Docs site.
I don't see the error when running the notebook on Animus. 
It happens the first time `matplotlib` is imported. 
Harshil also encountered the same error when he tried creating the input files as the `input` module imported `matplotlib.pyplot`. 
I've since removed the import of `matplotlib` from the `input` module because it is not needed, but it is still an issue.

## Disk quota exceeded

```console
[mschee@trig-login01 unox]$ git pull
error: cannot open '.git/FETCH_HEAD': Disk quota exceeded
```

Fix: Delete some data to free up room. 
I deleted a bunch of old stuff from `HPC_runs/`.
To check how much space is being used, try the following "disk usage" command, setting the flag for "human readable format":

```console
(base) username@<remote_machine>:~/unox$ du -sh HPC_runs/*
1.3G    HPC_runs/co_example_run
1.3G    HPC_runs/no2_example_run
4.1G    HPC_runs/_test_ens_zfi3
```

## Importing packages in the wrong order on Trillium

I have found that the order in which I import Python packages on Trillium matters. Basically, I need to load `xarray` and use it to import from a file before I load the `keras` / `tensorflow` modules.

On 2026-02-09, I hit this particular error which was caused by me trying to import functions from keras before loading the xarray package:

```console
Traceback (most recent call last):
  File "/scratch/mschee/Postdoc/unox/src/unox/HPC/run_model.py", line 61, in <module>
    uarr = uarray(inputfiles, is_input_set=True)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/scratch/mschee/Postdoc/unox/src/unox/HPC/data0/dataset.py", line 50, in __init__
    self.xr = get_dataset(
              ^^^^^^^^^^^^
  File "/scratch/mschee/Postdoc/unox/src/unox/HPC/data0/dataset.py", line 150, in get_dataset
    xr_dataset = load_dataset(file_path, **kwargs)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/scratch/mschee/Postdoc/unox/src/unox/HPC/data0/dataset.py", line 188, in load_dataset
    xr_dataset = xr.open_dataset(file_path)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/mschee/.virtualenvs/unoxTrilliumNC/lib/python3.12/site-packages/xarray/backends/api.py", line 573, in open_dataset
    backend_ds = backend.open_dataset(
                 ^^^^^^^^^^^^^^^^^^^^^
  File "/home/mschee/.virtualenvs/unoxTrilliumNC/lib/python3.12/site-packages/xarray/backends/netCDF4_.py", line 646, in open_dataset
    store = NetCDF4DataStore.open(
            ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/mschee/.virtualenvs/unoxTrilliumNC/lib/python3.12/site-packages/xarray/backends/netCDF4_.py", line 376, in open
    import netCDF4
  File "/home/mschee/.virtualenvs/unoxTrilliumNC/lib/python3.12/site-packages/netCDF4/__init__.py", line 3, in <module>
    from ._netCDF4 import *
ImportError: /cvmfs/soft.computecanada.ca/easybuild/software/2023/x86-64-v3/MPI/gcc12/openmpi4/netcdf-mpi/4.9.2/lib64/libnetcdf.so.19: undefined symbol: H5Pset_coll_metadata_write
```

I remember running into this sometime in 2025. I want to look back through my logs to see if I can find if that was the same error message that earlier time. 

## Cannot `make clean html` docs

```console
(uplt) mschee@animus-c:~/unox/docs$ make clean html
Removing everything under '_build'...
Traceback (most recent call last):
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/runpy.py", line 197, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/site-packages/sphinx/__main__.py", line 7, in <module>
    raise SystemExit(main(sys.argv[1:]))
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/site-packages/sphinx/cmd/build.py", line 382, in main
    return make_main(argv)
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/site-packages/sphinx/cmd/build.py", line 217, in make_main
    return make_mode.run_make_mode(argv[1:])
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/site-packages/sphinx/cmd/make_mode.py", line 175, in run_make_mode
    return getattr(make, run_method)()
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/site-packages/sphinx/cmd/make_mode.py", line 85, in build_clean
    rmtree(self.builddir_join(item))
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/site-packages/sphinx/util/osutil.py", line 256, in rmtree
    shutil.rmtree(path)
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/shutil.py", line 734, in rmtree
    _rmtree_safe_fd(fd, path, onerror)
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/shutil.py", line 667, in _rmtree_safe_fd
    _rmtree_safe_fd(dirfd, fullname, onerror)
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/shutil.py", line 667, in _rmtree_safe_fd
    _rmtree_safe_fd(dirfd, fullname, onerror)
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/shutil.py", line 690, in _rmtree_safe_fd
    onerror(os.unlink, fullname, sys.exc_info())
  File "/home/mschee/miniconda3/envs/uplt/lib/python3.9/shutil.py", line 688, in _rmtree_safe_fd
    os.unlink(entry.name, dir_fd=topfd)
OSError: [Errno 16] Device or resource busy: '.nfs0000000d003d06560000001b'
make: *** [Makefile:19: clean] Error 1
```

Fix: log out and log back in.

## Do you have more than one day in the data?

Need to confirm whether this actually has to do with only having one day and therefore having xarray drop the time index.

```python
# here’s the error that i get if i try to generate the input files using this command
make_all_input_files(
    output_dir='co_test',
    years=[2019],
    stage2=False,
    chemra_path='../../users/jk/20/hneeraj/GC_v14.1.1/gc_4x5_47L_merra2_tagCO/OutputDir',
    chemra_var='SpeciesConcVV_CO',
    insitu_path='US_EPA/NO2/daily_NO2/daily_42602_',
    era5_path='ERA5concatenated',
    scale_factors={'chemra': 1e-3,
                    'sp': 1e-5,
                    'ssrd': 1e-6,
                    'blh': 1e-3},
    stage_2_cutoff=2013,    
    var='EmisCO_BioBurn',
    emiss_dir='/users/jk/20/hneeraj/GC_v14.1.1/gc_4x5_47L_merra2_tagCO/OutputDir',
    emiss_pre='HEMCO_diagnostics.',
    emiss_post='01020000.nc',
    scale_factor=1e12,
)
```

```console
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[1], line 24
      1 from unox.input import make_all_input_files
      3 # make_all_input_files(
      4 #     output_dir='co_test',
      5 #     years=range(2023, 2024),
   (...)
     20 #     scale_factor=1e12,
     21 # )
---> 24 make_all_input_files(
     25     output_dir='co_test',
     26     years=[2019],
     27     stage2=False,
     28     chemra_path='../../users/jk/20/hneeraj/GC_v14.1.1/gc_4x5_47L_merra2_tagCO/OutputDir',
     29     chemra_var='SpeciesConcVV_CO',
     30     insitu_path='US_EPA/NO2/daily_NO2/daily_42602_',
     31     era5_path='ERA5concatenated',
     32     scale_factors={'chemra': 1e-3,
     33                     'sp': 1e-5,
     34                     'ssrd': 1e-6,
     35                     'blh': 1e-3},
     36     stage_2_cutoff=2013,    
     37     var='EmisCO_BioBurn',
     38     emiss_dir='/users/jk/20/hneeraj/GC_v14.1.1/gc_4x5_47L_merra2_tagCO/OutputDir',
     39     emiss_pre='HEMCO_diagnostics.',
     40     emiss_post='01020000.nc',
     41     scale_factor=1e12,
     42 )

File /users/jk/22/hneeraj/unox_dir/unox/src/unox/unox.py:35, in time_this.<locals>.wrap_func(*args, **kwargs)
     33 t1 = datetime.now()
     34 # Execute the function
---> 35 result = func(*args, **kwargs)
     36 # Get the time at the end of the execution
     37 t2 = datetime.now()

File /users/jk/22/hneeraj/unox_dir/unox/src/unox/input.py:998, in make_all_input_files(output_dir, sort, **kwargs)
    996 # Create y input data
    997 print("Creating y input data...")
--> 998 input_netcdf_xr = make_all_y_input_files(
    999     output_dir=output_dir,
   1000     sort=False,
   1001     **kwargs,
   1002 )
   1003 # Create x input data
   1004 print("Creating x input data...")

File /users/jk/22/hneeraj/unox_dir/unox/src/unox/input.py:868, in make_all_y_input_files(years, var, output_dir, sort, **kwargs)
    866 for year in years:
    867     print(f"\tCreating y input data for {var} in {year}...")
--> 868     y_data, g_attr_dict = make_y_input_file(
    869         year=year, 
    870         var=var,
    871         output_dir=output_dir,
    872         write_this_year=False,
    873         sort=False,
    874         **kwargs,
    875     )
    876     y_data_array.append(y_data)
    877 # Concatenate the datasets along the time dimension

File /users/jk/22/hneeraj/unox_dir/unox/src/unox/input.py:203, in make_y_input_file(year, var, emiss_dir, emiss_pre, emiss_post, scale_factor, nan_fill, stage_2_cutoff, output_dir, write_this_year, overwrite, output_format, **kwargs)
    200 # Write out results
    201 if not isinstance(output_dir, type(None)):
    202     # Create metadata file
--> 203     meta_dict = make_input_metadata_file(
    204         input_netcdf_xr,
    205         output_dir=output_dir,
    206         g_attrs=g_attr_dict,
    207     )
    208     # Save the data to file
    209     # For writing out a numpy file
    210     if output_format in ['npy', 'both']:
    211         # Assemble the file path

File /users/jk/22/hneeraj/unox_dir/unox/src/unox/input.py:1121, in make_input_metadata_file(input_set, output_dir, g_attrs, overwrite)
   1114     metadata_dict = {
   1115         'years': {
   1116             'x': [],
   1117             'y': [],
   1118         },
   1119     }
   1120 # Get a list of years present in the dataset
-> 1121 years = get_years(xr_dataset)
   1122 # Check for global attributes
   1123 if isinstance(g_attrs, type(None)):

File /users/jk/22/hneeraj/unox_dir/unox/src/unox/HPC/data0/dataset.py:366, in get_years(dataset)
    364     raise TypeError(f"(get_years) `dataset` must be an xarray Dataset or DataArray. Got type: {type(dataset)}.")
    365 # Get a list of years present in the dataset
--> 366 years = xr_dataset['time'].dt.year.values
    367 # Sort and get unique years
    368 years = sorted(list(set(years)))

File ~/miniconda3/envs/uplt/lib/python3.9/site-packages/xarray/core/common.py:285, in AttrAccessMixin.__getattr__(self, name)
    283         with suppress(KeyError):
    284             return source[name]
--> 285 raise AttributeError(
    286     f"{type(self).__name__!r} object has no attribute {name!r}"
    287 )

AttributeError: 'DataArray' object has no attribute 'dt'
```