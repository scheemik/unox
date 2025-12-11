<a id='top'></a>
# Installation

The documentation below describe how to install this package to enable active development. 
If you are interested in simply using `unox`, refer to the installation instructions in the {doc}`README <index>`.
<!-- Note: for linking between documents, use the `doc` role defined in the [Sphinx documentation](https://docs.readthedocs.com/platform/stable/guides/cross-referencing-with-sphinx.html#the-doc-role). 
TLDR: Create a link to a different document by typing `{doc}`, followed by the name of the file surrounded by backticks, excluding the extension. If you would like to change the rendered text of the link, surround the desired link text in backticks, then add the name of the file in angle brackets, in the format: "{doc}`Click here <filename>`".
In order to link to the README file as I did above, I need to actually link to the `index.html` file which is in the same directory as this current file. Linking to a file up the directory structure is difficult, but the README is included in the `index.html` file, and therefore I can link to it that way.  -->

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

## Contents

- [Remote connections](#connecting)
    - [Connecting to HPC](#hpc_connect)
    - [Connecting to Animus](#animus_connect)

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

Below, we detail how to connect to each of these remote machines.

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
Then, copy your public key by using the output of this command:
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
# In username@HPC:/Users/username/.ssh/config
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
# In username@HPC:/Users/username/.ssh/config
HOST animus
  HOSTNAME animus-c.atmosp.physics.utoronto.ca
  User <username>
```

