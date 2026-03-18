<a id='top'></a>
# Repository Management

## Contents

- [Creating a new branch](#new_branch)
- [Closing a branch](#close_branch)
    - [Sync changes across all relevant machines](#sync_changes)
    - [Create a pull request on GitHub](#pull_request)
    - [Review the changes](#review_changes)
    - [Clean up the repository](#clean_repo)
- [Making changes to the virtual environment](#change_env)
    - [Creating a test environment](#create_test_env)
    - [Modifying the environment](#modify_env)
    - [Cleaning up the test environments](#clean_test_env)

---
<a id='new_branch'></a>
[back to top](#top)

## Creating a new branch

When using `git`, it is often very advantageous to develop code in branches.
Using branches allows you to develop features of the code and test things out without overwriting code that you know works.
Generally, the branch called `main` is the default branch and is reserved for code that has been well-tested.

In VSCodium, your current branch is displayed in the bottom left corner, next to the name of your remote connection, if you are on a remote server. 
Clicking on this will display a drop-down with all the available branches.
You can also check the available branches with the following command.

```console
username@<relevant_machine>:~/unox$ git branch
  <an_example_branch>
  <new_branch>
* main
```

The star indicates your current branch.

You can create a new branch using the drop-down in the VSCodium GUI or the following command.

```console
username@<first_machine>:~/unox$ git checkout -b <new_branch>
Switched to a new branch '<new_branch>'
```

This will create `<new_branch>` if it doesn't exist already and switch you to that branch, which you can confirm using the `git branch` command as shown above.

Next, publish the branch to the remote (GitHub) to make it available on other machines.
**<ins>Note: This should only be done on the first machine.</ins>**

```console
username@<first_machine>:~/unox$ git push -u origin <new_branch>
Enter passphrase for key '/home/<username>/.ssh/<id_ed25519>': 
Total 0 (delta 0), reused 0 (delta 0), pack-reused 0
remote: 
remote: Create a pull request for '<new_branch>' on GitHub by visiting:
remote:      https://github.com/<username>/unox/pull/new/<new_branch>
remote: 
remote: GitHub found 124 vulnerabilities on <username>/unox's default branch (2 critical, 35 high, 83 moderate, 4 low). To find out more, visit:
remote:      https://github.com/<username>/unox/security/dependabot
remote: 
To github.com:<username>/unox.git
 * [new branch]      <new_branch> -> <new_branch>
Branch '<new_branch>' set up to track remote branch '<new_branch>' from 'origin'.
```

The warning about vulnerabilities largely have to do with the environment lists from old versions of the code. 
GitHub sees these packages with outdated versions that have known vulnerabilities and assumes they are being used in the actual environment.

On subsequent machines, you can pull this new branch. 
**<ins>Note: This should only be done on subsequent machines after completing the above steps.</ins>**

```console
username@<subsequent_machine>:~/unox$ git pull
Enter passphrase for key '/home/<username>/.ssh/id_GH_23': 
From github.com:<username>/unox
 * [new branch]      <new_branch> -> origin/<new_branch>
Already up to date.
```

Having created this new branch, you can develop the new feature of the code, making commits as you go,without affecting the code in the `main` or other branches. 
For more details on developing the code, see the {doc}`Workflow <workflow>` page. 
If working with others, I recommend each person work on different branches to minimize the likelihood of conflicts.
Communicate with those you are working with on what part of the code you are developing so that you don't work on the same part at the same time. 

---
<a id='close_branch'></a>
[back to top](#top)

## Closing a branch

When you are done developing code on a particular branch `<new_branch>`, you can merge it with `main`.

<a id='sync_changes'></a>
[back to top](#top)

### Sync changes across all relevant machines

When merging branches, it is important to make sure no outstanding changes are left.
You can check this by looking in the "Source Control" panel in VSCodium, or running `git status` on the relevant machine.

```console
username@<relevant_machine>:~/unox$ git status
On branch <new_branch>
Your branch is up to date with 'origin/<new_branch>'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   example_file.txt
        modified:   new_directory/another_example_file.txt

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        a_new_file.txt
        new_directory/another_new_file.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

Before attempting to merge a branch, make sure there are no files under `Changes not staged for commit:`.
Files which have already been tracked and have since been changed will be listed here. 
They also show up in the "Source Control" panel in VSCodium with either an orange `M` if modified or a red `D` if deleted. 
Relevant modifications are any changes to a file's content as well as moving, renaming, or deleting a file that was already tracked.
To resolve the changes, follow these steps:

1. Commit any changes you want to include in the branch.
2. Revert any changes you do not want to keep.
3. If any changes remain, use the command `git stash` to safely store them in your stash. This allows `git` to merge branches without needing to resolve un-committed changes, and these changes can be reapplied later, perhaps on a different branch.

```console
username@<relevant_machine>:~/unox$ git stash
Saved working directory and index state WIP on <new_branch>: 489067a <commit message>
```

Any new files that you've created (listed under `Untracked files:` when checking the status above) are not stashed as they are not yet tracked by `git` and will be ignored in the merging process.
Untracked files appear in the "Source Control" panel with a green `U`.

When checking the status above, the output included the line `Your branch is up to date with 'origin/<new_branch>'.`. 
If that was not the case for you, push and pull until you are up to date with the remote.
If this is the first time you have pushed `<new_branch>`, you may need to run the following command:
```console
username@<relevant_machine>:~/unox$ git push -u origin <new_branch>
Enter passphrase for key '/home/<username>/.ssh/<id_ed25519>': 
Total 0 (delta 0), reused 0 (delta 0), pack-reused 0
remote: 
remote: Create a pull request for '<new_branch>' on GitHub by visiting:
remote:      https://github.com/<username>/unox/pull/new/<new_branch>
remote: 
remote: GitHub found 124 vulnerabilities on <username>/unox's default branch (2 critical, 35 high, 83 moderate, 4 low). To find out more, visit:
remote:      https://github.com/<username>/unox/security/dependabot
remote: 
To github.com:<username>/unox.git
 * [new branch]      <new_branch> -> <new_branch>
Branch '<new_branch>' set up to track remote branch '<new_branch>' from 'origin'.
```
Here, the `-u` flag is short for `--set-upstream`. 

**<ins>Note: It is important to repeat the process above on all relevant machines (Animus, HPC, etc.) where you have developed the code on `<new_branch>`.</ins>**

<a id='pull_request'></a>
[back to top](#top)

### Create a pull request on GitHub

Log into GitHub and go to the [repository page for `unox`](https://github.com/<username>/unox). 
If you have recently pushed changes, you may see a button that says "<ins>Compare & pull request</ins>" which you can click to get the process started.
If that button doesn't appear, click the "<ins>Pull requests</ins>" tab, then the "<ins>New pull request</ins>" button. 

On the "<ins>Compare changes</ins>" page, make sure that the `base:` branch is set to `main` and the `compare:` branch is set to `<new_branch>`. 
When this is set, you should see a chronological list of all the commit messages you have made on `<new_branch>`. 
Click the "<ins>Create pull request</ins>" button.

On the "<ins>Open a pull request</ins>" page, you will be able to document the pull request you are making to merge your changes. 
Add a title and description following the [Angular Commit Style Guide](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines). For example, the title and description for [pull request #25](https://github.com/scheemik/unox/pull/25) was:

> **Title:**  
> feat: run ensembles of runs and plot their statistics
> 
> **Description:**  
> feat: add ensemble size `-e N` arg to `HPC_job_submit.sh` to run `N` of the same job with the same parameters.  
> refactor: remove option to use `.npy` files for input and output in favor of `.nc` files.  
> feat: add functionality to `HPC_to_animus.sh` to automatically merge `predictions.nc` files from all ensemble members into one.  
> perf: add function to `HPC_slurm.sh` to automatically remove all but most recent checkpoint when a job completes to save on storage space.  
> feat: add box-and-whisker plotting function to show R^2 and RMSE across ensemble runs.  
> fix: replace username with variable from `HPC_params.sh` to enable other users to submit jobs.  
> refactor: move code from `run_model.py` to new `training.py` module.  
> docs: add comments in `begin_training()` to describe the logging, early stopping, and checkpoint functions for model runs.   
> feat: add plotting function to show `loss`, `r2_keras`, etc. as a function of training epoch for model runs.  

The description can repeat exactly some of the commit messages you wrote, but try to summarize rather than repeating all the commit messages. 

In the sidebar, under "<ins>Assignees</ins>", assign someone to review your code.
If you are currently working on this project alone, you can assign yourself.

Click the "<ins>Create pull request</ins>" button.

<a id='review_changes'></a>
[back to top](#top)

### Review the changes

Wait for the person you assigned to review your pull request. 
When reviewing someone else's pull request, make sure to load their branch on your environment and test the new functionality. 
Be sure to give specific and constructive feedback.
If needed, request fixes for any bugs you find. 

At the bottom of the pull request page, there will be a status. 
GitHub automatically checks whether you can merge the branch without conflicts. 
If there are conflicts to merge, take a look at GitHub's guide [Resolving a merge conflict](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-on-github).
If you can merge without conflicts, click the dropdown on the "<ins>Merge pull request</ins>" button and select "<ins>Create a merge commit</ins>".
This will prompt you to add a title and description to the merge commit.
It will automatically fill it with information, but make sure it follows this format:

> **Commit message:**  
> pr: Merge pull request #25 from `<username>/<new_branch>`
> 
> **Extended Description:**   
> `<title of the pull request from above>`

Most of the time, the only change to make is to add "<ins>pr: </ins>" at the beginning of the commit message.
Next, click the "<ins>Confirm merge</ins>" button. 

<a id='clean_repo'></a>
[back to top](#top)

### Clean up the repository

Once you have merged `<new_branch>`, it is time to clean up the repository. 
On the same page where you clicked "Confirm merge", you should now see an option to "<ins>Delete branch</ins>".
Click this button to delete the branch from the remote repository on GitHub.

Next, on the relevant machine, go to the `main` branch. 
Since `<new_branch>` was merged with `main` then deleted on remote, you want to make sure you are on `main` before syncing the merge to the relevant machine. 
Checkout the `main` branch by using the GUI in VSCodium, or the command below.

```console
username@<relevant_machine>:~/unox$ git checkout main
Updating files: 100% (27/27), done.
Switched to branch 'main'
Your branch is up to date with 'origin/main'.
```

Either way you choose, you should see `main` as the current branch in the lower left corner of the VSCodium window, or, when running the command below, you should see a star next to `main`.

```console
username@<relevant_machine>:~/unox$ git branch
  <an_example_branch>
  <new_branch>
* main
```

Next, pull the changes from the remote (note that this is the step where you might run into issues if you had kept unstaged changes).
Here's an example of the kind of output you would expect to see.

```console
username@<relevant_machine>:~/unox$ git pull
Enter passphrase for key '/home/<username>/.ssh/<id_ed25519>': 
remote: Enumerating objects: 1, done.
remote: Counting objects: 100% (1/1), done.
remote: Total 1 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
Unpacking objects: 100% (1/1), 931 bytes | 20.00 KiB/s, done.
From github.com:<username>/unox
   ae7ece4..c050c9b  main       -> origin/main
Updating ae7ece4..c050c9b
Fast-forward
 HPC_CPU_slurm.sh                                |   1 +
 HPC_GPU_slurm.sh                                |   1 +
 HPC_from_animus.sh                              |   2 +-
 HPC_job_submit.sh                               | 176 +++++++++++---
 HPC_params.sh                                   |  54 ++++-
 ...
 tests/test_HPC/test_data0/test_dataset.py       |  66 +++++
 tests/test_evaluate.py                          | 103 ++++++++
 tests/test_plotting.py                          | 167 +++++++++++++
 26 files changed, 2209 insertions(+), 697 deletions(-)
 create mode 100644 src/unox/HPC/combine_predictions.py
 rename src/unox/HPC/{utils => legacy}/functions_old.py (100%)
 create mode 100644 src/unox/HPC/training.py
 create mode 100644 src/unox/evaluate.py
 create mode 100644 tests/test_evaluate.py
 create mode 100644 tests/test_plotting.py
```

Then, delete `<new_branch>` locally with the command below.

```console
username@<relevant_machine>:~/unox$ git branch -d <new_branch>
Deleted branch <new_branch> (was 489067a).
```

Next, prune the now-obsolete remote tracking branches with the command below.

```console
username@<relevant_machine>:~/unox$ git fetch origin --prune
Enter passphrase for key '/home/<username>/.ssh/<id_ed25519>': 
From github.com:<username>/unox
 - [deleted]         (none)     -> origin/<new_branch>
```

**<ins>Note: It is important to repeat the above process on all relevant machines (Animus, HPC, etc.) where you have developed the code on `<new_branch>`.</ins>**

Below repeats many of the steps under [Creating a new branch](#new_branch), however includes the commands needed to restore any changes you may have saved with the `git stash` command. 

#### On first machine only

**<ins>Note: This should only be done from the first machine. For subsequent machines, skip to [On subsequent machines](#on-subsequent-machines).</ins>**

Create a new branch for the next part of the code you want to develop and switch to it, either using the GUI in VSCodium or the following command.

```console
username@<first_machine>:~/unox$ git checkout -b <my_next_branch>
Switched to a new branch '<my_next_branch>'
```

Publish this new branch to the remote either using the GUI in VSCodium or the following command. 

```console
username@<first_machine>:~/unox$ git push -u origin <my_next_branch>
Enter passphrase for key '/home/<username>/.ssh/<id_ed25519>': 
Total 0 (delta 0), reused 0 (delta 0), pack-reused 0
remote: 
remote: Create a pull request for '<my_next_branch>' on GitHub by visiting:
remote:      https://github.com/<username>/unox/pull/new/<my_next_branch>
remote: 
remote: GitHub found 124 vulnerabilities on <username>/unox's default branch (2 critical, 35 high, 83 moderate, 4 low). To find out more, visit:
remote:      https://github.com/<username>/unox/security/dependabot
remote: 
To github.com:<username>/unox.git
 * [new branch]      <my_next_branch> -> <my_next_branch>
Branch '<my_next_branch>' set up to track remote branch '<my_next_branch>' from 'origin'.
```

#### On subsequent machines

**<ins>Note: This should only be done on subsequent machines after completing the steps in [On first machine only](#on-first-machine-only).</ins>**

Pull the new remote branch created on and published from the first machine.

```console
username@<subsequent_machine>:~/unox$ git pull
Enter passphrase for key '/home/<username>/.ssh/id_GH_23': 
From github.com:<username>/unox
 * [new branch]      <my_next_branch> -> origin/<my_next_branch>
Already up to date.
```

Create a local copy of the remote branch and check it out, either using the GUI in VSCodium or the following command. 

```console
username@<subsequent_machine>:~/unox$ git switch <my_next_branch>
branch '<my_next_branch>' set up to track 'origin/<my_next_branch>'.
Switched to a new branch '<my_next_branch>'
```

#### On each relevant machine

Finally, pop your stashed changes onto this new branch with the command below, <ins>only if you stashed changes earlier</ins>.

```console
username@<relevant_machine>:~/unox$ git stash pop
On branch <my_next_branch>
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   plot_tests.ipynb
        modified:   pyproject.toml

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        HPC_test.sh
        docs/env_package_lists/Trillium_pip_list.txt
        docs/env_package_lists/to_delete0_list.txt
        docs/env_package_lists/to_delete2_list.txt
        docs/env_package_lists/uplt_list.txt
        docs/repo_management.md
        docs/troubleshooting.md
        docs/write_docs.md
        poetry_to_delete0.lock_file
        poetry_to_delete1.lock_file
        poetry_uplt.lock_file
        test.py

no changes added to commit (use "git add" and/or "git commit -a")
Dropped refs/stash@{0} (4b120a52276a41068d32a5386f21e0d9e28d13e0)
```

---
<a id='change_env'></a>
[back to top](#top)

## Making changes to the virtual environment

You may find that you need to make modifications to the `conda` environment on Animus. 
Below is an example of doing so with instructions on how to create temporary environments to test changes before committing them.

The `conda` environment on Animus is built from the specifications in the `pyproject.toml` file which contains rules such as those shown below about which versions of packages to use.

```toml
...
[tool.poetry.dependencies]
python = ">=3.9, <3.13"
pandas = "<2"
proplot = ">=0.9.7"
cartopy = ">=0.21.1"
basemap = ">=1.4.1"
xarray = ">=2022.11.0"
scipy = ">=1.8.1"
matplotlib = ">=3.4.3"
netcdf4 = ">=1.6.2"
numpy = "<2"
tensorflow = "2.17.0"
setuptools = "<81"
jupyter = "^1.1.1"


[tool.poetry.group.dev.dependencies]
pytest = "^8.3.5"
pytest-cov = "^6.1.1"
myst-nb = "^1.2.0"
sphinx-autoapi = "^3.6.0"
sphinx-rtd-theme = "^3.0.2"
cdsapi = ">=0.7.7"
...
```

This list of packages is much shorter than the one you will see by running `pip list` with the environment activated.
That is because the list above only specifies the needed packages for the project, however each of those packages specify their own list of dependencies. 
When creating the environment as shown in the {doc}`Installation <../docs_setup/installation>` guide, the `poetry` package uses the list in `pyproject.toml` to determine the full list of packages and their versions to install. 
This depends on the developers of each of those packages to have correctly defined their own dependencies. 

Under the `dev` group of dependencies in `pyproject.toml` is the `jupyter` package. 
In order to allow [`matplotlib`](https://matplotlib.org/) to display plots in-line with Jupyter notebook cells, it depends on the package [`matplotlib-inline`](https://github.com/ipython/matplotlib-inline). 

Using the `pyproject.toml` shown above, `poetry` will install version 0.2.0 (or higher) of `matplotlib-inline`, following the dependency tree of other packages. 
However, all versions 0.2.0 or higher, when used in conjunction with `matplotlib` version 3.4.3, will result in the following error when trying to plot something in a Jupyter notebook:

```console
AttributeError: module 'matplotlib' has no attribute '__version_info__'
```

<a id='create_test_env'></a>
[back to top](#top)

### Creating a test environment

Before making changes to the packages in your main `conda` environment, I highly recommend making a new `conda` environment in which to test out the new build.

To create a new `conda` environment, follow the instructions in the {doc}`Installation <../docs_setup/installation>` guide under "Creating virtual environments" -> "Virtual environment on Animus" -> "Creating the `conda` environment on Animus with `poetry`", using a new, unique environment name.

Remember to remove the `poetry.lock` file.

Here, I created `<test_env>`, activated it, installed `poetry`, ran `poetry install`, and confirmed with `pip list` that version 0.2.1 of `matplotlib-inline` was installed.

```console
(<test_env>) username@animus-c:~/unox$ pip list
Package                       Version     Editable project location
----------------------------- ----------- -------------------------
...
matplotlib                    3.4.3
matplotlib-inline             0.2.1
...
```

To test this, make sure to select `<test_env>` as the kernel in your Jupyter notebook.
Attempting to plot in-line with `matplotlib` will result in the error described above.

<a id='modify_env'></a>
[back to top](#top)

### Modifying the environment

The solution to this particular issue is to specify that `unox` should install a version of `matplotlib-inline` less than 0.2.0.
This can be done by editing `pyproject.toml` directly, but I would recommend running the following command as it will automatically update the environment.

```console
(<test_env>) username@animus-c:~/unox$ poetry add matplotlib-inline="<0.2.0" --dev

Updating dependencies
Resolving dependencies... (3.4s)

Package operations: 0 installs, 1 update, 0 removals

  - Downgrading matplotlib-inline (0.2.1 -> 0.1.7)

Writing lock file
```

I added the `--dev` flag so `poetry` will add it to the development group of dependencies. 
If you wish to make a change to the main group of dependencies, remove that flag.

The `pyproject.toml` now looks like this:

```toml
...
[tool.poetry.dependencies]
python = ">=3.9, <3.13"
pandas = "<2"
proplot = ">=0.9.7"
cartopy = ">=0.21.1"
basemap = ">=1.4.1"
xarray = ">=2022.11.0"
scipy = ">=1.8.1"
matplotlib = ">=3.4.3"
netcdf4 = ">=1.6.2"
numpy = "<2"
tensorflow = "2.17.0"
setuptools = "<81"
jupyter = "^1.1.1"
matplotlib-inline = "<0.2.0"


[tool.poetry.group.dev.dependencies]
pytest = "^8.3.5"
pytest-cov = "^6.1.1"
myst-nb = "^1.2.0"
sphinx-autoapi = "^3.6.0"
sphinx-rtd-theme = "^3.0.2"
cdsapi = ">=0.7.7"
...
```

To test this change, be sure to restart the kernel in your Jupyter notebook. 
If everything is running well, make the same changes to your main `conda` environment.

<a id='clean_test_env'></a>
[back to top](#top)

### Cleaning up the test environments

Once you have your main `conda` environment running correctly, I recommend clearing out the test environments you created in this process.
As a reminder, you can list the existing environments using the following command.

```console
(base) username@animus-c:~/unox$ conda env list

conda environments:

base                 * /home/<username>/miniconda3
test_env0              /home/<username>/miniconda3/envs/test_env0
test_env1              /home/<username>/miniconda3/envs/test_env1
test_env2              /home/<username>/miniconda3/envs/test_env2
unet                   /home/<username>/miniconda3/envs/unet
uplt                   /home/<username>/miniconda3/envs/uplt
```

Make sure the environment you currently have activated is not one you want to delete. 
**<ins>Do not remove the `base` environment</ins>**

For each `<test_env>` you want to remove, run the following command, which can take several minutes to complete, depending on the size of the environment.
You will be prompted twice to confirm removal of the environment.

```console
(base) username@animus-c:~/unox$ conda remove --name <test_env> --all

Remove all packages in environment /home/mschee/miniconda3/envs/to_delete0:


## Package Plan ##

  environment location: /home/mschee/miniconda3/envs/to_delete0


The following packages will be REMOVED:

  _libgcc_mutex-0.1-main
  _openmp_mutex-5.1-1_gnu
  anyio-4.10.0-pyhe01879c_0
  backports-1.0-pyhd8ed1ab_5
  ...
  zipp-3.23.0-pyhd8ed1ab_0
  zlib-1.3.1-hb25bd0a_0
  zstandard-0.23.0-py39hd399759_3


Proceed ([y]/n)? y


Downloading and Extracting Packages:

Preparing transaction: done
Verifying transaction: done
Executing transaction: done
Everything found within the environment (/home/mschee/miniconda3/envs/to_delete0), including any conda environment configurations and any non-conda files, will be deleted. Do you wish to continue?
 (y/[n])? y


```

Confirm that the environment has been removed using the following command.

```console
(base) username@animus-c:~/unox$ conda env list

conda environments:

base                 * /home/<username>/miniconda3
unet                   /home/<username>/miniconda3/envs/unet
uplt                   /home/<username>/miniconda3/envs/uplt
```