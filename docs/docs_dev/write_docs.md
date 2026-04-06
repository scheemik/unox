<a id='top'></a>
# Writing Documentation

This guide describes how to make updates to the documentation while developing the code base.
This guide assumes you have read through the {doc}`Workflow <workflow>` page.
<!-- Note: for linking between documents, use the `doc` role defined in the [Sphinx documentation](https://docs.readthedocs.com/platform/stable/guides/cross-referencing-with-sphinx.html#the-doc-role). 
TLDR: Create a link to a different document by typing `{doc}`, followed by the name of the file surrounded by backticks, excluding the extension. If you would like to change the rendered text of the link, surround the desired link text in backticks, then add the name of the file in angle brackets, in the format: "{doc}`Click here <filename>`".  -->

## Contents

- [Preview documentation changes](#preview_changes)
    - [Live Preview](#live_preview)
- Managing the documentation
    - How did I set up the way it auto updates?
    - Links between internal pages
    - Auto API and why writing good docstrings is important
- [The model diagram](#model_diagram)
    - [Editing the diagram](#edit_diagram)

---
<a id='preview_changes'></a>
[back to top](#top)

## Preview documentation changes

To generate a preview of the documentation before pushing to the GitHub repository, you can run `docs/Makefile` as shown below. Note: it is important to navigate to the `unox/docs/` directory before running the command.

```console
(env_name) username@animus-c:~unox$ cd docs/
(env_name) username@animus-c:~unox/docs$ make html
make html
Running Sphinx v7.4.7
loading translations [en]... done
loading pickled environment... done
myst v3.0.1: MdParserConfig(commonmark_only=False, gfm_only=False, enable_extensions=set(), disable_syntax=[], all_links_external=False, links_external_new_tab=False, url_schemes=('http', 'https', 'mailto', 'ftp'), ref_domains=None, fence_as_directive=set(), number_code_blocks=[], title_to_header=False, heading_anchors=0, heading_slug_func=None, html_meta={}, footnote_transition=True, words_per_minute=200, substitutions={}, linkify_fuzzy_links=True, dmath_allow_labels=True, dmath_allow_space=True, dmath_allow_digits=True, dmath_double_inline=False, update_mathjax=True, mathjax_classes='tex2jax_process|mathjax_process|math|output_area', enable_checkboxes=False, suppress_warnings=[], highlight_code_blocks=True)
myst-nb v1.3.0: NbParserConfig(custom_formats={}, metadata_key='mystnb', cell_metadata_key='mystnb', kernel_rgx_aliases={}, eval_name_regex='^[a-zA-Z_][a-zA-Z0-9_]*$', execution_mode='auto', execution_cache_path='', execution_excludepatterns=(), execution_timeout=30, execution_in_temp=False, execution_allow_errors=False, execution_raise_on_error=False, execution_show_tb=False, merge_streams=False, render_plugin='default', remove_code_source=False, remove_code_outputs=False, scroll_outputs=False, code_prompt_show='Show code cell {type}', code_prompt_hide='Hide code cell {type}', number_source_lines=False, output_stderr='show', render_text_lexer='myst-ansi', render_error_lexer='ipythontb', render_image_options={}, render_figure_options={}, render_markdown_format='commonmark', output_folder='build', append_css=True, metadata_to_fm=False)
Using jupyter-cache at: /home/mschee/unox/docs/_build/.jupyter_cache
[AutoAPI] Reading files... [100%] /home/mschee/unox/src/unox/HPC/legacy/functions_old.py
WARNING: Cannot resolve import of unknown module unox.HPC.data0.paths in unox.data
WARNING: Cannot resolve import of unknown module unox.HPC.data0.latlon in unox.data
WARNING: Cannot resolve import of unknown module unox.HPC.data0.verify_dtype in unox.data
WARNING: Cannot resolve import of unknown module unox.HPC.data0.verify_dataset in unox.data
WARNING: Cannot resolve import of unknown module unox.HPC.data0.dataset in unox.data
WARNING: Cannot resolve import of unknown module unox.HPC.data0.paths in unox.model
WARNING: Cannot resolve import of unknown module unox.HPC.utils in unox.model
WARNING: Cannot resolve import of unknown module unox.HPC.data0.verify_dtype in unox.plot_format
WARNING: Cannot resolve import of unknown module unox.HPC.data0.paths in unox.unox
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
[AutoAPI] Mapping Data... [100%] /home/mschee/unox/src/unox/HPC/legacy/functions_old.py
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

[autosummary] generating autosummary for: CONDUCT.md, CONTRIBUTING.md, analysis.ipynb, autoapi/cleaner-checkpoint/index.rst, autoapi/cleaner/index.rst, autoapi/combine_predictions/index.rst, autoapi/core-checkpoint/index.rst, autoapi/core/index.rst, autoapi/core_new/index.rst, autoapi/core_old/index.rst, ..., example.ipynb, index.md, installation.md, license.md, repo_management.md, run_model.md, troubleshooting.md, unox_CO_docs.ipynb, workflow.md, write_docs.md
building [mo]: targets for 0 po files that are out of date
writing output... 
building [html]: targets for 43 source files that are out of date
updating environment: 5 added, 43 changed, 0 removed
/home/mschee/unox/docs/analysis.ipynb: Executing notebook using local CWD [mystnb]
/home/mschee/unox/docs/analysis.ipynb: Executed notebook in 41.94 seconds [mystnb]
2026-02-18 10:49:35.410797: I external/local_xla/xla/tsl/cuda/cudart_stub.cc:32] Could not find cuda drivers on your machine, GPU will not be used.
2026-02-18 10:49:36.396931: I external/local_xla/xla/tsl/cuda/cudart_stub.cc:32] Could not find cuda drivers on your machine, GPU will not be used.
2026-02-18 10:49:36.973645: E external/local_xla/xla/stream_executor/cuda/cuda_fft.cc:485] Unable to register cuFFT factory: Attempting to register factory for plugin cuFFT when one has already been registered
2026-02-18 10:49:37.458167: E external/local_xla/xla/stream_executor/cuda/cuda_dnn.cc:8454] Unable to register cuDNN factory: Attempting to register factory for plugin cuDNN when one has already been registered
2026-02-18 10:49:37.612055: E external/local_xla/xla/stream_executor/cuda/cuda_blas.cc:1452] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
2026-02-18 10:49:38.746178: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
2026-02-18 10:49:48.873997: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:38] TF-TRT Warning: Could not find TensorRT
/home/mschee/miniconda3/envs/uplt/lib/python3.9/site-packages/proplot/__init__.py:6: UserWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html. The pkg_resources package is slated for removal as early as 2025-11-30. Refrain from using this package or pin to Setuptools<81.
  import pkg_resources as pkg
reading sources... [100%] workflow
/home/mschee/unox/docs/analysis.ipynb:10002: ERROR: Document or section may not begin with a transition.
/home/mschee/unox/docs/autoapi/cleaner-checkpoint/index.rst:29: WARNING: duplicate object description of cleaner-checkpoint.flist, other instance in autoapi/cleaner-checkpoint/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/cleaner-checkpoint/index.rst:31: WARNING: duplicate object description of cleaner-checkpoint.data, other instance in autoapi/cleaner-checkpoint/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/cleaner-checkpoint/index.rst:33: WARNING: duplicate object description of cleaner-checkpoint.flist, other instance in autoapi/cleaner-checkpoint/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/cleaner-checkpoint/index.rst:35: WARNING: duplicate object description of cleaner-checkpoint.data, other instance in autoapi/cleaner-checkpoint/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/cleaner-checkpoint/index.rst:37: WARNING: duplicate object description of cleaner-checkpoint.flist, other instance in autoapi/cleaner-checkpoint/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/cleaner-checkpoint/index.rst:39: WARNING: duplicate object description of cleaner-checkpoint.data, other instance in autoapi/cleaner-checkpoint/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/cleaner/index.rst:29: WARNING: duplicate object description of cleaner.flist, other instance in autoapi/cleaner/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/cleaner/index.rst:31: WARNING: duplicate object description of cleaner.data, other instance in autoapi/cleaner/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/cleaner/index.rst:33: WARNING: duplicate object description of cleaner.flist, other instance in autoapi/cleaner/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/cleaner/index.rst:35: WARNING: duplicate object description of cleaner.data, other instance in autoapi/cleaner/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/cleaner/index.rst:37: WARNING: duplicate object description of cleaner.flist, other instance in autoapi/cleaner/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/cleaner/index.rst:39: WARNING: duplicate object description of cleaner.data, other instance in autoapi/cleaner/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/combine_predictions/index.rst:40: WARNING: duplicate object description of combine_predictions.config_file, other instance in autoapi/combine_predictions/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/data0/dataset/index.rst:79: WARNING: duplicate object description of data0.dataset.uarray.xr, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/data0/dataset/index.rst:82: WARNING: duplicate object description of data0.dataset.uarray.years, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/data0/dataset/index.rst:102: WARNING: duplicate object description of data0.dataset.uarray._verify, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/data0/dataset/index.rst:108: WARNING: duplicate object description of data0.dataset.uarray._get_years, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/data0/dataset/index.rst:111: WARNING: duplicate object description of data0.dataset.uarray._select_year, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/data0/dataset/index.rst:114: WARNING: duplicate object description of data0.dataset.uarray._get_metadata, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/data0/dataset/index.rst:117: WARNING: duplicate object description of data0.dataset.uarray._get_epochs_logs, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/data0/dataset/index.rst:120: WARNING: duplicate object description of data0.dataset.uarray._shift_lons, other instance in autoapi/data0/dataset/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/run_model/index.rst:45: WARNING: duplicate object description of run_model.unet, other instance in autoapi/run_model/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/run_model/index.rst:47: WARNING: duplicate object description of run_model.uarr, other instance in autoapi/run_model/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/run_model/index.rst:49: WARNING: duplicate object description of run_model.years, other instance in autoapi/run_model/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/run_model/index.rst:51: WARNING: duplicate object description of run_model.unet, other instance in autoapi/run_model/index, use :no-index: for one of them
/home/mschee/unox/docs/autoapi/unox/input/index.rst:90: ERROR: Unexpected indentation.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:91: WARNING: Block quote ends without a blank line; unexpected unindent.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:200: CRITICAL: Unexpected section title.

Parameters
----------
/home/mschee/unox/docs/autoapi/unox/input/index.rst:209: CRITICAL: Unexpected section title.

Returns
-------
/home/mschee/unox/docs/autoapi/unox/input/index.rst:220: ERROR: Unexpected indentation.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:221: WARNING: Block quote ends without a blank line; unexpected unindent.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:374: WARNING: Inline literal start-string without end-string.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:374: WARNING: Inline interpreted text or phrase reference start-string without end-string.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:382: WARNING: Definition list ends without a blank line; unexpected unindent.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:384: ERROR: Unexpected indentation.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:387: WARNING: Block quote ends without a blank line; unexpected unindent.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:388: WARNING: Definition list ends without a blank line; unexpected unindent.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:396: ERROR: Unexpected indentation.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:399: WARNING: Block quote ends without a blank line; unexpected unindent.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:405: ERROR: Unexpected indentation.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:407: WARNING: Block quote ends without a blank line; unexpected unindent.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:409: WARNING: Inline literal start-string without end-string.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:409: WARNING: Inline interpreted text or phrase reference start-string without end-string.
/home/mschee/unox/docs/autoapi/unox/input/index.rst:102: ERROR: Unknown target name: "nox".
/home/mschee/unox/docs/autoapi/unox/input/index.rst:233: ERROR: Unknown target name: "tropess_reanalysis_2hr_no2_sfc".
/home/mschee/unox/docs/autoapi/unox/input/index.rst:238: ERROR: Unknown target name: "daily_42602".
/home/mschee/unox/docs/autoapi/unox/input/index.rst:388: ERROR: Unknown target name: "nox".
/home/mschee/unox/docs/autoapi/unox/input/index.rst:399: ERROR: Unknown target name: "tropess_reanalysis_2hr_no2_sfc".
/home/mschee/unox/docs/autoapi/unox/input/index.rst:399: ERROR: Unknown target name: "daily_42602".
/home/mschee/unox/docs/autoapi/unox/plotting/index.rst:487: CRITICAL: Unexpected section title.

Parameters
----------
/home/mschee/unox/docs/autoapi/unox/plotting/index.rst:503: WARNING: Inline strong start-string without end-string.
/home/mschee/unox/docs/autoapi/unox/plotting/index.rst:507: CRITICAL: Unexpected section title.

Returns
-------
/home/mschee/unox/docs/autoapi/unox/plotting/index.rst:514: CRITICAL: Unexpected section title.

Examples
--------
/home/mschee/unox/docs/autoapi/unox/unox/index.rst:39: ERROR: Unexpected indentation.
/home/mschee/unox/docs/autoapi/unox/unox/index.rst:42: WARNING: Block quote ends without a blank line; unexpected unindent.
/home/mschee/unox/docs/index.md:4: WARNING: toctree contains reference to nonexisting document 'these_chapters/*'
looking for now-outdated files... none found
pickling environment... done
checking consistency... /home/mschee/unox/docs/development.md: WARNING: document isn't included in any toctree
/home/mschee/unox/docs/these_chapters/chapter_1.md: WARNING: document isn't included in any toctree
/home/mschee/unox/docs/these_chapters/chapter_2.md: WARNING: document isn't included in any toctree
/home/mschee/unox/docs/these_chapters/chapter_3.md: WARNING: document isn't included in any toctree
/home/mschee/unox/docs/todo_list.md: WARNING: document isn't included in any toctree
/home/mschee/unox/docs/troubleshooting.md: WARNING: document isn't included in any toctree
/home/mschee/unox/docs/unox_CO_docs.ipynb: WARNING: document isn't included in any toctree
/home/mschee/unox/docs/write_docs.md: WARNING: document isn't included in any toctree
done
preparing documents... done
copying assets... 
copying static files... done
copying extra files... done
copying assets: done
writing output... [100%] workflow
/home/mschee/unox/docs/analysis.ipynb:30004: WARNING: 'myst' cross-reference target not found: 'before_you_start' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:30005: WARNING: 'myst' cross-reference target not found: 'exploring_a_dataset' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:30006: WARNING: 'myst' cross-reference target not found: 'jupyter_inspect' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:30007: WARNING: 'myst' cross-reference target not found: 'map_inspect' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:30008: WARNING: 'myst' cross-reference target not found: 'uarray_inspect' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:30009: WARNING: 'myst' cross-reference target not found: 'compare_inputs' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:30010: WARNING: 'myst' cross-reference target not found: 'plotting_results' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:40003: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:100003: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:130002: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:170002: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:260002: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:350003: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/analysis.ipynb:420003: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/autoapi/training/index.rst:17: WARNING: more than one target found for cross-reference 'Unet': core-checkpoint.Unet, core.Unet, core_new.Unet, core_old.Unet, core_tl.Unet
/home/mschee/unox/docs/development.md:11: WARNING: 'myst' cross-reference target not found: 'intro' [myst.xref_missing]
/home/mschee/unox/docs/development.md:18: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/index.md:64: WARNING: 'myst' cross-reference target not found: 'doi.org/10.5194/acp-22-14059-2022' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:6: WARNING: 'myst' cross-reference target not found: 'new_branch' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:7: WARNING: 'myst' cross-reference target not found: 'close_branch' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:8: WARNING: 'myst' cross-reference target not found: 'sync_changes' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:9: WARNING: 'myst' cross-reference target not found: 'pull_request' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:10: WARNING: 'myst' cross-reference target not found: 'review_changes' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:11: WARNING: 'myst' cross-reference target not found: 'clean_repo' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:12: WARNING: 'myst' cross-reference target not found: 'change_env' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:13: WARNING: 'myst' cross-reference target not found: 'create_test_env' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:14: WARNING: 'myst' cross-reference target not found: 'modify_env' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:15: WARNING: 'myst' cross-reference target not found: 'clean_test_env' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:18: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:88: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:95: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:162: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:199: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:225: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:306: WARNING: 'myst' cross-reference target not found: 'on-subsequent-machines' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:335: WARNING: 'myst' cross-reference target not found: 'on-first-machine-only' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:388: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:441: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:467: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/repo_management.md:525: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/these_chapters/chapter_1.md:11: WARNING: 'myst' cross-reference target not found: 'intro' [myst.xref_missing]
/home/mschee/unox/docs/these_chapters/chapter_1.md:18: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/these_chapters/chapter_1.md:4: WARNING: unknown document: 'workflow'
/home/mschee/unox/docs/these_chapters/chapter_2.md:11: WARNING: 'myst' cross-reference target not found: 'intro' [myst.xref_missing]
/home/mschee/unox/docs/these_chapters/chapter_2.md:18: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/these_chapters/chapter_2.md:4: WARNING: unknown document: 'workflow'
/home/mschee/unox/docs/these_chapters/chapter_3.md:11: WARNING: 'myst' cross-reference target not found: 'intro' [myst.xref_missing]
/home/mschee/unox/docs/these_chapters/chapter_3.md:18: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/these_chapters/chapter_3.md:4: WARNING: unknown document: 'workflow'
/home/mschee/unox/docs/todo_list.md:11: WARNING: 'myst' cross-reference target not found: 'intro' [myst.xref_missing]
/home/mschee/unox/docs/todo_list.md:18: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
/home/mschee/unox/docs/workflow.md:11: WARNING: 'myst' cross-reference target not found: 'intro' [myst.xref_missing]
/home/mschee/unox/docs/workflow.md:22: WARNING: 'myst' cross-reference target not found: 'top' [myst.xref_missing]
generating indices... genindex py-modindex done
highlighting module code... [100%] unox.unox
writing additional pages... search done
copying images... [100%] model_diagram.png
dumping search index in English (code: en)... done
dumping object inventory... done
build succeeded, 140 warnings.

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