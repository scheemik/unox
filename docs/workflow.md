<a id='top'></a>
# Workflow

The documentation below describes a workflow to actively develop the code base.
This guide assumes you have read through the {doc}`Installation <installation>`, {doc}`Data <data>`, and {doc}`Running the model <run_model>` pages.
<!-- Note: for linking between documents, use the `doc` role defined in the [Sphinx documentation](https://docs.readthedocs.com/platform/stable/guides/cross-referencing-with-sphinx.html#the-doc-role). 
TLDR: Create a link to a different document by typing `{doc}`, followed by the name of the file surrounded by backticks, excluding the extension. If you would like to change the rendered text of the link, surround the desired link text in backticks, then add the name of the file in angle brackets, in the format: "{doc}`Click here <filename>`".  -->

## Contents

- [Introduction](#intro)
- Writing functions
    - Separating into modules
    - Verifying input arguments
    - Writing docstrings
- Using a Jupyter notebook for initial testing
- Writing tests
    - Using the "Testing" panel in VSCodium
    - Using `pytest`

---
<a id='intro'></a>
[back to top](#top)

## Introduction
