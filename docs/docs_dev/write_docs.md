<a id='top'></a>
# Writing Documentation

This guide describes how to make updates to the documentation while developing the code base.
This guide assumes you have read through the {doc}`Workflow <workflow>` page.
<!-- Note: for linking between documents, use the `doc` role defined in the [Sphinx documentation](https://docs.readthedocs.com/platform/stable/guides/cross-referencing-with-sphinx.html#the-doc-role). 
TLDR: Create a link to a different document by typing `{doc}`, followed by the name of the file surrounded by backticks, excluding the extension. If you would like to change the rendered text of the link, surround the desired link text in backticks, then add the name of the file in angle brackets, in the format: "{doc}`Click here <filename>`".  -->

## Contents

- [Introduction](#intro)
- [Preview documentation changes](#preview_changes)
    - [Live Preview](#live_preview)
- Managing the documentation
    - How did I set up the way it auto updates?
    - Links between internal pages
    - Auto API and why writing good docstrings is important
- [The model diagram](#model_diagram)
    - [Editing the diagram](#edit_diagram)

---
<a id='intro'></a>
[back to top](#top)

## Introduction

The documentation for this project is contained within the `docs/` directory. 
When you need to make a change to the documentation, you will generally edit the Markdown files, with the extension `.md`. 
Any time you push a commit to the remote repository, these Markdown files will be used to generate `html` to display on the [Read the Docs page](https://unox.readthedocs.io/en/latest/index.html).
That automatic process, as well as the structure of the documentation, was set up following [Chapter 6 of the Py-Pkgs guide](https://py-pkgs.org/06-documentation).
Below are a few notes of differences between what is described in that guide and what you will find in this repository.
- Typical locations of standard documentation files.
    - I have moved the following files from their typical location in the root directory to the `docs/docs_ref` directory.
        - Code of Conduct, in the `CONDUCT.md` file.
        - Contributing Guidelines, in the `CONTRIBUTING.md` file.
    - The `CHANGELOG.md`, `LICENSE`, and `README.md` files are kept in the root directory.
        - This is to allow GitHub to automatically use their content to fill parts of the repository's page. If these files are not in the root directory, that functionality will break.
        - I have created the `changelog.md` and `license.md` files in the `docs/docs_ref/` directory which simply contain statements to include the content of the files in the root directory. This is so that the Read the Docs pages for those files will be populated with the content without needing to make copies.
    - In contrast to the file structure shown in [Section 6.2 of the Py-Pkgs guide](https://py-pkgs.org/06-documentation#writing-documentation), below is the structure of this repositories documentation.
        ```
        unox
        ├── ...
        ├── docs
        │   ├── ...
        │   ├── docs_ref      
        │   │   ├── changelog.md       <- Links to CHANGELOG.md
        │   │   ├── CONDUCT.md         <--------
        │   │   ├── CONTRIBUTING.md    <--------
        │   │   └── license.md         <- Links to LICENSE
        │   └── ...
        ├── ...
        ├── src
        │   └── ...
        ├── tests
        │   └── ...
        ├── .readthedocs.yml
        ├── CHANGELOG.md               <--------
        ├── LICENSE                    <--------
        ├── ...
        ├── README.md                  <--------
        ├── ...
        └── pyproject.toml
        ```

---
<a id='preview_changes'></a>
[back to top](#top)

## Preview documentation changes

To generate a preview of the documentation before pushing to the GitHub repository, you can run the `docs/Makefile` script as shown below. 
For more detail on this process, see [Section 6.3 of the Py-Pkgs guide](https://py-pkgs.org/06-documentation#building-documentation).
Note: it is important to **<ins>navigate to the `unox/docs/` directory</ins>** before running the "make" command.

```console
(env_name) username@animus-c:~unox$ cd docs/
(env_name) username@animus-c:~/unox/docs$ make html
Running Sphinx v7.4.7
loading translations [en]... done
loading pickled environment... done
...
```
<details>

<summary>Expand for all output</summary>

```console
myst v3.0.1: MdParserConfig(commonmark_only=False, gfm_only=False, enable_extensions=set(), disable_syntax=[], all_links_external=False, links_external_new_tab=False, url_schemes=('http', 'https', 'mailto', 'ftp'), ref_domains=None, fence_as_directive=set(), number_code_blocks=[], title_to_header=False, heading_anchors=0, heading_slug_func=None, html_meta={}, footnote_transition=True, words_per_minute=200, substitutions={}, linkify_fuzzy_links=True, dmath_allow_labels=True, dmath_allow_space=True, dmath_allow_digits=True, dmath_double_inline=False, update_mathjax=True, mathjax_classes='tex2jax_process|mathjax_process|math|output_area', enable_checkboxes=False, suppress_warnings=[], highlight_code_blocks=True)
myst-nb v1.3.0: NbParserConfig(custom_formats={}, metadata_key='mystnb', cell_metadata_key='mystnb', kernel_rgx_aliases={}, eval_name_regex='^[a-zA-Z_][a-zA-Z0-9_]*$', execution_mode='auto', execution_cache_path='', execution_excludepatterns=(), execution_timeout=30, execution_in_temp=False, execution_allow_errors=False, execution_raise_on_error=False, execution_show_tb=False, merge_streams=False, render_plugin='default', remove_code_source=False, remove_code_outputs=False, scroll_outputs=False, code_prompt_show='Show code cell {type}', code_prompt_hide='Hide code cell {type}', number_source_lines=False, output_stderr='show', render_text_lexer='myst-ansi', render_error_lexer='ipythontb', render_image_options={}, render_figure_options={}, render_markdown_format='commonmark', output_folder='build', append_css=True, metadata_to_fm=False)
Using jupyter-cache at: /home/username/unox/docs/_build/.jupyter_cache
[AutoAPI] Reading files... [ 54%] /home/username/unox/src/unox/HPC/utils/.ipynb_checkpoints/cleaner-checkpoint
[AutoAPI] Reading files... [ 57%] /home/username/unox/src/unox/HPC/utils/.ipynb_checkpoints/functions-checkpoi
[AutoAPI] Reading files... [100%] /home/username/unox/src/unox/HPC/legacy/run_functions_old.py
WARNING: Cannot resolve import of unknown module unox.HPC.data0.paths in unox.data
WARNING: Cannot resolve import of unknown module unox.HPC.data0.latlon in unox.data
WARNING: Cannot resolve import of unknown module unox.HPC.data0.verify_dtype in unox.data
WARNING: Cannot resolve import of unknown module unox.HPC.data0.verify_dataset in unox.data
WARNING: Cannot resolve import of unknown module unox.HPC.data0.dataset in unox.data
WARNING: Cannot resolve import of unknown module unox.HPC.data0.verify_dtype in unox.plot_format
WARNING: Cannot resolve import of unknown module unox.HPC.data0.paths in unox.unox
WARNING: Cannot resolve import of unknown module unox.HPC.data0.paths in unox.model
WARNING: Cannot resolve import of unknown module unox.HPC.utils in unox.model
WARNING: Cannot resolve import of unknown module unox.HPC.data0.paths in unox.input
WARNING: Cannot resolve import of unknown module unox.HPC.data0.paths in unox.input
WARNING: Cannot resolve import of unknown module unox.HPC.data0.paths in unox.input
WARNING: Cannot resolve import of unknown module unox.HPC.data0.dataset in unox.input
WARNING: Cannot resolve import of unknown module unox.HPC.data0.dataset in unox.input
WARNING: Cannot resolve import of unknown module unox.HPC.data0.verify_dataset in unox.input
WARNING: Cannot resolve import of unknown module unox.HPC.data0.verify_dataset in unox.input
WARNING: Cannot resolve import of unknown module unox.HPC.data0.latlon in unox.input
WARNING: Cannot resolve import of unknown module unox.HPC.data0.dataset in unox.plotting
WARNING: Cannot resolve import of unknown module unox.HPC.data0.verify_dataset in unox.plotting
WARNING: Cannot resolve import of unknown module unox.HPC.data0.verify_dataset in unox.plotting
WARNING: Cannot resolve import of unknown module unox.HPC.data0.verify_dtype in unox.plotting
WARNING: Cannot resolve import of unknown module unox.HPC.data0.paths in unox.plotting
[AutoAPI] Mapping Data... [ 54%] /home/username/unox/src/unox/HPC/utils/.ipynb_checkpoints/cleaner-checkpoint.
[AutoAPI] Mapping Data... [ 57%] /home/username/unox/src/unox/HPC/utils/.ipynb_checkpoints/functions-checkpoin
[AutoAPI] Mapping Data... [100%] /home/username/unox/src/unox/HPC/legacy/run_functions_old.py
[AutoAPI] Rendering Data... [  3%] unox
[AutoAPI] Rendering Data... [  5%] core
[AutoAPI] Rendering Data... [  8%] data0
[AutoAPI] Rendering Data... [ 11%] cleaner
[AutoAPI] Rendering Data... [ 14%] core_tl
[AutoAPI] Rendering Data... [ 16%] training
[AutoAPI] Rendering Data... [ 19%] core_new
[AutoAPI] Rendering Data... [ 22%] core_old
[AutoAPI] Rendering Data... [ 24%] unox.data
[AutoAPI] Rendering Data... [ 27%] unox.unox
[AutoAPI] Rendering Data... [ 30%] run_model
[AutoAPI] Rendering Data... [ 32%] functions
[AutoAPI] Rendering Data... [ 35%] unox.model
[AutoAPI] Rendering Data... [ 38%] unox.input
[AutoAPI] Rendering Data... [ 41%] data_split
[AutoAPI] Rendering Data... [ 43%] set_of_runs
[AutoAPI] Rendering Data... [ 46%] data0.paths
[AutoAPI] Rendering Data... [ 49%] data0.config
[AutoAPI] Rendering Data... [ 51%] data0.latlon
[AutoAPI] Rendering Data... [ 54%] unox.evaluate
[AutoAPI] Rendering Data... [ 57%] unox.plotting
[AutoAPI] Rendering Data... [ 59%] data0.dataset
[AutoAPI] Rendering Data... [ 62%] functions_old
[AutoAPI] Rendering Data... [ 65%] data-checkpoint
[AutoAPI] Rendering Data... [ 68%] unox-checkpoint
[AutoAPI] Rendering Data... [ 70%] core-checkpoint
[AutoAPI] Rendering Data... [ 73%] unox.plot_format
[AutoAPI] Rendering Data... [ 76%] input-checkpoint
[AutoAPI] Rendering Data... [ 78%] data0.load_input
[AutoAPI] Rendering Data... [ 81%] run_functions_old
[AutoAPI] Rendering Data... [ 84%] cleaner-checkpoint
[AutoAPI] Rendering Data... [ 86%] data0.verify_dtype
[AutoAPI] Rendering Data... [ 89%] plotting-checkpoint
[AutoAPI] Rendering Data... [ 92%] combine_predictions
[AutoAPI] Rendering Data... [ 95%] data0.run_functions
[AutoAPI] Rendering Data... [ 97%] functions-checkpoint
[AutoAPI] Rendering Data... [100%] data0.verify_dataset

[autosummary] generating autosummary for: analysis.ipynb, autoapi/cleaner-checkpoint/index.rst, autoapi/cleaner/index.rst, autoapi/combine_predictions/index.rst, autoapi/core-checkpoint/index.rst, autoapi/core/index.rst, autoapi/core_new/index.rst, autoapi/core_old/index.rst, autoapi/core_tl/index.rst, autoapi/data-checkpoint/index.rst, ..., docs_ref/CONDUCT.md, docs_ref/CONTRIBUTING.md, docs_ref/changelog.md, docs_ref/license.md, docs_setup/data.md, docs_setup/installation.md, docs_setup/run_model.md, example.ipynb, index.md, unox_CO_docs.ipynb
building [mo]: targets for 0 po files that are out of date
writing output... 
building [html]: targets for 43 source files that are out of date
updating environment: 0 added, 45 changed, 0 removed
2026-04-06 13:23:37.348637: I external/local_xla/xla/tsl/cuda/cudart_stub.cc:32] Could not find cuda drivers on your machine, GPU will not be used.
2026-04-06 13:23:37.448230: I external/local_xla/xla/tsl/cuda/cudart_stub.cc:32] Could not find cuda drivers on your machine, GPU will not be used.
2026-04-06 13:23:37.465897: E external/local_xla/xla/stream_executor/cuda/cuda_fft.cc:485] Unable to register cuFFT factory: Attempting to register factory for plugin cuFFT when one has already been registered
2026-04-06 13:23:37.490579: E external/local_xla/xla/stream_executor/cuda/cuda_dnn.cc:8454] Unable to register cuDNN factory: Attempting to register factory for plugin cuDNN when one has already been registered
2026-04-06 13:23:37.497935: E external/local_xla/xla/stream_executor/cuda/cuda_blas.cc:1452] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
2026-04-06 13:23:37.518875: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
2026-04-06 13:23:42.291321: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:38] TF-TRT Warning: Could not find TensorRT
/home/username/miniconda3/envs/env_name/lib/python3.9/site-packages/proplot/__init__.py:6: UserWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html. The pkg_resources package is slated for removal as early as 2025-11-30. Refrain from using this package or pin to Setuptools<81.
  import pkg_resources as pkg
reading sources... [100%] index
/home/username/unox/docs/autoapi/cleaner-checkpoint/index.rst:29: WARNING: duplicate object description of cleaner-checkpoint.flist, other instance in autoapi/cleaner-checkpoint/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/cleaner-checkpoint/index.rst:31: WARNING: duplicate object description of cleaner-checkpoint.data, other instance in autoapi/cleaner-checkpoint/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/cleaner-checkpoint/index.rst:33: WARNING: duplicate object description of cleaner-checkpoint.flist, other instance in autoapi/cleaner-checkpoint/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/cleaner-checkpoint/index.rst:35: WARNING: duplicate object description of cleaner-checkpoint.data, other instance in autoapi/cleaner-checkpoint/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/cleaner-checkpoint/index.rst:37: WARNING: duplicate object description of cleaner-checkpoint.flist, other instance in autoapi/cleaner-checkpoint/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/cleaner-checkpoint/index.rst:39: WARNING: duplicate object description of cleaner-checkpoint.data, other instance in autoapi/cleaner-checkpoint/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/cleaner/index.rst:29: WARNING: duplicate object description of cleaner.flist, other instance in autoapi/cleaner/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/cleaner/index.rst:31: WARNING: duplicate object description of cleaner.data, other instance in autoapi/cleaner/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/cleaner/index.rst:33: WARNING: duplicate object description of cleaner.flist, other instance in autoapi/cleaner/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/cleaner/index.rst:35: WARNING: duplicate object description of cleaner.data, other instance in autoapi/cleaner/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/cleaner/index.rst:37: WARNING: duplicate object description of cleaner.flist, other instance in autoapi/cleaner/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/cleaner/index.rst:39: WARNING: duplicate object description of cleaner.data, other instance in autoapi/cleaner/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/combine_predictions/index.rst:35: WARNING: duplicate object description of combine_predictions.jobname, other instance in autoapi/combine_predictions/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/combine_predictions/index.rst:43: WARNING: duplicate object description of combine_predictions.savedir, other instance in autoapi/combine_predictions/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/data0/dataset/index.rst:121: WARNING: duplicate object description of data0.dataset.uarray._verify, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/data0/dataset/index.rst:127: WARNING: duplicate object description of data0.dataset.uarray._get_years, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/data0/dataset/index.rst:130: WARNING: duplicate object description of data0.dataset.uarray._select_year, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/data0/dataset/index.rst:133: WARNING: duplicate object description of data0.dataset.uarray._get_metadata, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/data0/dataset/index.rst:136: WARNING: duplicate object description of data0.dataset.uarray._get_epochs_logs, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/data0/dataset/index.rst:139: WARNING: duplicate object description of data0.dataset.uarray._shift_lons, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/run_model/index.rst:45: WARNING: duplicate object description of run_model.unet, other instance in autoapi/run_model/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/run_model/index.rst:47: WARNING: duplicate object description of run_model.uarr, other instance in autoapi/run_model/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/run_model/index.rst:49: WARNING: duplicate object description of run_model.years, other instance in autoapi/run_model/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/run_model/index.rst:51: WARNING: duplicate object description of run_model.unet, other instance in autoapi/run_model/index, use :no-index: for one of them
/home/username/unox/docs/autoapi/unox/input/index.rst:90: ERROR: Unexpected indentation.
/home/username/unox/docs/autoapi/unox/input/index.rst:91: WARNING: Block quote ends without a blank line; unexpected unindent.
/home/username/unox/docs/autoapi/unox/input/index.rst:217: ERROR: Unexpected indentation.
/home/username/unox/docs/autoapi/unox/input/index.rst:218: WARNING: Block quote ends without a blank line; unexpected unindent.
/home/username/unox/docs/autoapi/unox/input/index.rst:367: WARNING: Inline literal start-string without end-string.
/home/username/unox/docs/autoapi/unox/input/index.rst:367: WARNING: Inline interpreted text or phrase reference start-string without end-string.
/home/username/unox/docs/autoapi/unox/input/index.rst:375: WARNING: Definition list ends without a blank line; unexpected unindent.
/home/username/unox/docs/autoapi/unox/input/index.rst:377: ERROR: Unexpected indentation.
/home/username/unox/docs/autoapi/unox/input/index.rst:380: WARNING: Block quote ends without a blank line; unexpected unindent.
/home/username/unox/docs/autoapi/unox/input/index.rst:381: WARNING: Definition list ends without a blank line; unexpected unindent.
/home/username/unox/docs/autoapi/unox/input/index.rst:389: ERROR: Unexpected indentation.
/home/username/unox/docs/autoapi/unox/input/index.rst:392: WARNING: Block quote ends without a blank line; unexpected unindent.
/home/username/unox/docs/autoapi/unox/input/index.rst:398: ERROR: Unexpected indentation.
/home/username/unox/docs/autoapi/unox/input/index.rst:400: WARNING: Block quote ends without a blank line; unexpected unindent.
/home/username/unox/docs/autoapi/unox/input/index.rst:402: WARNING: Inline literal start-string without end-string.
/home/username/unox/docs/autoapi/unox/input/index.rst:402: WARNING: Inline interpreted text or phrase reference start-string without end-string.
/home/username/unox/docs/autoapi/unox/input/index.rst:102: ERROR: Unknown target name: "nox".
/home/username/unox/docs/autoapi/unox/input/index.rst:230: ERROR: Unknown target name: "tropess_reanalysis_2hr_no2_sfc".
/home/username/unox/docs/autoapi/unox/input/index.rst:235: ERROR: Unknown target name: "daily_42602".
/home/username/unox/docs/autoapi/unox/input/index.rst:381: ERROR: Unknown target name: "nox".
/home/username/unox/docs/autoapi/unox/input/index.rst:392: ERROR: Unknown target name: "tropess_reanalysis_2hr_no2_sfc".
/home/username/unox/docs/autoapi/unox/input/index.rst:392: ERROR: Unknown target name: "daily_42602".
/home/username/unox/docs/autoapi/unox/unox/index.rst:41: ERROR: Unexpected indentation.
/home/username/unox/docs/autoapi/unox/unox/index.rst:44: WARNING: Block quote ends without a blank line; unexpected unindent.
/home/username/unox/docs/docs_analysis/ensemble_runs.md:605: ERROR: Document may not end with a transition.
/home/username/unox/docs/docs_ref/license.md:3: CRITICAL: Directive "include": file not found: '/home/username/unox/docs/LICENSE'
looking for now-outdated files... none found
pickling environment... done
checking consistency... /home/username/unox/docs/unox_CO_docs.ipynb: WARNING: document isn't included in any toctree
done
preparing documents... done
copying assets... 
copying static files... done
copying extra files... done
copying assets: done
writing output... [100%] index
/home/username/unox/docs/autoapi/training/index.rst:17: WARNING: more than one target found for cross-reference 'Unet': core-checkpoint.Unet, core.Unet, core_new.Unet, core_old.Unet, core_tl.Unet
/home/username/unox/docs/docs_analysis/ensemble_runs.md:11: WARNING: 'myst' cross-reference target not found: 'intro' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:12: WARNING: 'myst' cross-reference target not found: 'run_ensemble' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:13: WARNING: 'myst' cross-reference target not found: 'prep_ensemble' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:14: WARNING: 'myst' cross-reference target not found: 'submit_ensemble' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:15: WARNING: 'myst' cross-reference target not found: 'monitor_ensemble' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:16: WARNING: 'myst' cross-reference target not found: 'collect_results' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:17: WARNING: 'myst' cross-reference target not found: 'analyze_ensemble' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:18: WARNING: 'myst' cross-reference target not found: 'explore_ensemble' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:19: WARNING: 'myst' cross-reference target not found: 'plot_ensemble_member' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:20: WARNING: 'myst' cross-reference target not found: 'BaW_plots' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:21: WARNING: 'myst' cross-reference target not found: 'regularizers' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:22: WARNING: 'myst' cross-reference target not found: 'what_is_regularizer' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:23: WARNING: 'myst' cross-reference target not found: 'config_reg_ens' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:24: WARNING: 'myst' cross-reference target not found: 'plot_reg_impact' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:27: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:38: WARNING: 'myst' cross-reference target not found: 'submit_ensemble' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:38: WARNING: 'myst' cross-reference target not found: 'analyze_ensemble' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:38: WARNING: 'myst' cross-reference target not found: 'regularizers' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:44: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:49: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:67: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:123: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:157: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:218: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:226: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:281: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:322: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:391: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:399: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:432: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:509: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_analysis/ensemble_runs.md:38: WARNING: unknown document: 'analysis'
/home/username/unox/docs/docs_analysis/ensemble_runs.md:223: WARNING: unknown document: 'analysis'
/home/username/unox/docs/docs_dev/write_docs.md:11: WARNING: 'myst' cross-reference target not found: 'preview_changes' [myst.xref_missing]
/home/username/unox/docs/docs_dev/write_docs.md:12: WARNING: 'myst' cross-reference target not found: 'live_preview' [myst.xref_missing]
/home/username/unox/docs/docs_dev/write_docs.md:17: WARNING: 'myst' cross-reference target not found: 'model_diagram' [myst.xref_missing]
/home/username/unox/docs/docs_dev/write_docs.md:18: WARNING: 'myst' cross-reference target not found: 'edit_diagram' [myst.xref_missing]
/home/username/unox/docs/docs_dev/write_docs.md:21: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_dev/write_docs.md:279: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_dev/write_docs.md:293: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_dev/write_docs.md:344: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:10: WARNING: 'myst' cross-reference target not found: 'data_sources' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:11: WARNING: 'myst' cross-reference target not found: 'tcr-2_nox' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:13: WARNING: 'myst' cross-reference target not found: 'tcr2-no2' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:15: WARNING: 'myst' cross-reference target not found: 'era5' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:17: WARNING: 'myst' cross-reference target not found: 'download_era5' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:18: WARNING: 'myst' cross-reference target not found: 'us_epa' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:20: WARNING: 'myst' cross-reference target not found: 'download_us_epa' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:23: WARNING: 'myst' cross-reference target not found: 'input_files' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:24: WARNING: 'myst' cross-reference target not found: 'input_file_structure' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:25: WARNING: 'myst' cross-reference target not found: 'make_input_files' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:28: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:33: WARNING: 'myst' cross-reference target not found: 'tcr-2_nox' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:40: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:61: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:83: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:108: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:172: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:193: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:224: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:236: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/data.md:318: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:11: WARNING: 'myst' cross-reference target not found: 'intro' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:12: WARNING: 'myst' cross-reference target not found: 'prep_model_run' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:13: WARNING: 'myst' cross-reference target not found: 'from_animus_to_HPC' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:14: WARNING: 'myst' cross-reference target not found: 'config_files' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:15: WARNING: 'myst' cross-reference target not found: 'run_model_HPC' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:16: WARNING: 'myst' cross-reference target not found: 'submit_job' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:17: WARNING: 'myst' cross-reference target not found: 'monitor_job' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:18: WARNING: 'myst' cross-reference target not found: 'get_output' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:19: WARNING: 'myst' cross-reference target not found: 'from_HPC_to_animus' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:22: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:38: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:47: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:86: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:145: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:152: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:198: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:578: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:585: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/username/unox/docs/docs_setup/run_model.md:341: WARNING: Pygments lexer name 'txt' is not known
/home/username/unox/docs/index.md:64: WARNING: 'myst' cross-reference target not found: 'doi.org/10.5194/acp-22-14059-2022' [myst.xref_missing]
generating indices... genindex py-modindex done
highlighting module code... [100%] unox.unox
writing additional pages... search done
Copying the source path /home/username/unox/docs/model_diagram.png to /home/username/unox/docs/_build/html/_images/model_diagram.png will overwrite data, as a file already exists at the destination path and the content does not match.
copying images... [100%] ../model_diagram.png
dumping search index in English (code: en)... done
dumping object inventory... done
```

</details>

```console
...
build succeeded, 156 warnings.

The HTML pages are in _build/html.
```
<!-- TO ADD OUTPUT -->

This will use the Sphinx package (hence including `sphinx-autoapi` and
`sphinx-rtd-theme` under the development group `dev`) to turn the markdown documents and docstrings into `html` pages that will be used by the site hosted on Read the Docs.

Sometimes, a change you make to the docs will not be picked up when regenerating the `html` files. 
This can often be solved by running `make clean html` instead, which takes a bit longer as it does a complete rebuild. 
If you are still having errors, see the troubleshooting guide. 

<a id='live_preview'></a>
[back to top](#top)

### Live Preview

The `Live Preview` extension allows you to preview how `html` pages will look. 
I find this particularly helpful when editing the documentation files you are viewing right now. 
If you want to edit the documentation, open the `unox/docs/_build/html/index.html` file in VSCodium and in the top right corner, there is a symbol which looks like a rectangle divided in half with a magnifying glass over it.
This will open a live preview in a split view. 
I find it helpful to have this preview in a separate window. 
You can also open this preview in your browser to see how it will render by copying the URL at the top of the preview window and pasting it into your browser.
The URL will look something like `http://127.0.0.1:3000/docs/_build/html/docs_dev/write_docs.html`. 

---
<a id='model_diagram'></a>
[back to top](#top)

## The model diagram

A diagram of the U-net model appears in the {doc}`README <workflow>` file, the contents of which is displayed on the project's [GitHub page](https://github.com/scheemik/unox) as well as the [Read the Docs page](https://unox.readthedocs.io/en/latest/index.html).

I have two copies of this model diagram in the repository, both of which are shown below and should match:
- `unox/model_diagram.png`
    - ![model_diagram](../model_diagram.png)
- `unox/docs/model_diagram.png` 
    - ![model_diagram](../../model_diagram.png)

The reason for this is because there is no way I have found to write include statements for the `README` such that the model diagram shows up both in the GitHub page as well as Read the Docs. 
If you change the model diagram, be sure to update it in both places. 

This diagram was generated using LaTeX following the example of the [`PlotNeuralNet` project by `HarisIqbal88`](https://github.com/HarisIqbal88/PlotNeuralNet/tree/master).
This project allows you to specify your model's architecture in a Python file and then it generates the LaTeX file for you to render the diagram. 
However, this Python project is based around Ubuntu 16 or 18 and is very difficult to get running correctly. 
I was able to run it by loading a Docker instance running Ubuntu 16, but I would highly recommend against doing it that way. 

Instead, I have included files in this repository to reproduce the model diagram:
```
docs/
└── docs_dev/
    └── model_diagram/
        ├── layers/
        │   ├── Ball.sty            # Style sheet for "Ball" objects
        │   ├── Box.sty             # Style sheet for "Box" objects
        │   ├── init.tex            # Initialization file for the layer objects
        │   ├── Label_Box.sty       # Style sheet for "Label_Box" objects
        │   └── RightBandedBox.sty  # Style sheet for "RightBandedBox" objects
        ├── make_diagram_plots.py   # Script to generate plots to use in the diagram
        ├── plots/                  # Directory of plots generated by `make_diagram_plots.py`
        │   ├── no2_2019_JFM_blh_plot.png
        │   ├── ...
        │   └── no2_2019_JFM_v10_plot.png
        └── unet.tex                # LaTeX file that defines the model diagram
```

The Python script `make_diagram_plots.py` will generate the plots used in the model diagram.
I have not included the `plots/` directory of images in the repository, so if you want to recreate the diagram, you will need to run `make_diagram_plots.py` first. 
To avoid having each plot include a subplot label "a", change `pplt.rc.abc = True` to `pplt.rc.abc = False` in `plotting.py`.
Then, run the script **<ins>from the base `unox/` directory with the conda environment activated</ins>**:
```console
username@animus-c:~/unox$ conda activate env_name
(env_name) username@animus-c:~/unox$ python docs/docs_dev/model_diagram/make_diagram_plots.py
```
This will automatically generate a plot of a map of each variable contained in the `no2_JFM_2019` input file for 2019-01-01.
If you need to make changes to the model diagram, I recommend copying the files inside the `model_diagram/` directory into an [Overleaf](https://www.overleaf.com/) project and making the required changes.

<a id='edit_diagram'></a>
[back to top](#top)

### Editing the diagram

The model diagram is made using `tiz` inside of LaTeX. 
Most of the parameters of the diagram are defined in `unet.tex` while the definitions for particular objects used in the diagram are found in their respective style sheets inside the `layers/` directory. 

In the diagram, `x` is the horizontal direction, `y` is vertical, and `z` is the direction into the page. 
The objects are spaced out in the diagram in a couple different ways.
The input variable images and the first convolutional layer are spaced out using coordinates. 
For example, here is the first input frame:
```tex
\node[canvas is yz plane at x=0] (temp) at (-8,0,0) {\includegraphics[width=15cm,height=7cm,angle=270]{plots/no2_2019_JFM_u10_plot.png}};
```
A couple of things to note:
- The coordinates of where this will appear are defined as `(-8,0,0)`
    - This corresponds to x=-8, y=0, and z=0
- The canvas is defined as `yz`
    - The original code defined the canvas as `zy`, but this flipped the images horizontally
    - In order to have the images show up in the correct orientation, I chose `yz`, but this rendered the image tilted by 90 degrees
        - To undo this rotation, I add `angle=270` to the arguments of `\includegraphics`
- The width and height of the image were choosen arbitrarily 
    - The `\includegraphics` function requires dimensions in physical units, so I wasn't able to just copy the `height` and `depth` dimensions of the first convolutional layer

For the labels along the bottom, I created a type of layer I call `Label_Box`.
Here's an example showing the label for the input variables:
```tex
% Label the input variables
\pic[shift={ (-6,0,0) }] at (0,0,0) 
    {Label_Box={
        name=input,
        caption=Input Variables,
        fill=white, 
        opacity=0,
        height=45,
        width=20,
        depth=40
        }
    };
```
- The coordinates are specified as a `shift` of `(-6,0,0)` from `(0,0,0)`.
    - This should be equivalent to just specifying the coordinates to be `(-6,0,0)`, but shows how objects will be placed in relation to other objects in farther along.
- The `caption` argument is what will show up in the diagram
    - To change the font size, I added the command `\Huge` to `layers/Label_Box.sty`
- This actually defines a box, but it is transparent
    - I did this by defining the `fill` to be `white` and `opacity` to be `0`.
    - Note that I needed to make changes in `layers/Label_Box.sty` for this to work, which is why I copied that style sheet from `layers/Box.sty` to have a separate kind of layer object.
- The `height`, `width`, and `depth` values were chosen by trial-and-error.
    - I kept changing their values until the text appeared where I wanted it to.

The next example shows how layer objects are defined:
```tex
%%% Block 1
%% Block1_Conv1
\pic[shift={ (2,0,0) }] at (0,0,0) 
    {RightBandedBox={
        name=b1_conv1,
        caption= $n$,
        xlabel={{ 128, }},
        zlabel=,
        fill=\ConvColor,
        bandfill=\ConvReluColor,
        opacity=0.75,
        height=32,
        width={{ 1 }},
        depth=64
        }
    };
%% Block1_Conv2
\pic[shift={ (0.5,0,0) }] at (b1_conv1-east) 
    {RightBandedBox={
        name=b1_conv2,
        caption= $2n$,
        xlabel={{ 256, }},
        zlabel=,
        fill=\ConvColor,
        bandfill=\ConvReluColor,
        opacity=0.75,
        height=32,
        width={{ 2 }},
        depth=64
        }
    };
```
- The second object, `b1_conv2`, has it's position defined in relation to the first object, `b1_conv1`
    - I gave it a shift of `(0.5,0,0)` from `b1_conv1-east`.
    - Using `-east` specifies the right side of an object, `-west` is the left.
- The `caption` argument can take in math text
    - The `xlabel` must take in a double curly bracketed list of integers where there must be at least one integer and at least one comma.
        - I don't know why, it just is the case.
    - The `zlabel` can take in integers, or nothing.
- The `width` argument must be a double curly bracketed list.
    - I've only given it one number, but you can give it multiple which will create a banded box.
- For the convolutional layers, I've defined the `height`, `width`, and `depth` in relation to each other.
    - The objects in the diagram are relatively the correct size in relation to each other based on how `core.py` is written.

The arrows connecting the different layers along the main axis are `connections`:
```tex
\draw [connection]  (b1_maxpool-east)    -- node {\midarrow} (b2_conv1-west);
```
- Note how the `-east` and `-west` suffixes are used to note which side of the object the arrow should touch.
- The order in which these connections are drawn matters.
    - You will get an error if you put this line before the lines in which the `b1_maxpool` and `b2_conv1` objects are defined.
    - The arrows will be drawn on top of all objects that come before them in the script.

The residual learning connection arrows are a bit more complicated:
```tex
%% Residual Learning Connection
% b1_conv2 to b6_c1_cropped
\path (b1_conv2-south) -- (b1_conv2-north) coordinate[pos=1.25] (b1_conv2-top) ;
\path (b6_c1_cropped-south)  -- (b6_c1_cropped-north)  coordinate[pos=2.] (b6_c1_cropped-top) ;
\draw [copyconnection]  (b1_conv2-north)  
-- node {\copymidarrow}(b1_conv2-top)
-- node {\copymidarrow}(b6_c1_cropped-top)
-- node {\copymidarrow} (b6_c1_cropped-north);
```
- Like `-east` and `-west` define the right and left sides of an object, `-north` defines the top and `-south` defines the bottom.
- I found the values of the `coordinate[pos=X]` by trial-and-error.
    - I just tried values until the lines were where I wanted them to be. 