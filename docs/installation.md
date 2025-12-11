<a id='top'></a>
# Installation

The documentation below describe how to install this package to enable active development. 
If you are interested in simply using `unox`, refer to the installation instructions in the {doc}`README <index>`.
<!-- Note: for linking between documents, use the `doc` role defined in the [Sphinx documentation](https://docs.readthedocs.com/platform/stable/guides/cross-referencing-with-sphinx.html#the-doc-role). 
TLDR: Create a link to a different document by typing `{doc}`, followed by the name of the file surrounded by backticks, excluding the extension. If you would like to change the rendered text of the link, surround the desired link text in backticks, then add the name of the file in angle brackets, in the format: "{doc}`Click here <filename>`".
In order to link to the README file as I did above, I need to actually link to the `index.html` file which is in the same directory as this current file. Linking to a file up the directory structure is difficult, but the README is included in the `index.html` file, and therefore I can link to it that way.  -->

## Contents

- [Introduction](#intro)
- [Remote connections](#connecting)
    - [Connecting to HPC](#hpc_connect)
    - [Connecting to Animus](#animus_connect)
- [Initializing the repository](#init_repo)
    - [Connecting to GitHub](#connect_to_github)
    - [Cloning the GitHub repository](#clone_github_repo)
- [Creating virtual environments](#create_venvs)
    - [Virtual environment on Trillium](#HPC_venv)
    - [Virtual environment on Animus](#animus_venv)
        - [Installing `miniconda` on Animus](#animus_conda)
        - [Creating the `conda` environment on Animus with `poetry`](#animus_poetry)

---
<a id='intro'></a>
[back to top](#top)

## Introduction

This document details the initial steps required to set up the environments necessary to develop this code base and run the model on a High-Performance Computing (HPC) cluster.
Command line prompts that are to be entered into a terminal as part of this process are shown here in `console` blocks like this:
```console
username@local:~/$ pwd
/Users/username
```
where `username` would correspond to the username on the `local` machine. 
In this guide, the three machines that are referenced are `local` (the computer in front of you), `animus-c`, and `HPC` (the HPC cluster). 
All command prompts assume a unix-based system (ex: Linux or MacOS). 
If your local machine runs Windows, you will need to modify the `local` commands. 
The machine in each console prompt indicates where the command is supposed to be executed. 
Command prompts in these `console` blocks are shown on lines which start with the username and the machine.
Expected output is shown on subsequent lines.
When executing a command, only enter what is shown in prompt lines after the `$`.
For example, for the block above, you would enter only `pwd` into your console, not `username@local:~/$ pwd`.

In some cases, it is important to have a particular virtual environment activated when executing a command. 
This will be indicated by the name of the virtual environment appearing in parentheses before the username. For example:
```console
(my_venv) username@HPC:~/$ pip list
```

---
<a id='connecting'></a>
[back to top](#top)

## Remote connections

For this project, we are using two different remote machines:
- `animus-c`
    - Hosted in the Physics Department.
    - Used for developing the code and analyzing the results of model runs.
- [Trillium](https://docs.alliancecan.ca/wiki/Trillium)
    - HPC cluster run by SciNet / Compute Canada / Digital Research Alliance of Canada. 
    - Used to run the model with GPU resources.

Below, we detail how to setup `ssh` connections to each of these remote machines and save their configurations to make connecting to them via VSCodium (or VSCode) easier.

<a id='hpc_connect'></a>
[back to top](#top)

### Connecting to HPC

If you do not already have access to Trillium, follow the steps below.

#### Verify Digital Research Alliance account

Go to the [Digital Research Alliance of Canada website](https://ccdb.alliancecan.ca/security/login) and verify that you can log in. 
Once logged in, check your active roles and ensure you are sponsored by your supervisor. 
If not, request access by going to "My Acount" -> "Apply for New Role" using your supervisor's CCRI.

#### SSH into Trillium

In order to access Trillium, you will need to create an ssh authentication key and set up 2-factor authentication. 
Following the [Alliance docs](https://docs.alliancecan.ca/wiki/Using_SSH_keys_in_Linux) (assuming you have a unix-based system), generate a key pair on your local computer with:
```console
username@local:~/$ ssh-keygen -t ed25519
```

Then, as described in [this Alliance docs page](https://docs.alliancecan.ca/wiki/SSH_Keys), log in to Alliance at the [SSH authorized keys page](https://ccdb.computecanada.ca/ssh_authorized_keys). 
Then, copy and paste in your public key by using the output of this command:
```console
username@local:~/$ cat ~/.ssh/<id_ed25519>.pub
```
where `<id_ed25519>` is the name of the key you generated (default is usually just `id_ed25519.pub`). 
It might take about 30 minutes for the changes to take place and allow you to connect via SSH.

Next, verify that you can access Trillium through the command line. 
Open a terminal and use the following command, replacing `<SSH_id>` with the path to your authentication file (default is `~/.ssh/id_ed25519`) and `<username>` with your user name:
```console
username@local:~/$ ssh -XY -i <SSH_id> <username>@trillium-gpu.alliancecan.ca
```
Be sure to log in to `trillium-gpu`, and not just `trillium` as you will need access to the GPU resources.

Once that works, I suggest adding the following lines to your local `~/.bashrc` file to make an alias command:
```bash
# In username@local:/Users/username/.bashrc
SSH_id=<SSH_id>
alias trillium="ssh -XY -i $SSH_id <username>@trillium-gpu.alliancecan.ca"
```
That way, after saving and sourcing the `~/.bashrc` file (by running `source ~/.bashrc`), you can just type `trillium` in the terminal to log in.

Note that, upon logging in to `trillium`, you will always be put into your home directory (`/home/<username>`, which you can check with the `pwd` command). 
However, following the recommendations of SciNet, you will want to always work in your "scratch" directory, which will be `scratch/<username>` (we'll make an alias to get there quickly later).

You should also find your local SSH configuration file `~/.ssh/config`, or create it if it doesn't exist already, and add the following:
```bash
# In username@local:/Users/username/.ssh/config
HOST trillium
  HOSTNAME trillium-gpu.alliancecan.ca
  User <username>
  IdentityFile <SSH_id>
```
This will essentially tell your computer how to build the command you added to your `~/.bashrc` file above where `HOST` can be whatever you want (essentially the name of the alias command), `HOSTNAME` is the server (what comes after the `@`), `User` is your user name `<username>`, and `IdentityFile` is the path to the authentication key you made for Trillium above. 
Note that the last argument is _Identity_ File, not _Identify_ File. 
This step will become important when connecting via VSCodium later. 
But, it also allows you to connect to Trillium with the following command (in case you prefer that over the alias in `~/.bashrc` mentioned above):
```console
username@local:~/$ ssh trillium
```

<a id='hpc_clone'></a>
[back to top](#top)

### Connecting to Animus

Your supervisor in the Physics Department will set you up with access to `animus-c`. 
Once that is done, verify that you can access `animus-c` through the command line. 
Open a terminal and use the following command, replacing `<username>` with your user name:
```console
username@local:~/$ ssh <username>@animus-c.atmosp.physics.utoronto.ca
```
As with connecting to HPC, I would suggest adding the following alias to your `.bashrc`:
```bash
# In username@local:/Users/username/.bashrc
alias animus="ssh <username>@animus-c.atmosp.physics.utoronto.ca"
```
Again, as with HPC, and add the following to your SSH configuration file `~/.ssh/config`:
```bash
# In username@local:/Users/username/.ssh/config
HOST animus
  HOSTNAME animus-c.atmosp.physics.utoronto.ca
  User <username>
```

---
<a id='init_repo'></a>
[back to top](#top)

## Initializing the repository

The code for this project is hosted on GitHub at [https://github.com/scheemik/unox](https://github.com/scheemik/unox).

<a id='connect_to_github'></a>
[back to top](#top)

### Connecting to GitHub

In order to connect to GitHub to allow cloning the code repository as well as pushing and pulling changes during development, you'll need to set up authentication keys between GitHub and each remote machine.
This is similar to what is shown in [Connecting to HPC](#hpc_connect).

GitHub has an entire series of guides on [Connecting to GitHub with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).
If you are curious to learn more about `ssh` or are not sure whether you already have a key for GitHub, I would recommend working through those guides in order.

If you know you do not already have a key for GitHub, open the guide for [Generating a new SSH key and adding it to the ssh-agent](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent?platform=linux). 
In these instructions, you will be asked to enter an email address (below referred to as `<user@mail.ca>`) and select a file name for the SSH key (below referred to as `<GH_id>`, the default being `~/.ssh/id_ed25519`).
Follow that guide, entering the suggested commands first from Trillium, then from Animus, making sure you have selected the "Linux" version of the guide as the webpage will default to the system on which you are viewing it.

Next, follow the GitHub guide for [Adding a new SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).

Then, you can follow the guide on [Testing your SSH connection](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection) to make sure you can connect to GitHub from each remote machine.
This amounts to first activating your authentication key:
```console
username@<animus-c or HPC>:~/$ eval $(ssh-agent -s); ssh-add ~/.ssh/<GH_id>
Agent pid 669646
Enter passphrase for /home/<username>/.ssh/<GH_id>: 
Identity added: /home/<username>/.ssh/<GH_id> (<user@mail.ca>)
```
Then, attempting to connect to `git@github.com`:
```console
username@<animus-c or HPC>:~/$ ssh git@github.com
Enter passphrase for key '/home/<username>/.ssh/<GH_id>': 
PTY allocation request failed on channel 0
Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.
Connection to github.com closed.
```

If you see similar output, you are now ready to clone the repository and will be able to push and pull changes while developing the code.
Remember to do this for both Trillium _and_ Animus!

<a id='clone_github_repo'></a>
[back to top](#top)

### Cloning the GitHub repository

#### Trillium

According to the [Trillium Quickstart](https://docs.alliancecan.ca/wiki/Trillium_Quickstart) page:
> "Job output must be written to the scratch file system"

The code is set up to save model run output to the same directory as the repository. 
For this reason, make sure to clone the repository into the `scratch` filesystem. 
You may choose to create a new directory within which to clone the repository, but this is optional:
```console
username@HPC:~/$ cd /scratch/<username>/<optional_directory>/
username@HPC:$ git clone git@github.com:scheemik/unox.git
Cloning into 'unox'...
Enter passphrase for key '/home/<username>/.ssh/<GH_id>': 
remote: Enumerating objects: 2995, done.
remote: Counting objects: 100% (942/942), done.
remote: Compressing objects: 100% (466/466), done.
remote: Total 2995 (delta 426), reused 645 (delta 366), pack-reused 2053 (from 1)
Receiving objects: 100% (2995/2995), 194.17 MiB | 64.12 MiB/s, done.
Resolving deltas: 100% (1768/1768), done.
Updating files: 100% (102/102), done.
```
This creates a directory called `unox` and clones the contents of the repository into it.

For ease of navigation, I suggest adding the following alias to your HPC `~/.bashrc`:
```bash
# In username@HPC:/home/username/.bashrc
alias cdproj='cd $SCRATCH/<optional_directory>/unox/'
```
Then, after sourcing `~/.bashrc`, you can execute the command `cdproj` to automatically navigate to the project directory.

#### Animus

Navigate to a directory location in which you have write permissions (ex: your home directory) and clone the repository:

```console
username@animus-c:~/$ git clone git@github.com:scheemik/unox.git
Cloning into 'unox'...
Enter passphrase for key '/home/<username>/.ssh/<GH_id>': 
remote: Enumerating objects: 2995, done.
remote: Counting objects: 100% (942/942), done.
remote: Compressing objects: 100% (466/466), done.
remote: Total 2995 (delta 426), reused 645 (delta 366), pack-reused 2053 (from 1)
Receiving objects: 100% (2995/2995), 194.17 MiB | 64.12 MiB/s, done.
Resolving deltas: 100% (1768/1768), done.
Updating files: 100% (102/102), done.
```

---
<a id='create_venvs'></a>
[back to top](#top)

## Creating virtual environments

A virtual environment is a way to install all the correct software dependencies needed for a project in a separate, siloed environment. 
That way, you can have multiple environments for different projects and, if you update the version of a software package in one environment, you don't need to worry about that breaking the code in a different environment.
The two remote machines, Trillium and Animus, are used for different parts of this project and therefore have different virtual environments. 

<a id='HPC_venv'></a>
[back to top](#top)

### Virtual environment on Trillium

Anaconda is one way of creating virtual environments, which we will use on [Animus](#animus_venv). 
However, Digital Alliance Canada very [explicitly asks you to not install Anaconda on their systems](https://docs.alliancecan.ca/wiki/Anaconda/en). 
So, we will use a similar method called `virtualenv`.

The Digital Alliance wiki has instructions for [Creating and using a virtual environment](https://docs.alliancecan.ca/wiki/Python#Creating_and_using_a_virtual_environment). 
They actually suggest [Creating a virtual environment inside of your jobs](https://docs.alliancecan.ca/wiki/Python#Creating_virtual_environments_inside_of_your_jobs), however I was unable to get that to work. 
They suggest that creating a new environment every time might actually speed up performance, but it is more important for the code to run consistently.

To see what environments you have created on Trillium, run:
```
console
username@HPC:~/$ ls /home/<username>/.virtualenvs/
unoxTrillium  unoxTrilliumNC  unoxTrilliumTest
```
If you haven't created a virtual environment on Trillium before, this output might be empty or the `.virtualenvs/` directory might not exist yet. 

The following commands will create the exact virtual environment the code expects to run in:
```console
username@HPC:~/$ module load StdEnv/2023 gcc/12.3 python/3.12.4 cuda/12.6 hdf5/1.14.2 netcdf/4.9.2 mpi4py/4.0.0
username@HPC:~/$ virtualenv --no-download /home/<username>/.virtualenvs/unoxTrilliumNC
username@HPC:~/$ source /home/<username>/.virtualenvs/unoxTrilliumNC/bin/activate
(unoxTrilliumNC) username@HPC:~/$ pip install --no-index --upgrade pip
(unoxTrilliumNC) username@HPC:~/$ pip install --no-index 'tensorflow==2.17.0'
(unoxTrilliumNC) username@HPC:~/$ pip install --no-index 'xarray==2024.3.0'
(unoxTrilliumNC) username@HPC:~/$ pip install --no-index 'netcdf4==1.7.2'
```
<!-- TODO: Add the output of each command in collapsible section. -->

<!-- TODO: Add explanation of each module I load, the creation and sourcing of the venv, and for each of the packages I install and what dependencies come with them. -->

<details>

<summary>Expand for details and example output</summary>

#### Modules

Trillium, like many Alliance clusters, uses [Environment Modules](https://docs.alliancecan.ca/wiki/Utiliser_des_modules/en) to load software that has been already installed and configured. 
The first command in creating the virtual environment above loads all the necessary modules:
```console
username@HPC:~/$ module load StdEnv/2023 gcc/12.3 python/3.12.4 cuda/12.6 hdf5/1.14.2 netcdf/4.9.2 mpi4py/4.0.0
```

The required modules are loaded in this order specifically:
- `StdEnv/2023` 
- `gcc/12.3 `
- `python/3.12.4` 
    - This determines the version of Python used to create the virtual environment.
    - Python 3.12 was selected because, at least at the time, `tensorflow` didn't support any more up-to-date version of Python. 
- `cuda/12.6` 
- `hdf5/1.14.2` 
- `netcdf/4.9.2` 
- `mpi4py/4.0.0`

#### Creating the virtual environment

The next command actually creates the virtual environment:
```console
username@HPC:~/$ virtualenv --no-download /home/<username>/.virtualenvs/unoxTrilliumNC
```

The name of the environment, `unoxTrilliumNC` could be anything, but this is the name that is expected in the code when activating the environment in `HPC_slurm.sh`. 

#### Activating the virtual environment

The next command activates the virtual environment:
```console
username@HPC:~/$ source /home/<username>/.virtualenvs/unoxTrilliumNC/bin/activate
```

This is important to do before installing any packages as to not affect your base environment.
After activating, the command prompt will have the name of the environment in parentheses at the beginning of the line as an indicator:
```console
(unoxTrilliumNC) username@HPC:~/$ 
```

#### Upgrading `pip`

The default package installer for Python is [`pip`](https://pip.pypa.io/en/stable/).
The next command ensures that the version of `pip` in the environment is up to date.
Make sure the virtual environment is activated first:
```console
(unoxTrilliumNC) username@HPC:~/$ pip install --no-index --upgrade pip
```

#### Installing the packages

The next commands install the packages required to run the code on Trillium.
Make sure the virtual environment is activated first:
```console
(unoxTrilliumNC) username@HPC:~/$ pip install --no-index 'tensorflow==2.17.0'
(unoxTrilliumNC) username@HPC:~/$ pip install --no-index 'xarray==2024.3.0'
(unoxTrilliumNC) username@HPC:~/$ pip install --no-index 'netcdf4==1.7.2'
```
The version of `tensorflow` (2.17.0, and `keras` version 3.10.0, as a dependency), was selected as the most up-to-date version available on Trillium at the time. 
The packages `xarray` version 2024.3.0 and `netcdf4` version 1.7.2 were selected to match the `conda` environment on Animus.

These packages are installed in this order specifically. 
This is due to the fact that `pip` will automatically upgrade packages that are dependencies for the package it is currently installing. 
Therefore, even when specifying a specific version of a package to install using the `==` operator, there is no guarantee that package will remain at that version when subsequent packages are installed.
This issue is solved by using a dependency manager like `poetry`. 
Even though `poetry` is available on the Alliance systems, I have had no luck actually managing to get it to work properly. 

The three packages installed explicitly above also have dependencies which get installed along with them. 
A full list of all packages and their versions in the `unoxTrilliumNC` environment is below:
```console
(unoxTrilliumNC) username@HPC:~/$ pip list
Package                 Version
----------------------- -------------------------
absl_py                 2.3.1+computecanada
astunparse              1.6.3+computecanada
certifi                 2025.10.5+computecanada
cftime                  1.6.4.post1+computecanada
charset_normalizer      3.4.4+computecanada
flatbuffers             25.2.10+computecanada
gast                    0.6.0+computecanada
google-pasta            0.2.0+computecanada
grpcio                  1.73.0+computecanada
h5py                    3.13.0+computecanada
idna                    3.11+computecanada
keras                   3.10.0+computecanada
libclang                14.0.1+computecanada
markdown                3.9+computecanada
markdown_it_py          4.0.0+computecanada
MarkupSafe              3.0.2+computecanada
mdurl                   0.1.2+computecanada
ml_dtypes               0.4.0+computecanada
namex                   0.1.0+computecanada
netCDF4                 1.7.2+computecanada
numpy                   1.26.4+computecanada
opt_einsum              3.4.0+computecanada
optree                  0.14.0+computecanada
packaging               25.0+computecanada
pandas                  2.3.3+computecanada
pip                     25.2+computecanada
protobuf                4.25.4+computecanada
pygments                2.19.2+computecanada
python_dateutil         2.9.0.post0+computecanada
pytz                    2025.2+computecanada
requests                2.32.5+computecanada
rich                    14.2.0+computecanada
setuptools              80.9.0+computecanada
six                     1.17.0+computecanada
tensorboard             2.17.1+computecanada
tensorboard_data_server 0.7.2+computecanada
tensorflow              2.17.0+computecanada
termcolor               3.1.0+computecanada
typing_extensions       4.15.0+computecanada
tzdata                  2025.2+computecanada
urllib3                 2.5.0+computecanada
werkzeug                3.1.3+computecanada
wheel                   0.45.1+computecanada
wrapt                   1.17.3+computecanada
xarray                  2024.3.0+computecanada
```

</details>

<a id='animus_venv'></a>
[back to top](#top)

### Virtual environment on Animus

This project uses a `conda` environment on Animus.

<a id='animus_conda'></a>
[back to top](#top)

#### Installing `miniconda` on Animus

If you do not yet have `conda` installed for your user on Animus, follow the instructions below. 
Otherwise, skip to [Creating the `conda` environment on Animus with `poetry`](#animus_poetry).

There is a way to activate and use a `conda` installation in another user's directory on Animus.
However, doing so will not allow modifications you make to the `unox` code base in your own cloned repository affect it's behavior in your `conda` environment.
This makes development very difficult.

If you need to install `conda`, I recommend using `miniconda`, which can be installed by running the following commands from your home directory:
```console
username@animus-c:~/$ mkdir -p ~/miniconda3
username@animus-c:~/$ wget https://repo.anaconda.com/miniconda/Miniconda3-py39_25.1.1-2-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
username@animus-c:~/$ bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
username@animus-c:~/$ rm ~/miniconda3/miniconda.sh
username@animus-c:~/$ source ~/miniconda3/bin/activate
(base) username@animus-c:~/$ conda init --all
(base) username@animus-c:~/$ conda info
```

<a id='animus_poetry'></a>
[back to top](#top)

#### Creating the `conda` environment on Animus with `poetry`

To see what `conda` environments you have created on Animus, run:
```console
username@animus-c:~/$ conda env list
/home/<username>/miniconda3/lib/python3.12/site-packages/conda/base/context.py:891: FutureWarning: Adding the 'free' channel as it existed prior to conda 4.7. is deprecated and will be removed in 25.3. See https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/free-channel.html for more details.
  deprecated.topic(

# conda environments:
#
base                   /home/<username>/miniconda3
unet0                  /home/<username>/miniconda3/envs/unet0
uplt                 * /home/<username>/miniconda3/envs/uplt
```
The warning has to do with having an old version of `miniconda` installed.
If you haven't created a `conda` environment on Animus yet, you will only see the `base` environment. 
It is highly discouraged to modify the `base` environment. 
If you have an environment activated when running this command, that environment will have a `*` next to it's path.

Create a new `conda` environment:
```console
username@animus-c:~/$ conda create -n <env_name> python=3.9
```
where `<env_name>` should be a memorable and distinct name. 
Since this environment is primarily used to create plots, I named mine `uplt`.
<!-- TODO: add output -->
Then, activate this environment:
```console
username@animus-c:~/$ conda activate <env_name>
```
Make sure to activate this environment before running the code or installing / updating any packages.

This project uses the Python package called `poetry` to manage the dependencies. 
Install the version of `poetry` used in this project:
```console
username@animus-c:~/$ conda install -n <env_name> -c conda-forge poetry=2.1.2
```

Once `poetry` is installed, it can be used to automatically install all other dependencies of the project based on the `pyproject.toml` file. 
First, navigate to the project directory and remove the `poetry.lock` file, if it exists:
```console
username@animus-c:~/$ cd unox/
username@animus-c:~/unox$ rm poetry.lock
```
Then, use `poetry` to install the dependencies:
```console
username@animus-c:~/unox$ poetry install
```