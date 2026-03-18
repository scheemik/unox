<a id='top'></a>
# Installation

The documentation below describes how to install this package in a way that enables active development. 
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
- [Configuring VSCodium](#config_vscodium)
    - [Connecting to remote machines](#vsc_ssh)
    - [Setting up VSCodium](#vsc_setup)
    - [Configuring the testing environment](#vsc_testing)

---
<a id='intro'></a>
[back to top](#top)

## Introduction

This document details the initial steps required to set up the environments necessary to develop this code base and run the model on a High-Performance Computing (HPC) cluster.
Command line prompts that are to be entered into a terminal as part of this process are shown here in `console` blocks like this:
```console
username@local:~$ pwd
/Users/<username>
```
where `<username>` would correspond to the username on the `local` machine. 
In this guide, the three machines that are referenced are `local` (the computer in front of you), `animus-c`, and `HPC` (the HPC cluster). 
All command prompts assume a unix-based system (ex: Linux or MacOS). 
If your local machine runs Windows, you will need to modify the `local` commands. 
**<ins>The machine in each console prompt indicates where the command is supposed to be executed</ins>**. 
Command prompts in these `console` blocks are shown on lines which start with the username and the machine.
Expected output is shown on subsequent lines.
When executing a command, only enter what is shown in prompt lines after the `$`.
For example, for the block above, you would enter only `pwd` into your console, not `username@local:~$ pwd`.

In some cases, it is important to have a particular virtual environment activated when executing a command. 
This will be indicated by the name of the virtual environment appearing in parentheses before the username. For example:
```console
(my_venv) username@HPC:~$ pip list
Package                 Version
----------------------- -------------------------
...
xarray                  2024.3.0+computecanada
```

In some instances, such as above, the output has been truncated for brevity using ellipses `...`.

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

In order to access Trillium, you will need to create an `ssh` authentication key and set up 2-factor authentication. 
Following the [Alliance docs](https://docs.alliancecan.ca/wiki/Using_SSH_keys_in_Linux) (assuming you have a unix-based system), generate a key pair on your local computer with:
```console
username@local:~$ ssh-keygen -t ed25519
```

Then, as described in [this Alliance docs page](https://docs.alliancecan.ca/wiki/SSH_Keys), log in to Alliance at the [SSH authorized keys page](https://ccdb.computecanada.ca/ssh_authorized_keys). 
Then, copy and paste in your public key by using the output of this command:
```console
username@local:~$ cat ~/.ssh/<id_ed25519>.pub
```
where `<id_ed25519>` is the name of the key you generated (default is usually just `id_ed25519.pub`). 
It might take about 30 minutes for the changes to take place and allow you to connect via SSH.

Next, verify that you can access Trillium through the command line. 
Open a terminal and use the following command, replacing `<SSH_id>` with the path to your authentication file (default is `~/.ssh/id_ed25519`) and `<username>` with your user name:
```console
username@local:~$ ssh -XY -i <SSH_id> <username>@trillium-gpu.alliancecan.ca
```
Be sure to log in to `trillium-gpu`, and not just `trillium` as you will need access to the GPU resources.

Once that works, I suggest adding the following lines to your local `~/.bashrc` file to make an alias command:
```bash
# In username@local:/Users/<username>/.bashrc
SSH_id=<SSH_id>
alias trillium="ssh -XY -i $SSH_id <username>@trillium-gpu.alliancecan.ca"
```
That way, after saving and sourcing the `~/.bashrc` file (by running `source ~/.bashrc`), you can just type `trillium` in the terminal to log in.

Note that, upon logging in to `trillium`, you will always be put into your home directory (`/home/<username>`, which you can check with the `pwd` command). 
However, following the recommendations of SciNet, you will want to always work in your "scratch" directory, which will be `scratch/<username>` (we'll make an alias to get there quickly later).

You should also find your local SSH configuration file `~/.ssh/config`, or create it if it doesn't exist already, and add the following:
```bash
# In username@local:/Users/<username>/.ssh/config
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
username@local:~$ ssh trillium
Enter passphrase for key '/Users/<username>/.ssh/<id_ed25519>': 
(<username>@trillium-gpu.alliancecan.ca) Duo two-factor login for <username>

Enter a passcode or select one of the following options:

 1. Duo Push to <mobile device>

Passcode or option (1-1): 1
Success. Logging you in...
Last login: Thu Dec 11 15:59:49 2025 from static-68-235-46-107.cust.tzulo.com
==============================================================================
 _____     _ _ _ _            SciNet welcomes you to the Trillium 
|_   _|___|_| | |_|_ _ _____  cluster at the University of Toronto!
  | | |  _| | | | | | |     |
  | | | | | | | | | | | | | | Docs: https://docs.alliancecan.ca/wiki/Trillium
  |_| |_| |_|_|_|_|___|G|P|U| Help: trillium@tech.alliancecan.ca

This is the GPU login node trig-login01. Use this node to develop and compile
code, to run short tests, and to submit GPU compute jobs to the scheduler.
==============================================================================

For help with your transition to Trillium, please see:
https://docs.alliancecan.ca/wiki/Transition_from_Niagara_to_Trillium

Prefer a self-guided course instead?
Check out: see https://scinet.courses/1389
===============================================================================

Welcome <username>, your access to this system has been logged.
If you are not <username>, please disconnect immediately.

username@HPC:~$
```

<a id='animus_connect'></a>
[back to top](#top)

### Connecting to Animus

Your supervisor in the Physics Department will set you up with access to `animus-c`. 
Once that is done, verify that you can access `animus-c` through the command line. 
Open a terminal and use the following command, replacing `<username>` with your user name:
```console
username@local:~$ ssh <username>@animus-c.atmosp.physics.utoronto.ca
username@animus-c.atmosp.physics.utoronto.ca's password: 
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-164-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Tue Jan  6 09:43:04 AM EST 2026

  System load:  1.15               Temperature:           32.0 C
  Usage of /:   51.7% of 97.87GB   Processes:             524
  Memory usage: 53%                Users logged in:       3
  Swap usage:   23%                IPv4 address for eno1: 128.100.80.74

 * Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
   just raised the bar for easy, resilient and secure K8s cluster deployment.

   https://ubuntu.com/engage/secure-kubernetes-at-the-edge

Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

26 additional security updates can be applied with ESM Apps.
Learn more about enabling ESM Apps service at https://ubuntu.com/esm

New release '24.04.3 LTS' available.
Run 'do-release-upgrade' to upgrade to it.


Last login: Tue Nov 25 14:32:40 2025 from 68.235.46.14
username@animus-c:~$
```
As with connecting to HPC, I would suggest adding the following alias to your `.bashrc`:
```bash
# In username@local:/Users/<username>/.bashrc
alias animus="ssh <username>@animus-c.atmosp.physics.utoronto.ca"
```
Again, as with HPC, and add the following to your SSH configuration file `~/.ssh/config`:
```bash
# In username@local:/Users/<username>/.ssh/config
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

Then, you can follow the guide on [Testing your SSH connection](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection) to make sure you can connect to GitHub **<ins>from each remote machine</ins>**.
This amounts to first activating your authentication key:
```console
username@<animus-c_or_HPC>:~$ eval $(ssh-agent -s); ssh-add ~/.ssh/<GH_id>
Agent pid 669646
Enter passphrase for /home/<username>/.ssh/<GH_id>: 
Identity added: /home/<username>/.ssh/<GH_id> (<user@mail.ca>)
```
Then, attempting to connect to `git@github.com`:
```console
username@<animus-c_or_HPC>:~$ ssh git@github.com
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
For this reason, make sure to clone the repository into the `scratch` filesystem **<ins>on HPC</ins>**. 
You may choose to create a new directory within which to clone the repository, but this is optional:
```console
username@HPC:~$ cd /scratch/<username>/<optional_directory>/
username@HPC:<optional_directory>$ git clone git@github.com:scheemik/unox.git
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
# In username@HPC:/home/<username>/.bashrc
alias cdproj='cd $SCRATCH/<optional_directory>/unox/'
```
Then, after sourcing `~/.bashrc`, you can execute the command `cdproj` to automatically navigate to the project directory.

#### Animus

Navigate to a directory location in which you have write permissions (ex: your home directory) and clone the repository **<ins>on Animus</ins>**:

```console
username@animus-c:~$ git clone git@github.com:scheemik/unox.git
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

#### Git exclude

There are many files which are produced by running this code which do not need to be tracked by `git`.
Some of these files are specified in the `.gitignore` file in the base directory of the repository. 
Note: this `.gitignore` file is tracked by `git` and will be pushed to the repository, meaning those files will be ignored for everyone who clones it. 

Some files in this repository need to be edited for each individual (e.g., to hold a username) and some directories will hold generated data which is too large to be uploaded to GitHub. 
For these, add them to the list in the `unox/git/info/exclude` file, meaning that `git` will not monitor changes in them for your instance of the repository.
Add the following to the `unox/git/info/exclude` file **<ins>on both HPC and Animus</ins>**:

```bash
# git ls-files --others --exclude-from=.git/info/exclude
# Lines that start with '#' are comments.
# For a project mostly in C, the following would be a good set of
# exclude patterns (uncomment them if you want to use them):
# *.[oa]
# *~
*.pyc
.vscode/*
datafiles/era5_downloads/*
datafiles/ERA5concatenated/*
datafiles/GEOSChem.SpeciesConc_merged/*
datafiles/HEMCO_diagnostics_merged/*
HPC_runs/*
HPC_params.sh
HPC_GPU_slurm.sh
sample_data/*
outputs/*
inputfiles/*
!inputfiles/_input_configs/test_config.json
input_test/*
poetry.lock
```

The `!` at a start of a line means to specifically _include_ a file to be tracked by `git`. 

#### Setting the HPC parameters

The `HPC_params.sh` file in the repository contains parameters that will be used to facilitate transferring between the two remote systems. 
Find this file **<ins>on HPC</ins>** and change the parameters to reflect those for your user accounts, especially the user names. 
Because `HPC_params.sh` will contain information specific to each person, it doesn't make sense to push the changes made there, which would cause a different user to use the wrong parameters after the pull from the repository.
However, with the `HPC_params.sh` file added to the list in `unox/git/info/exclude` as shown above, it will no longer be tracked by `git` and so it is unlikely you could accidentally push changes to it. 

As an additional step, change the email address in the `HPC_GPU_slurm.sh` file in the `#SBATCH` options to that you are the one who receives email notifications for the model runs you submit.

```bash
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=1:00:00
#SBATCH --mail-user=<your_email@domain>
#SBATCH --mail-type=ALL
#SBATCH --output=HPC_runs/%x/log_%j.txt				# %x = job_name, %j = job_number
...
```

Unfortunately, I was unable to find a way to have the `#SBATCH` notification email be pulled from the `HPC_params.sh` file and so I set it up to be the other way around. 
For the same reason as with `HPC_params.sh`, the `HPC_GPU_slurm.sh` file was added to the list in `unox/git/info/exclude`.

Note that the changes to both `HPC_params.sh` and `HPC_GPU_slurm.sh` described in this section only need to be made **<ins>on HPC</ins>**.
None of the scripts that are meant to be executed on Animus will be affected. 
You can change the contents of `HPC_params.sh` and `HPC_GPU_slurm.sh` on Animus to match what is on HPC, but it is not necessary.

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
They suggest that creating a new environment every time might actually speed up performance, but I believe it is more important for the code to run consistently.

To see what environments you have created **<ins>on Trillium</ins>**, run:
```console
username@HPC:~$ ls /home/<username>/.virtualenvs/
unoxTrillium  unoxTrilliumNC  unoxTrilliumTest
```
If you haven't created a virtual environment on Trillium before, this output might be empty or the `.virtualenvs/` directory might not exist yet. 

The following commands will create the exact virtual environment the code expects to run in:
```console
username@HPC:~$ module load StdEnv/2023 gcc/12.3 python/3.12.4 cuda/12.6 hdf5/1.14.2 netcdf/4.9.2 mpi4py/4.0.0
username@HPC:~$ virtualenv --no-download /home/<username>/.virtualenvs/unoxTrilliumNC
username@HPC:~$ source /home/<username>/.virtualenvs/unoxTrilliumNC/bin/activate
(unoxTrilliumNC) username@HPC:~$ pip install --no-index --upgrade pip
(unoxTrilliumNC) username@HPC:~$ pip install --no-index 'tensorflow==2.17.0'
(unoxTrilliumNC) username@HPC:~$ pip install --no-index 'xarray==2024.3.0'
(unoxTrilliumNC) username@HPC:~$ pip install --no-index 'netcdf4==1.7.2'
```
<!-- TODO: Add the output of each command in collapsible section. -->

<!-- TODO: Add explanation of each module I load, the creation and sourcing of the venv, and for each of the packages I install and what dependencies come with them. -->

<details>

<summary>Expand for details and example output</summary>

#### Modules

Trillium, like many Alliance clusters, uses [Environment Modules](https://docs.alliancecan.ca/wiki/Utiliser_des_modules/en) to load software that has been already installed and configured. 
The first command in creating the virtual environment above loads all the necessary modules:
```console
username@HPC:~$ module load StdEnv/2023 gcc/12.3 python/3.12.4 cuda/12.6 hdf5/1.14.2 netcdf/4.9.2 mpi4py/4.0.0
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
username@HPC:~$ virtualenv --no-download /home/<username>/.virtualenvs/unoxTrilliumNC
created virtual environment CPython3.12.4.final.0-64 in 3124ms
  creator CPython3Posix(dest=/home/<username>/.virtualenvs/unoxTrilliumNC, clear=False, no_vcs_ignore=False, global=False)
  seeder FromAppData(download=False, pip=bundle, via=copy, app_data_dir=/home/<username>/.local/share/virtualenv)
    added seed packages: pip==25.3
  activators BashActivator,CShellActivator,FishActivator,NushellActivator,PowerShellActivator,PythonActivator
```

The name of the environment, `unoxTrilliumNC` could be anything, but this is the name that is expected in the code when activating the environment in `HPC_slurm.sh`. 

#### Activating the virtual environment

The next command activates the virtual environment:
```console
username@HPC:~$ source /home/<username>/.virtualenvs/unoxTrilliumNC/bin/activate
```

This is important to do before installing any packages as to not affect your base environment.
After activating, the command prompt will have the name of the environment in parentheses at the beginning of the line as an indicator:
```console
(unoxTrilliumNC) username@HPC:~$ 
```

#### Upgrading `pip`

The default package installer for Python is [`pip`](https://pip.pypa.io/en/stable/).
The next command ensures that the version of `pip` in the environment is up to date.
Make sure the virtual environment is activated first:
```console
(unoxTrilliumNC) username@HPC:~$ pip install --no-index --upgrade pip
Looking in links: /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v4, /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v3, /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/generic, /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic
Requirement already satisfied: pip in /home/<username>/.virtualenvs/unoxTrilliumNC/lib/python3.12/site-packages (25.3)
```

#### Installing the packages

The next commands install the packages required to run the code on Trillium.
Make sure the virtual environment is activated first:
```console
(unoxTrilliumNC) username@HPC:~$ pip install --no-index 'tensorflow==2.17.0'
Looking in links: /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v4, /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v3, /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/generic, /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/generic/tensorflow-2.17.0+computecanada-cp312-cp312-linux_x86_64.whl
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/absl_py-2.3.1+computecanada-py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/astunparse-1.6.3+computecanada-py2.py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/flatbuffers-25.9.23+computecanada-py2.py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/gast-0.7.0+computecanada-py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/google_pasta-0.2.0+computecanada-py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v3/h5py-3.15.0+computecanada-cp312-cp312-linux_x86_64.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/libclang-14.0.1+computecanada-py2.py3-none-linux_x86_64.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/generic/ml_dtypes-0.4.0+computecanada-cp312-cp312-linux_x86_64.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/opt_einsum-3.4.0+computecanada-py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/packaging-25.0+computecanada-py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v3/protobuf-4.25.4+computecanada-cp312-cp312-linux_x86_64.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/requests-2.32.5+computecanada-py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/setuptools-80.9.0+computecanada-py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/six-1.17.0+computecanada-py2.py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/termcolor-3.2.0+computecanada-py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/typing_extensions-4.15.0+computecanada-py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/wrapt-2.0.1+computecanada-cp312-cp312-linux_x86_64.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/grpcio-1.73.0+computecanada-cp312-cp312-linux_x86_64.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/tensorboard-2.17.1+computecanada-py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/keras-3.11.3+computecanada-py3-none-any.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/generic/numpy-1.26.4+computecanada-cp312-cp312-linux_x86_64.whl (from tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/charset_normalizer-3.4.4+computecanada-py3-none-any.whl (from requests<3,>=2.21.0->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/idna-3.11+computecanada-py3-none-any.whl (from requests<3,>=2.21.0->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/urllib3-2.6.2+computecanada-py3-none-any.whl (from requests<3,>=2.21.0->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/certifi-2025.11.12+computecanada-py3-none-any.whl (from requests<3,>=2.21.0->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/markdown-3.9+computecanada-py3-none-any.whl (from tensorboard<2.18,>=2.17->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/tensorboard_data_server-0.7.2+computecanada-py3-none-linux_x86_64.whl (from tensorboard<2.18,>=2.17->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/werkzeug-3.1.4+computecanada-py3-none-any.whl (from tensorboard<2.18,>=2.17->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/wheel-0.45.1+computecanada-py3-none-any.whl (from astunparse>=1.6.0->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/rich-14.2.0+computecanada-py3-none-any.whl (from keras>=3.2.0->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/namex-0.1.0+computecanada-py3-none-any.whl (from keras>=3.2.0->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/generic/optree-0.14.0+computecanada-cp312-cp312-linux_x86_64.whl (from keras>=3.2.0->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/MarkupSafe-3.0.2+computecanada-cp312-cp312-linux_x86_64.whl (from werkzeug>=1.0.1->tensorboard<2.18,>=2.17->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/markdown_it_py-4.0.0+computecanada-py3-none-any.whl (from rich->keras>=3.2.0->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/pygments-2.19.2+computecanada-py3-none-any.whl (from rich->keras>=3.2.0->tensorflow==2.17.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/mdurl-0.1.2+computecanada-py3-none-any.whl (from markdown-it-py>=2.2.0->rich->keras>=3.2.0->tensorflow==2.17.0)
Installing collected packages: namex, libclang, flatbuffers, wrapt, wheel, urllib3, typing-extensions, termcolor, tensorboard-data-server, six, setuptools, pygments, protobuf, packaging, opt-einsum, numpy, mdurl, markupsafe, markdown, idna, grpcio, gast, charset-normalizer, certifi, absl-py, werkzeug, requests, optree, ml-dtypes, markdown-it-py, h5py, google-pasta, astunparse, tensorboard, rich, keras, tensorflow
Successfully installed absl-py-2.3.1+computecanada astunparse-1.6.3+computecanada certifi-2025.11.12+computecanada charset-normalizer-3.4.4+computecanada flatbuffers-25.9.23+computecanada gast-0.7.0+computecanada google-pasta-0.2.0+computecanada grpcio-1.73.0+computecanada h5py-3.15.0+computecanada idna-3.11+computecanada keras-3.11.3+computecanada libclang-14.0.1+computecanada markdown-3.9+computecanada markdown-it-py-4.0.0+computecanada markupsafe-3.0.2+computecanada mdurl-0.1.2+computecanada ml-dtypes-0.4.0+computecanada namex-0.1.0+computecanada numpy-1.26.4+computecanada opt-einsum-3.4.0+computecanada optree-0.14.0+computecanada packaging-25.0+computecanada protobuf-4.25.4+computecanada pygments-2.19.2+computecanada requests-2.32.5+computecanada rich-14.2.0+computecanada setuptools-80.9.0+computecanada six-1.17.0+computecanada tensorboard-2.17.1+computecanada tensorboard-data-server-0.7.2+computecanada tensorflow-2.17.0+computecanada termcolor-3.2.0+computecanada typing-extensions-4.15.0+computecanada urllib3-2.6.2+computecanada werkzeug-3.1.4+computecanada wheel-0.45.1+computecanada wrapt-2.0.1+computecanada
```

```console
(unoxTrilliumNC) username@HPC:~$ pip install --no-index 'xarray==2024.3.0'
Looking in links: /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v4, /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v3, /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/generic, /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/xarray-2024.3.0+computecanada-py3-none-any.whl
Requirement already satisfied: numpy>=1.23 in /home/<username>/.virtualenvs/unoxTrilliumNC/lib/python3.12/site-packages (from xarray==2024.3.0) (1.26.4+computecanada)
Requirement already satisfied: packaging>=22 in /home/<username>/.virtualenvs/unoxTrilliumNC/lib/python3.12/site-packages (from xarray==2024.3.0) (25.0+computecanada)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v3/pandas-2.3.3+computecanada-cp312-cp312-linux_x86_64.whl (from xarray==2024.3.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/python_dateutil-2.9.0.post0+computecanada-py2.py3-none-any.whl (from pandas>=1.5->xarray==2024.3.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/pytz-2025.2+computecanada-py2.py3-none-any.whl (from pandas>=1.5->xarray==2024.3.0)
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic/tzdata-2025.3+computecanada-py2.py3-none-any.whl (from pandas>=1.5->xarray==2024.3.0)
Requirement already satisfied: six>=1.5 in /home/<username>/.virtualenvs/unoxTrilliumNC/lib/python3.12/site-packages (from python-dateutil>=2.8.2->pandas>=1.5->xarray==2024.3.0) (1.17.0+computecanada)
Installing collected packages: pytz, tzdata, python-dateutil, pandas, xarray
Successfully installed pandas-2.3.3+computecanada python-dateutil-2.9.0.post0+computecanada pytz-2025.2+computecanada tzdata-2025.3+computecanada xarray-2024.3.0+computecanada
```

```console
(unoxTrilliumNC) username@HPC:~$ pip install --no-index 'netcdf4==1.7.2'
Looking in links: /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v4, /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v3, /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/generic, /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/generic
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v3/netCDF4-1.7.2+computecanada-cp312-cp312-linux_x86_64.whl
Processing /cvmfs/soft.computecanada.ca/custom/python/wheelhouse/gentoo2023/x86-64-v3/cftime-1.6.4.post1+computecanada-cp312-cp312-linux_x86_64.whl (from netcdf4==1.7.2)
Requirement already satisfied: certifi in /home/<username>/.virtualenvs/unoxTrilliumNC/lib/python3.12/site-packages (from netcdf4==1.7.2) (2025.11.12+computecanada)
Requirement already satisfied: numpy in /home/<username>/.virtualenvs/unoxTrilliumNC/lib/python3.12/site-packages (from netcdf4==1.7.2) (1.26.4+computecanada)
Installing collected packages: cftime, netcdf4
Successfully installed cftime-1.6.4.post1+computecanada netcdf4-1.7.2+computecanada
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
(unoxTrilliumNC) username@HPC:~$ pip list
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

<!-- 2026-01-06
```console
(unoxToDelete) username@HPC:~$ pip list
Package                 Version
----------------------- -------------------------
absl_py                 2.3.1+computecanada
astunparse              1.6.3+computecanada
certifi                 2025.11.12+computecanada
cftime                  1.6.4.post1+computecanada
charset_normalizer      3.4.4+computecanada
flatbuffers             25.9.23+computecanada
gast                    0.7.0+computecanada
google-pasta            0.2.0+computecanada
grpcio                  1.73.0+computecanada
h5py                    3.15.0+computecanada
idna                    3.11+computecanada
keras                   3.11.3+computecanada
libclang                14.0.1+computecanada
markdown                3.9+computecanada
markdown_it_py          4.0.0+computecanada
MarkupSafe              3.0.2+computecanada
mdurl                   0.1.2+computecanada
ml_dtypes               0.4.0+computecanada
mpi4py                  4.0.0
namex                   0.1.0+computecanada
netCDF4                 1.7.2+computecanada
numpy                   1.26.4+computecanada
opt_einsum              3.4.0+computecanada
optree                  0.14.0+computecanada
packaging               25.0+computecanada
pandas                  2.3.3+computecanada
pip                     25.3
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
termcolor               3.2.0+computecanada
typing_extensions       4.15.0+computecanada
tzdata                  2025.3+computecanada
urllib3                 2.6.2+computecanada
werkzeug                3.1.4+computecanada
wheel                   0.45.1+computecanada
wrapt                   2.0.1+computecanada
xarray                  2024.3.0+computecanada
``` -->

</details>

<br/>

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

If you need to install `conda`, I recommend using `miniconda`, which can be installed by running the following commands from your home directory **<ins>on Animus</ins>**:
```console
username@animus-c:~$ mkdir -p ~/miniconda3
username@animus-c:~$ wget https://repo.anaconda.com/miniconda/Miniconda3-py39_25.1.1-2-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
username@animus-c:~$ bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
username@animus-c:~$ rm ~/miniconda3/miniconda.sh
username@animus-c:~$ source ~/miniconda3/bin/activate
(base) username@animus-c:~$ conda init --all
(base) username@animus-c:~$ conda info
/home/<username>/miniconda3/lib/python3.12/site-packages/conda/base/context.py:891: FutureWarning: Adding the 'free' channel as it existed prior to conda 4.7. is deprecated and will be removed in 25.3. See https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/free-channel.html for more details.
  deprecated.topic(

     active environment : base
    active env location : /home/<username>/miniconda3
            shell level : 1
       user config file : /home/<username>/.condarc
 populated config files : /home/<username>/miniconda3/.condarc
                          /home/<username>/.condarc
          conda version : 25.1.1
    conda-build version : not installed
         python version : 3.12.9.final.0
                 solver : libmamba (default)
       virtual packages : __archspec=1=broadwell
                          __conda=25.1.1=0
                          __glibc=2.35=0
                          __linux=5.15.0=0
                          __unix=0=0
       base environment : /home/<username>/miniconda3  (writable)
      conda av data dir : /home/<username>/miniconda3/etc/conda
  conda av metadata url : None
           channel URLs : https://repo.anaconda.com/pkgs/main/linux-64
                          https://repo.anaconda.com/pkgs/main/noarch
                          https://repo.anaconda.com/pkgs/r/linux-64
                          https://repo.anaconda.com/pkgs/r/noarch
          package cache : /home/<username>/miniconda3/pkgs
                          /home/<username>/.conda/pkgs
       envs directories : /home/<username>/miniconda3/envs
                          /home/<username>/.conda/envs
               platform : linux-64
             user-agent : conda/25.1.1 requests/2.32.3 CPython/3.12.9 Linux/5.15.0-164-generic ubuntu/22.04.5 glibc/2.35 solver/libmamba conda-libmamba-solver/25.1.1 libmambapy/2.0.5 aau/0.5.0 c/. s/. e/.
                UID:GID : 101076:101076
             netrc file : None
           offline mode : False
```

<a id='animus_poetry'></a>
[back to top](#top)

#### Creating the `conda` environment on Animus with `poetry`

To see what `conda` environments you have created **<ins>on Animus</ins>**, run:
```console
(base) username@animus-c:~$ conda env list
/home/<username>/miniconda3/lib/python3.12/site-packages/conda/base/context.py:891: FutureWarning: Adding the 'free' channel as it existed prior to conda 4.7. is deprecated and will be removed in 25.3. See https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/free-channel.html for more details.
  deprecated.topic(

# conda environments:
#
base                 * /home/<username>/miniconda3
unet                   /home/<username>/miniconda3/envs/unet
uplt                   /home/<username>/miniconda3/envs/uplt
```
The warning has to do with having an old version of `miniconda` installed.
If you haven't created a `conda` environment on Animus yet, you will only see the `base` environment. 
It is highly discouraged to modify the `base` environment. 
If you have an environment activated when running this command, that environment will have a `*` next to it's path.

Create a new `conda` environment **<ins>on Animus</ins>**:
```console
username@animus-c:~$ conda create -n <env_name> python=3.9
```
where `<env_name>` should be a memorable and distinct name. 
Since this environment is primarily used to create plots, I named mine `uplt`.
Currently, the environment for Aniums uses Python version 3.9.21. 
This is not as current as the Trillium environment, which uses 3.12.4. 
I hope to update the Python version for the Animus environment to match that of Trillium. 

<details>

<summary>Expand for output</summary>

```console
username@animus-c:~$ conda create -n <env_name> python=3.9
/home/mschee/miniconda3/lib/python3.12/site-packages/conda/base/context.py:891: FutureWarning: Adding the 'free' channel as it existed prior to conda 4.7. is deprecated and will be removed in 25.3. See https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/free-channel.html for more details.
  deprecated.topic(
Retrieving notices: done
Channels:
 - defaults
Platform: linux-64
Collecting package metadata (repodata.json): done
Solving environment: done


==> WARNING: A newer version of conda exists. <==
    current version: 25.1.1
    latest version: 25.11.1

Please update conda by running

    $ conda update -n base -c defaults conda



## Package Plan ##

  environment location: /home/mschee/miniconda3/envs/delete_this

  added / updated specs:
    - python=3.9


The following packages will be downloaded:

    package                    |            build
    ---------------------------|-----------------
    ca-certificates-2025.12.2  |       h06a4308_0         125 KB
    expat-2.7.3                |       h7354ed3_4          25 KB
    ld_impl_linux-64-2.44      |       h153f514_2         672 KB
    libexpat-2.7.3             |       h7354ed3_4         121 KB
    libgcc-15.2.0              |       h69a1729_7         806 KB
    libgcc-ng-15.2.0           |       h166f726_7          28 KB
    libgomp-15.2.0             |       h4751f2c_7         436 KB
    libnsl-2.0.0               |       h5eee18b_0          31 KB
    libstdcxx-15.2.0           |       h39759b7_7         3.7 MB
    libstdcxx-ng-15.2.0        |       hc03a8fd_7          28 KB
    libxcb-1.17.0              |       h9b100fa_0         430 KB
    libzlib-1.3.1              |       hb25bd0a_0          59 KB
    ncurses-6.5                |       h7934f7d_0         1.1 MB
    openssl-3.0.18             |       hd6dcaed_0         4.5 MB
    pip-25.3                   |     pyhc872135_0         1.1 MB
    pthread-stubs-0.3          |       h0ce48e5_1           5 KB
    python-3.9.25              |       h0dcde21_1        23.0 MB
    readline-8.3               |       hc2a1206_0         471 KB
    setuptools-80.9.0          |   py39h06a4308_0         1.4 MB
    sqlite-3.51.1              |       he0a8d7e_0         1.2 MB
    tk-8.6.15                  |       h54e0aa7_0         3.4 MB
    xorg-libx11-1.8.12         |       h9b100fa_1         895 KB
    xorg-libxau-1.0.12         |       h9b100fa_0          13 KB
    xorg-libxdmcp-1.1.5        |       h9b100fa_0          19 KB
    xorg-xorgproto-2024.1      |       h5eee18b_1         580 KB
    zlib-1.3.1                 |       hb25bd0a_0          96 KB
    ------------------------------------------------------------
                                           Total:        44.2 MB

The following NEW packages will be INSTALLED:

  _libgcc_mutex      pkgs/main/linux-64::_libgcc_mutex-0.1-main 
  _openmp_mutex      pkgs/main/linux-64::_openmp_mutex-5.1-1_gnu 
  bzip2              pkgs/main/linux-64::bzip2-1.0.8-h5eee18b_6 
  ca-certificates    pkgs/main/linux-64::ca-certificates-2025.12.2-h06a4308_0 
  expat              pkgs/main/linux-64::expat-2.7.3-h7354ed3_4 
  ld_impl_linux-64   pkgs/main/linux-64::ld_impl_linux-64-2.44-h153f514_2 
  libexpat           pkgs/main/linux-64::libexpat-2.7.3-h7354ed3_4 
  libffi             pkgs/main/linux-64::libffi-3.4.4-h6a678d5_1 
  libgcc             pkgs/main/linux-64::libgcc-15.2.0-h69a1729_7 
  libgcc-ng          pkgs/main/linux-64::libgcc-ng-15.2.0-h166f726_7 
  libgomp            pkgs/main/linux-64::libgomp-15.2.0-h4751f2c_7 
  libnsl             pkgs/main/linux-64::libnsl-2.0.0-h5eee18b_0 
  libstdcxx          pkgs/main/linux-64::libstdcxx-15.2.0-h39759b7_7 
  libstdcxx-ng       pkgs/main/linux-64::libstdcxx-ng-15.2.0-hc03a8fd_7 
  libuuid            pkgs/main/linux-64::libuuid-1.41.5-h5eee18b_0 
  libxcb             pkgs/main/linux-64::libxcb-1.17.0-h9b100fa_0 
  libzlib            pkgs/main/linux-64::libzlib-1.3.1-hb25bd0a_0 
  ncurses            pkgs/main/linux-64::ncurses-6.5-h7934f7d_0 
  openssl            pkgs/main/linux-64::openssl-3.0.18-hd6dcaed_0 
  pip                pkgs/main/noarch::pip-25.3-pyhc872135_0 
  pthread-stubs      pkgs/main/linux-64::pthread-stubs-0.3-h0ce48e5_1 
  python             pkgs/main/linux-64::python-3.9.25-h0dcde21_1 
  readline           pkgs/main/linux-64::readline-8.3-hc2a1206_0 
  setuptools         pkgs/main/linux-64::setuptools-80.9.0-py39h06a4308_0 
  sqlite             pkgs/main/linux-64::sqlite-3.51.1-he0a8d7e_0 
  tk                 pkgs/main/linux-64::tk-8.6.15-h54e0aa7_0 
  tzdata             pkgs/main/noarch::tzdata-2025b-h04d1e81_0 
  wheel              pkgs/main/linux-64::wheel-0.45.1-py39h06a4308_0 
  xorg-libx11        pkgs/main/linux-64::xorg-libx11-1.8.12-h9b100fa_1 
  xorg-libxau        pkgs/main/linux-64::xorg-libxau-1.0.12-h9b100fa_0 
  xorg-libxdmcp      pkgs/main/linux-64::xorg-libxdmcp-1.1.5-h9b100fa_0 
  xorg-xorgproto     pkgs/main/linux-64::xorg-xorgproto-2024.1-h5eee18b_1 
  xz                 pkgs/main/linux-64::xz-5.6.4-h5eee18b_1 
  zlib               pkgs/main/linux-64::zlib-1.3.1-hb25bd0a_0 


Proceed ([y]/n)? 


Downloading and Extracting Packages:
                                                                                                                   
Preparing transaction: done                                                                                        
Verifying transaction: done                                                                                        
Executing transaction: done                                                                                        
#                                                                                                                  
# To activate this environment, use                                                                                
#                                                                                                                  
#     $ conda activate delete_this                                                                                 
#                                                                                                                  
# To deactivate an active environment, use                                                                         
#                                                                                                                  
#     $ conda deactivate
```

</details>

<br/>

Then, activate this environment:
```console
username@animus-c:~$ conda activate <env_name>
```
Make sure to activate this environment before running the code or installing / updating any packages.

This project uses the Python package called `poetry` to manage the dependencies. 
Install the version of `poetry` used in this project:
```console
(env_name) username@animus-c:~$ conda install -n <env_name> -c conda-forge poetry=2.1.2
```

<details>

<summary>Expand for output</summary>

```console
(env_name) username@animus-c:~$ conda install -n <env_name> -c conda-forge poetry=2.1.2
/home/mschee/miniconda3/lib/python3.12/site-packages/conda/base/context.py:891: FutureWarning: Adding the 'free' channel as it existed prior to conda 4.7. is deprecated and will be removed in 25.3. See https://docs.conda.io/projects/conda/en/stable/user-guide/configuration/free-channel.html for more details.                                    
  deprecated.topic(   
Channels:
 - conda-forge
 - defaults
Platform: linux-64
Collecting package metadata (repodata.json): done
Solving environment: done


==> WARNING: A newer version of conda exists. <==
    current version: 25.1.1
    latest version: 25.11.1

Please update conda by running

    $ conda update -n base -c defaults conda



## Package Plan ##

  environment location: /home/mschee/miniconda3/envs/delete_this

  added / updated specs:
    - poetry=2.1.2


The following packages will be downloaded:

    package                    |            build
    ---------------------------|-----------------
    anyio-4.10.0               |     pyhe01879c_0         132 KB  conda-forge
    brotli-python-1.1.0        |   py39hf88036b_3         342 KB  conda-forge
    ca-certificates-2026.1.4   |       hbd8a1cb_0         143 KB  conda-forge
    certifi-2025.8.3           |     pyhd8ed1ab_0         155 KB  conda-forge
    cffi-1.17.1                |   py39h15c3d72_0         236 KB  conda-forge
    charset-normalizer-3.4.3   |     pyhd8ed1ab_0          50 KB  conda-forge
    cryptography-45.0.6        |   py39hb2f7f84_0         1.5 MB  conda-forge
    dbus-1.16.2                |       h3c4dab8_0         428 KB  conda-forge
    distlib-0.4.0              |     pyhd8ed1ab_0         269 KB  conda-forge
    dulwich-0.22.8             |   py39he612d8f_0         721 KB  conda-forge
    filelock-3.19.1            |     pyhd8ed1ab_0          18 KB  conda-forge
    jaraco.functools-4.3.0     |     pyhd8ed1ab_0          16 KB  conda-forge
    libblas-3.11.0             |5_h4a7cf45_openblas          18 KB  conda-forge
    libcblas-3.11.0            |5_h0358290_openblas          18 KB  conda-forge
    libgfortran-15.2.0         |      h69a702a_16          27 KB  conda-forge
    libgfortran5-15.2.0        |      h68bc16d_16         2.4 MB  conda-forge
    libglib-2.84.4             |       h77a78f3_0         2.8 MB
    libiconv-1.18              |       h3b78370_2         772 KB  conda-forge
    liblapack-3.11.0           |5_h47877c9_openblas          18 KB  conda-forge
    libopenblas-0.3.30         |pthreads_h94d23a6_4         5.7 MB  conda-forge
    msgpack-python-1.1.1       |   py39h74842e3_0          93 KB  conda-forge
    numpy-2.0.2                |   py39h9cb892a_1         7.6 MB  conda-forge
    openssl-3.6.0              |       h26f9b46_0         3.0 MB  conda-forge
    pbs-installer-2025.8.18    |     pyhd8ed1ab_0          55 KB  conda-forge
    pcre2-10.46                |       h1321c63_0         1.2 MB  conda-forge
    python-build-1.3.0         |     pyhff2d567_0          25 KB  conda-forge
    python-fastjsonschema-2.21.2|     pyhe01879c_0         239 KB  conda-forge
    rapidfuzz-3.13.0           |   py39hf88036b_0         2.1 MB  conda-forge
    requests-2.32.5            |     pyhd8ed1ab_0          58 KB  conda-forge
    tomli-2.2.1                |     pyhe01879c_2          21 KB  conda-forge
    tomlkit-0.13.3             |     pyha770c72_0          38 KB  conda-forge
    trove-classifiers-2025.8.6.13|     pyhd8ed1ab_0          19 KB  conda-forge
    typing_extensions-4.14.1   |     pyhe01879c_0          50 KB  conda-forge
    urllib3-2.5.0              |     pyhd8ed1ab_0          99 KB  conda-forge
    virtualenv-20.34.0         |     pyhd8ed1ab_0         4.2 MB  conda-forge
    zipp-3.23.0                |     pyhd8ed1ab_0          22 KB  conda-forge
    zstandard-0.23.0           |   py39hd399759_3         466 KB  conda-forge
    ------------------------------------------------------------
                                           Total:        34.8 MB

The following NEW packages will be INSTALLED:

  anyio              conda-forge/noarch::anyio-4.10.0-pyhe01879c_0 
  backports          conda-forge/noarch::backports-1.0-pyhd8ed1ab_5 
  backports.tarfile  conda-forge/noarch::backports.tarfile-1.2.0-pyhd8ed1ab_1 
  brotli-python      conda-forge/linux-64::brotli-python-1.1.0-py39hf88036b_3 
  cachecontrol       conda-forge/noarch::cachecontrol-0.14.3-pyha770c72_0 
  cachecontrol-with~ conda-forge/noarch::cachecontrol-with-filecache-0.14.3-pyhd8ed1ab_0 
  certifi            conda-forge/noarch::certifi-2025.8.3-pyhd8ed1ab_0 
  cffi               conda-forge/linux-64::cffi-1.17.1-py39h15c3d72_0 
  charset-normalizer conda-forge/noarch::charset-normalizer-3.4.3-pyhd8ed1ab_0 
  cleo               conda-forge/noarch::cleo-2.1.0-pyhd8ed1ab_1 
  colorama           conda-forge/noarch::colorama-0.4.6-pyhd8ed1ab_1 
  crashtest          conda-forge/noarch::crashtest-0.4.1-pyhd8ed1ab_1 
  cryptography       conda-forge/linux-64::cryptography-45.0.6-py39hb2f7f84_0 
  dbus               conda-forge/linux-64::dbus-1.16.2-h3c4dab8_0 
  distlib            conda-forge/noarch::distlib-0.4.0-pyhd8ed1ab_0 
  dulwich            conda-forge/linux-64::dulwich-0.22.8-py39he612d8f_0 
  exceptiongroup     conda-forge/noarch::exceptiongroup-1.3.0-pyhd8ed1ab_0 
  filelock           conda-forge/noarch::filelock-3.19.1-pyhd8ed1ab_0 
  findpython         conda-forge/noarch::findpython-0.6.3-pyhff2d567_0 
  h11                conda-forge/noarch::h11-0.16.0-pyhd8ed1ab_0 
  h2                 conda-forge/noarch::h2-4.2.0-pyhd8ed1ab_0 
  hpack              conda-forge/noarch::hpack-4.1.0-pyhd8ed1ab_0 
  httpcore           conda-forge/noarch::httpcore-1.0.9-pyh29332c3_0 
  httpx              conda-forge/noarch::httpx-0.28.1-pyhd8ed1ab_0 
  hyperframe         conda-forge/noarch::hyperframe-6.1.0-pyhd8ed1ab_0 
  idna               conda-forge/noarch::idna-3.10-pyhd8ed1ab_1 
  importlib-metadata conda-forge/noarch::importlib-metadata-8.7.0-pyhe01879c_1 
  importlib_resourc~ conda-forge/noarch::importlib_resources-6.5.2-pyhd8ed1ab_0 
  jaraco.classes     conda-forge/noarch::jaraco.classes-3.4.0-pyhd8ed1ab_2 
  jaraco.context     conda-forge/noarch::jaraco.context-6.0.1-pyhd8ed1ab_0 
  jaraco.functools   conda-forge/noarch::jaraco.functools-4.3.0-pyhd8ed1ab_0 
  jeepney            conda-forge/noarch::jeepney-0.9.0-pyhd8ed1ab_0 
  keyring            conda-forge/noarch::keyring-25.6.0-pyha804496_0 
  libblas            conda-forge/linux-64::libblas-3.11.0-5_h4a7cf45_openblas 
  libcblas           conda-forge/linux-64::libcblas-3.11.0-5_h0358290_openblas 
  libgfortran        conda-forge/linux-64::libgfortran-15.2.0-h69a702a_16 
  libgfortran5       conda-forge/linux-64::libgfortran5-15.2.0-h68bc16d_16 
  libglib            pkgs/main/linux-64::libglib-2.84.4-h77a78f3_0 
  libiconv           conda-forge/linux-64::libiconv-1.18-h3b78370_2 
  liblapack          conda-forge/linux-64::liblapack-3.11.0-5_h47877c9_openblas 
  libopenblas        conda-forge/linux-64::libopenblas-0.3.30-pthreads_h94d23a6_4 
  more-itertools     conda-forge/noarch::more-itertools-10.7.0-pyhd8ed1ab_0 
  msgpack-python     conda-forge/linux-64::msgpack-python-1.1.1-py39h74842e3_0 
  numpy              conda-forge/linux-64::numpy-2.0.2-py39h9cb892a_1 
  packaging          conda-forge/noarch::packaging-25.0-pyh29332c3_1 
  pbs-installer      conda-forge/noarch::pbs-installer-2025.8.18-pyhd8ed1ab_0 
  pcre2              conda-forge/linux-64::pcre2-10.46-h1321c63_0 
  pkginfo            conda-forge/noarch::pkginfo-1.12.1.2-pyhd8ed1ab_0 
  platformdirs       conda-forge/noarch::platformdirs-4.3.8-pyhe01879c_0 
  poetry             conda-forge/noarch::poetry-2.1.2-pyha804496_0 
  poetry-core        conda-forge/noarch::poetry-core-2.1.2-pyhd8ed1ab_0 
  pycparser          conda-forge/noarch::pycparser-2.22-pyh29332c3_1 
  pyproject_hooks    conda-forge/noarch::pyproject_hooks-1.2.0-pyhd8ed1ab_1 
  pysocks            conda-forge/noarch::pysocks-1.7.1-pyha55dd90_7 
  python-build       conda-forge/noarch::python-build-1.3.0-pyhff2d567_0 
  python-fastjsonsc~ conda-forge/noarch::python-fastjsonschema-2.21.2-pyhe01879c_0 
  python-installer   conda-forge/noarch::python-installer-0.7.0-pyhff2d567_1 
  python_abi         conda-forge/linux-64::python_abi-3.9-2_cp39 
  rapidfuzz          conda-forge/linux-64::rapidfuzz-3.13.0-py39hf88036b_0 
  requests           conda-forge/noarch::requests-2.32.5-pyhd8ed1ab_0 
  requests-toolbelt  conda-forge/noarch::requests-toolbelt-1.0.0-pyhd8ed1ab_1 
  secretstorage      conda-forge/linux-64::secretstorage-3.3.3-py39hf3d152e_3 
  shellingham        conda-forge/noarch::shellingham-1.5.4-pyhd8ed1ab_1 
  sniffio            conda-forge/noarch::sniffio-1.3.1-pyhd8ed1ab_1 
  tomli              conda-forge/noarch::tomli-2.2.1-pyhe01879c_2 
  tomlkit            conda-forge/noarch::tomlkit-0.13.3-pyha770c72_0 
  trove-classifiers  conda-forge/noarch::trove-classifiers-2025.8.6.13-pyhd8ed1ab_0 
  typing_extensions  conda-forge/noarch::typing_extensions-4.14.1-pyhe01879c_0 
  urllib3            conda-forge/noarch::urllib3-2.5.0-pyhd8ed1ab_0 
  virtualenv         conda-forge/noarch::virtualenv-20.34.0-pyhd8ed1ab_0 
  zipp               conda-forge/noarch::zipp-3.23.0-pyhd8ed1ab_0 
  zstandard          conda-forge/linux-64::zstandard-0.23.0-py39hd399759_3 

The following packages will be UPDATED:

  ca-certificates    pkgs/main/linux-64::ca-certificates-2~ --> conda-forge/noarch::ca-certificates-2026.1.4-hbd8a1cb_0 
  openssl              pkgs/main::openssl-3.0.18-hd6dcaed_0 --> conda-forge::openssl-3.6.0-h26f9b46_0 


Proceed ([y]/n)? 


Downloading and Extracting Packages:
                                                                                                                   
Preparing transaction: done                                                                                        
Verifying transaction: done                                                                                        
Executing transaction: done 
```

</details>

<br/>

Once `poetry` is installed, it can be used to automatically install all other dependencies of the project based on the `pyproject.toml` file. 
First, navigate to the project directory and remove the `poetry.lock` file, if it exists:
```console
(env_name) username@animus-c:~$ cd unox/
(env_name) username@animus-c:~unox$ rm poetry.lock
```
Then, use `poetry` to install the dependencies:
```console
(env_name) username@animus-c:~unox$ poetry install
```

Sometimes this will initially fail. 
Try running the `poetry install` command again immediately as this will often fix the issue and continue installing the dependencies. 

<details>

<summary>Expand for output</summary>

```console
(env_name) username@animus-c:~unox$ poetry install
Updating dependencies                                                                                              
Resolving dependencies... (40.5s)
                                                                                                                   
Package operations: 157 installs, 20 updates, 0 removals                                                           
                                                                                                                   
  - Installing attrs (25.4.0)
  - Installing rpds-py (0.27.1)
  - Updating typing-extensions (4.14.1 /home/conda/feedstock_root/build_artifacts/bld/rattler-build_typing_extensions_1751643513/work -> 4.15.0)
  - Installing referencing (0.36.2)
  - Installing six (1.17.0)
  - Installing jsonschema-specifications (2025.9.1)
  - Updating platformdirs (4.3.8 /home/conda/feedstock_root/build_artifacts/bld/rattler-build_platformdirs_1746710438/work -> 4.4.0)
  - Installing python-dateutil (2.9.0.post0)
  - Installing traitlets (5.14.3)
  - Installing tzdata (2025.3)
  - Updating zipp (3.23.0 /home/conda/feedstock_root/build_artifacts/zipp_1749421620841/work -> 3.23.0)
  - Installing arrow (1.4.0)
  - Updating fastjsonschema (2.21.2 /home/conda/feedstock_root/build_artifacts/bld/rattler-build_python-fastjsonschema_1755304154/work/dist -> 2.21.2)
  - Updating importlib-metadata (8.7.0 /home/conda/feedstock_root/build_artifacts/bld/rattler-build_importlib-metadata_1747934053/work -> 8.7.1)
  - Installing jsonschema (4.25.1)
  - Installing jupyter-core (5.8.1)
  - Installing lark (1.3.1)
  - Updating pycparser (2.22 /home/conda/feedstock_root/build_artifacts/bld/rattler-build_pycparser_1733195786/work -> 2.23)
  - Installing pyzmq (27.1.0)
  - Installing tornado (6.5.4)
  - Installing webencodings (0.5.1)
  - Updating cffi (1.17.1 /home/conda/feedstock_root/build_artifacts/cffi_1725571112467/work -> 2.0.0)
  - Installing fqdn (1.5.1)
  - Updating idna (3.10 /home/conda/feedstock_root/build_artifacts/idna_1733211830134/work -> 3.11)
  - Installing isoduration (20.11.0)
  - Installing jsonpointer (3.0.0)
  - Installing jupyter-client (8.6.3)
  - Installing markupsafe (3.0.3)
  - Installing nbformat (5.10.4)
  - Installing ptyprocess (0.7.0)
  - Installing rfc3339-validator (0.1.4)
  - Installing rfc3986-validator (0.1.1)
  - Installing rfc3987-syntax (1.1.0)
  - Installing soupsieve (2.8.1)
  - Installing tinycss2 (1.4.0)
  - Installing uri-template (1.3.0)
  - Installing webcolors (24.11.1)
  - Installing argon2-cffi-bindings (25.1.0)
  - Installing asttokens (3.0.1)
  - Installing beautifulsoup4 (4.14.3)
  - Installing bleach (6.2.0)
  - Installing defusedxml (0.7.1)
  - Updating exceptiongroup (1.3.0 /home/conda/feedstock_root/build_artifacts/exceptiongroup_1746947292760/work -> 1.3.1)
  - Installing executing (2.2.1)
  - Installing jinja2 (3.1.6)
  - Installing jupyterlab-pygments (0.3.0)
  - Installing mistune (3.2.0)
  - Installing nbclient (0.10.2)
  - Downgrading packaging (25.0 /home/conda/feedstock_root/build_artifacts/bld/rattler-build_packaging_1745345660/work -> 23.2)
  - Installing pandocfilters (1.5.1)
  - Installing parso (0.8.5)
  - Installing pure-eval (0.2.3)
  - Installing pygments (2.19.2)
  - Installing python-json-logger (4.0.0)
  - Installing pyyaml (6.0.3)
  - Installing terminado (0.18.1)
  - Installing wcwidth (0.2.14)
  - Updating anyio (4.10.0 /home/conda/feedstock_root/build_artifacts/bld/rattler-build_anyio_1754315087/work -> 4.12.1)
  - Installing argon2-cffi (25.1.0)
  - Updating certifi (2025.8.3 /home/conda/feedstock_root/build_artifacts/certifi_1754231422783/work/certifi -> 2026.1.4)
  - Updating charset-normalizer (3.4.3 /home/conda/feedstock_root/build_artifacts/charset-normalizer_1754767332901/work -> 3.4.4)
  - Installing decorator (5.2.1)
  - Updating h11 (0.16.0 /home/conda/feedstock_root/build_artifacts/h11_1745526374115/work -> 0.16.0)
  - Installing jedi (0.19.2)
  - Installing jupyter-events (0.12.0)
  - Installing jupyter-server-terminals (0.5.3)
  - Installing matplotlib-inline (0.2.1)
  - Installing nbconvert (7.16.6)
  - Installing overrides (7.7.0)
  - Installing pexpect (4.9.0)
  - Installing prometheus-client (0.23.1)
  - Installing prompt-toolkit (3.0.52)
  - Installing send2trash (2.0.0)
  - Installing stack-data (0.6.3)
  - Updating urllib3 (2.5.0 /home/conda/feedstock_root/build_artifacts/urllib3_1750271362675/work -> 2.6.2)
  - Installing websocket-client (1.9.0)
  - Installing babel (2.17.0)
  - Installing comm (0.2.3)
  - Installing debugpy (1.8.19)
  - Updating httpcore (1.0.9 /home/conda/feedstock_root/build_artifacts/bld/rattler-build_httpcore_1745602916/work -> 1.0.9)
  - Installing ipython (8.18.1)
  - Installing json5 (0.13.0)
  - Installing jupyter-server (2.17.0)
  - Installing mdurl (0.1.2)
  - Installing nest-asyncio (1.6.0)
  - Installing psutil (7.2.1)
  - Updating requests (2.32.5 /home/conda/feedstock_root/build_artifacts/requests_1755614211359/work -> 2.32.5)
  - Installing alabaster (0.7.16)
  - Installing async-lru (2.0.5)
  - Installing docutils (0.21.2)
  - Installing greenlet (3.2.4)
  - Updating httpx (0.28.1 /home/conda/feedstock_root/build_artifacts/httpx_1733663348460/work -> 0.28.1)
  - Installing imagesize (1.4.1)
  - Installing ipykernel (6.31.0)
  - Installing jupyter-lsp (2.3.0)
  - Installing jupyterlab-server (2.28.0)
  - Installing markdown-it-py (3.0.0)
  - Installing notebook-shim (0.2.4)
  - Downgrading numpy (2.0.2 /home/conda/feedstock_root/build_artifacts/numpy_1732314280888/work/dist/numpy-2.0.2-cp39-cp39-linux_x86_64.whl -> 1.26.4)
  - Installing pytz (2025.2)
  - Installing snowballstemmer (3.0.1)
  - Installing sphinxcontrib-applehelp (2.0.0)
  - Installing sphinxcontrib-devhelp (2.0.0)
  - Installing sphinxcontrib-htmlhelp (2.1.0)
  - Installing sphinxcontrib-jsmath (1.0.1)
  - Installing sphinxcontrib-qthelp (2.0.0)
  - Installing sphinxcontrib-serializinghtml (2.0.0)
  - Updating tomli (2.2.1 /home/conda/feedstock_root/build_artifacts/bld/rattler-build_tomli_1753796677/work -> 2.3.0)
  - Installing tqdm (4.67.1)
  - Installing absl-py (2.3.1)
  - Installing click (8.1.8)
  - Installing cycler (0.12.1)
  - Installing grpcio (1.76.0)
  - Installing h5py (3.14.0)
  - Installing iniconfig (2.1.0)
  - Installing jupyterlab (4.5.1)
  - Installing jupyterlab-widgets (3.0.16)
  - Installing kiwisolver (1.4.7)
  - Installing markdown (3.9)
  - Installing mdit-py-plugins (0.4.2)
  - Installing ml-dtypes (0.4.1)
  - Installing multiurl (0.3.7)
  - Installing namex (0.1.0)
  - Installing optree (0.18.0)
  - Installing pillow (11.3.0)
  - Installing pluggy (1.6.0)
  - Installing protobuf (4.25.8)
  - Installing pyparsing (3.3.1)
  - Installing rich (14.2.0)
  - Installing sphinx (7.4.7)
  - Installing sqlalchemy (2.0.45)
  - Installing tabulate (0.9.0)
  - Installing tensorboard-data-server (0.7.2)
  - Installing werkzeug (3.1.4)
  - Installing widgetsnbextension (4.0.15)
  - Installing astroid (3.3.11)
  - Installing astunparse (1.6.3)
  - Installing basemap-data (1.3.2)
  - Installing cftime (1.6.4.post1)
  - Installing coverage (7.10.7)
  - Installing ecmwf-datastores-client (0.4.1)
  - Installing flatbuffers (25.12.19)
  - Installing gast (0.7.0)
  - Installing google-pasta (0.2.0)
  - Installing ipywidgets (8.1.8)
  - Installing jupyter-cache (1.0.1)
  - Installing jupyter-console (6.6.3)
  - Installing keras (3.10.0)
  - Installing libclang (18.1.1)
  - Installing matplotlib (3.4.3)
  - Installing myst-parser (3.0.1)
  - Installing notebook (7.5.1)
  - Installing opt-einsum (3.4.0)
  - Installing pandas (1.5.3)
  - Installing pyproj (3.6.1)
  - Installing pyshp (2.3.1)
  - Installing pytest (8.4.2)
  - Installing shapely (2.0.7)
  - Installing sphinxcontrib-jquery (4.1)
  - Installing stdlib-list (0.12.0)
  - Installing tensorboard (2.17.1)
  - Installing tensorflow-io-gcs-filesystem (0.37.1)
  - Installing termcolor (3.1.0)
  - Installing wrapt (2.0.1)
  - Installing basemap (1.4.1)
  - Installing cartopy (0.22.0)
  - Installing cdsapi (0.7.7)
  - Installing jupyter (1.1.1)
  - Installing myst-nb (1.3.0)
  - Installing netcdf4 (1.7.2)
  - Installing proplot (0.9.7)
  - Installing pytest-cov (6.3.0)
  - Installing scipy (1.13.1)
  - Installing sphinx-autoapi (3.6.1)
  - Installing sphinx-rtd-theme (3.0.2)
  - Installing tensorflow (2.17.0)
  - Installing xarray (2024.3.0)

Writing lock file

Installing the current project: unox (0.1.1)
```

</details>

<br/>

If this runs without error, you should then be able to use the `unox` code base.
To confirm the location of where `unox` is installed, use `pip` to output a list of packages:
```console
(env_name) username@animus-c:~unox$ pip list
Package                       Version        Editable project location
----------------------------- -------------- -------------------------
absl-py                       2.3.1
...
typing_extensions             4.15.0
tzdata                        2025.2
unox                          0.1.1          /home/<username>/unox
uri-template                  1.3.0
urllib3                       2.5.0
...
```

Ensure the file path listed next to `unox` is the location of where you cloned the repository.
This will enable you to make changes to the `unox` code base in your cloned repository and have those changes be reflected when running parts of the code using your `conda` environment.
This is opposed to other installation methods, such as using `pip install` where the source code used would be in a different location.

<a id='config_vscodium'></a>
[back to top](#top)

## Configuring VSCodium

My IDE of choice is [VSCodium](https://vscodium.com/). As described on the website:

> "VSCodium is a community-driven, freely-licensed binary distribution of Microsoft’s editor VS Code."

Much of the functionality is the same as VS Code, but VSCodium does not send telemetry data to Microsoft. 

<a id='vsc_ssh'></a>
[back to top](#top)

### Connecting to remote machines

VSCodium can connect via SSH to a server and interact with code using their nice GUI, including all the extensions you might want installed, such as GitHub Copilot.

First, open the "Extensions" pane (the symbol is four squares next to each other) in VSCodium, and install the ["Open Remote - SSH" extension by `jeanp413`](https://github.com/jeanp413/open-remote-ssh) **<ins>on your local machine</ins>**. It is very similar to the "Remote - SSH" extension available with VSCode, however "Remote - SSH" is written in a way that is incompatible with VSCodium.

Once installed, I needed to go to the extension settings, and enable "Remote.SSH: Remote Server Listen On Socket" to get the connection to work. Your mileage may vary. 

You should now have a symbol in the left-hand panel of VSCodium that looks like a monitor and the hover text is "Remote Explorer." Clicking on that should bring up a panel with "SSH Targets." Assuming you have added the code to `~/.ssh/config` that was shown above (in [SSH into Trillium](#hpc_connect) and [Connecting to Animus](#animus_connect)), you should already have the targets `trillium` and `animus` available. 

Opening the `trillium` target should prompt you for a password. 
The box to type it in will appear at the top of the VSCodium window and should show hidden characters as you type, as opposed to typing in a password in a terminal where no indication is given while typing. 
Next, you should be able to select a folder, so look for `/scratch/<username>/<optional_directory>/unox`. 
This will prompt you to enter your password yet again. 
After going through this process the first time, on subsequent log-ins, a drop-down menu next to the `trillium` SSH target should allow to to directly select the `unox` directory next time you log in, meaning you should only need to type in your password once. 

Now, you should be able to select the "File explorer" side panel and see all the files in the `unox` repository.
Repeat the same process for the `animus` target, opening it in a new window.
You should now be able to see the `unox` repository on both remote machines in VSCodium.

**<ins>On both Animus and HPC</ins>**, open the "Extensions" pane and insure any extensions you use on a regular basis locally are installed on the remote system as well.
You are very unlikely to need the "Open Remote - SSH" extension on either Animus or HPC.

<a id='vsc_setup'></a>
[back to top](#top)

### Setting up VSCodium

If you are already familiar with VSCodium (or VSCode) you probably have a setup that you prefer. 
If that is the case, feel free to move on to the guide on {doc}`data <data>` the development {doc}`workflow <workflow>`.
Below, I list a few of the features that I find invaluable when I am coding as suggestions.
Remember to verify that the changes you make in VSCodium are propagated to both Animus and HPC.

#### Terminal panel

You can open a panel in the VSCodium window which displays a terminal prompt by going to the "View" menu and selecting "Terminal." 
This can also be done with the keyboard shortcut ``ctrl + ` `` (control and the backtick / tilde key). 
The console prompt is automatically set to the home directory open in the VSCodium window, which I find very convenient. 

#### Source Control panel

By going to the "View" menu and selecting "Source Control", you will open a panel which displays the status of the repository source control.
I usually put this panel on the right-hand side.
In the panel, you can see a live-updating list of "Changes" that `git` is tracking.
Each will have a letter on the right-hand side indicating the status of the file:
- `M`: Modified
    - A file which has already been added to `git` which has been changed since the last commit.
- `U`: Untracked
    - A file (usually a new one) which has not been added to `git`.
- `R`: Renamed
    - A file which has been renamed using the `git mv <file> <destination>` command.
- `D`: Deleted
    - A file which `git` has been tracking which has been deleted. Note: If an untracked file is deleted, it will not show up with this indicator, it will be gone.

This panel will also allow you to make commits using the GUI. 
You can click on a file under "Changes" to add it to the "Staged Changes" section.
Then, you can add a commit message in the text box at the top (I suggest using [Angular style commit messages](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines)), and click the "Commit" button to make a commit. 
When you are ready to push any number of commits to the remote repository on GitHub, you can do so under the "Outgoing" section. 

I also appreciate the "Timeline" feature of this panel.
When you select a particular file (that is, have it focused in your editor window), the "Timeline" will list the commits that have made changes to that file. 

#### Jupyter Notebooks

VSCodium can run Jupyter Notebooks by installing the `Jupyter` extension and it's extension pack which contains:
- `Jupyter Keymap`
- `Jupyter Notebook Renderers`
- `Jupyter Slide Show`
- `Jupyter Cell Tags`

Once this is installed, you can load and run Jupyter Notebooks using the virtual environments installed [above](#create_venvs). 

#### Live Preview

The `Live Preview` extension allows you to preview how `html` pages will look. 
I find this particularly helpful when editing the documentation files you are viewing right now. 
To learn more about how to edit this documentation, see the guide on {doc}`Writing Documentation <../docs_dev/write_docs>`.