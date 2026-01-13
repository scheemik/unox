<a id='top'></a>
# Running the model

The documentation below describes how to run the U-net model and retrieve the results. 
This guide assumes you have followed the instructions on the {doc}`Installation <installation>` and {doc}`Data <data>` pages.
<!-- Note: for linking between documents, use the `doc` role defined in the [Sphinx documentation](https://docs.readthedocs.com/platform/stable/guides/cross-referencing-with-sphinx.html#the-doc-role). 
TLDR: Create a link to a different document by typing `{doc}`, followed by the name of the file surrounded by backticks, excluding the extension. If you would like to change the rendered text of the link, surround the desired link text in backticks, then add the name of the file in angle brackets, in the format: "{doc}`Click here <filename>`".  -->

## Contents

- [Introduction](#intro)
- [Preparing a model run](#prep_model_run)
    - [From Animus to HPC](#from_animus_to_HPC)
    - [Input configuration files](#config_files)
- [Running the model on HPC](#run_model_HPC)
    - [Submitting a model run](#submit_job)
    - [Monitoring a job](#monitor_job)
- [Gathering model output](#get_output)
    - [From HPC to Animus](#from_HPC_to_animus)

---
<a id='intro'></a>
[back to top](#top)

## Introduction

As was mentioned under "Creating virtual environments" on the {doc}`Installation <installation>` page, the two remote machines, Trillium and Animus, are used for different parts of this project. 
Trillium has GPU resources which allow the U-net model to run quickly and efficiently. 
However, as Trillium is an Alliance Canada system, it can make it fairly restrictive and difficult to perform plotting and analysis tasks. 
Therefore, after running the model on Trillium, I transfer the output to Animus to do the analysis.
Animus also holds the data used to create the inputs for the model. 
Generally, I use Animus for all tasks related to this project except for running the model itself. 

This guide details how to prepare a model run on Animus, transfer that preparation to Trillium and run the model, then transfer the model output back to Animus. 
A demonstration of how to use the analysis tools can be found in the {doc}`Example usage <example>`.

---
<a id='prep_model_run'></a>
[back to top](#top)

## Preparing a model run

The preparation for a model run starts on Animus. 
In principle, you could use your local machine, avoiding Animus all together. 
However, in order to do so, you would need to download the relevant data and some are currently not publicly available.

<a id='from_animus_to_HPC'></a>
[back to top](#top)

### From Animus to HPC

The process of creating an input netCDF is explained on the {doc}`Data <data>` page. 
Below is an explanation of the command used to transfer input files from Animus to HPC. 
You only need to do this once per different input file.
If you plan on running many jobs with the same input file, you do not need to repeat this step every time.

The script `HPC_from_animus.sh` is set up to facilitate the transfer so you do not need to remember how to format a `scp` command and works by taking in the following arguments:
- `-f`: Filename
    - The name of the file to transfer.
    - Can be used individually, adding a `-f` flag for each file to transfer.
- `-i`: Inputfile
    - If specified, it will look for an input file with the name given in the `-f` flag.
    - This flag does not accept any input, it is just a binary.
- `-c`: Cluster
    - The name of the cluster to transfer to, the default being `trillium`.

Here is an example of transferring the `no2_sample_input` input file from Animus to Trillium:

```console
(uplt) username@animus-c:~/unox$ bash HPC_from_animus.sh -f no2_sample_input -i 
-c, No cluster specified, defaulting to trillium
-i, Copying full input file directory for no2_sample_input to trillium from Animus
Enter passphrase for key '/home/<username>/.ssh/<GH_id>': 
(<username>@trillium.alliancecan.ca) Duo two-factor login for <username>

Enter a passcode or select one of the following options:

 1. Duo Push to <mobile device>

Passcode or option (1-1): 1
Success. Logging you in...
input_metadata.json         100% 1307    90.1KB/s   00:00    
Y_2005.npy                  100%   19MB  24.6MB/s   00:00    
Y_2006.npy                  100%   19MB  61.1MB/s   00:00
...
X_2019.npy                  100%  168MB  84.3MB/s   00:01    
X_2020.npy                  100%  168MB  89.4MB/s   00:01    
no2_sample_input.nc         100% 3882MB  91.9MB/s   00:42
```

Note that the `.npy` files are now deprecated. 

<a id='config_files'></a>
[back to top](#top)

### Input configuration files

The parameters that a model run will use are defined in "input configuration" files. 
These are `.json` files stored in `inputfiles/_input_configs/` and follow the following format:

```json
{
    "input_set": "no2_lsm6",
    "x_vars": [
        "no2",
        "no2_tm1",
        "u10",
        "v10",
        "blh",
        "sp",
        "skt",
        "t2m",
        "ssrd"
    ],
    "stage_2": true,
    "stage_2_cutoff": 2013,
    "lsm_vars": [
    ],
    "grid_size": [35, 46]
}
```

The attributes of this file are explained below:
- `input_set`: The name of the input netCDF to use.
- `x_vars`: The list of variables to use as input to the model.
    - See the {doc}`Data <data>` page for documentation of these variables.
- `stage_2`: A boolean as to whether to run Stage 2 of training.
- `stage_2_cutoff`: The cutoff year for Stage 2 training.
    - Stage 2 training will start the year after the one specified here.
- `lsm_vars`: A list of variables on which to apply the land-sea mask (`lsm`).
- `grid_size`: A list of the number of grid cells to use in latitude and longitude.

When preparing for a model run, make sure the configuration file you wish to use is present on the HPC cluster in the `inputfiles/_input_configs/` directory. 
This can be accomplished by creating a configuration file on Animus, then using the `HPC_from_animus.sh` script to transfer it. 
Or, one can simply create a new configuration file on HPC directly, which is what I usually do.

---
<a id='run_model_HPC'></a>
[back to top](#top)

## Running the model on HPC

To actually run the model, go to the HPC, in this case, Trillium. 

<a id='submit_job'></a>
[back to top](#top)

### Submitting a model run

I have created a script, `HPC_job_submit.sh` which handles much of the boiler-plate necessary for submitting a job to the Alliance Canada scheduler and works by taking in the following arguments:
- `-j`: Job name
    - The name of the job to submit, the default being `test_unet`.
    - This should be a short and identifiable name (i.e., `grid_test0`, `grid_test1`, etc.).
    - If a directory under `HPC_runs/` with the specified name already exists, the script will prompt you to decide whether to overwrite it.
- `-i`: Input configuration file
    - The name of the configuration file in the `inputfiles/_input_configs/` directory to use.
    - The default is `sample_config`.
- `-t`: Type of run
    - The type of model run to use. Current options are:
        - `test`: The default job which runs the `run_model.py` script once using the `HPC_GPU_slurm.sh` launcher. 
        - `zfi_set`: A Zeroed Feature Importance run. This runs the `run_model.py` script a number of times equal to the number of "x" input variables using the `HPC_GPU_slurm.sh` launcher. 
- `-v`: Version
    - The version of the code to use, either `1` (default, current code) or `0` (legacy code).
    - This was implemented during the transition from Mist to Trillium and is deprecated. You can safely ignore this argument if only running on Trillium.
- `-c`: Cluster
    - The name of the cluster to transfer to, the default being `trillium`.

Here is an example of submitting a job named `example_job` to Trillium:

```console
username@HPC: unox$ bash HPC_job_submit.sh -j example_job
===== Begin HPC_job_submit.sh =====
-j, Name specified, using JOBNAME=example_job
-i, No config file specified, using CONFIG_FILE=sample_config
    Configuration file inputfiles/_input_configs/sample_config.json found.
-t, No run type specified, using TYPE=test
    Using LAUNCHER=HPC_GPU_slurm.sh
-v, No version specified, using VERSION=1
-c, Using cluster: trillium
Directory for job HPC_runs/example_job already exists
Would you like to overwrite it? (y/n)
y
Overwriting directory HPC_runs/example_job
Sending HPC notifications to email: <your_email@domain>
Submitted batch job 199403
[<username>@trig-login01 unox]$ 
```

The output can be used to confirm you set the arguments as expected. 

<a id='monitor_job'></a>
[back to top](#top)

### Monitoring a job

Most standard jobs take around 40 minutes to an hour to run. 
There are three main ways to monitor jobs as they are running: by email, the scheduler queue, or the log file.
For more information, see the Alliance Canada documentation on [Monitoring Jobs](https://docs.alliancecan.ca/wiki/Monitoring_jobs).

#### Email monitoring

By adding your email to the `HPC_slurm.sh` script as described on the {doc}`Installation <installation>`, you should receive emails every time a job begins or ends.
Here's an example email notifying of a job starting:

> Subject line: Trillium-GPU slurm Job_id=199403 Name=example_job Began, Queued time 00:00:01
> 
> Body of message:
> 
> ```console
> scontrol show jobid 199403
> JobId=199403 JobName=example_job
>   UserId=<username>(<userID>) GroupId=<username>(<userID>) MCS_label=N/A
>   Priority=958038 Nice=0 Account=def-dylan QOS=normal
>   JobState=RUNNING Reason=None Dependency=(null)
>   Requeue=0 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
>   RunTime=00:00:02 TimeLimit=01:00:00 TimeMin=N/A
>   SubmitTime=2026-01-13T14:13:03 EligibleTime=2026-01-13T14:13:03
>   AccrueTime=2026-01-13T14:13:03
>   StartTime=2026-01-13T14:13:04 EndTime=2026-01-13T15:13:04 Deadline=N/A
>   SuspendTime=None SecsPreSuspend=0 LastSchedEval=2026-01-13T14:13:04 Scheduler=Main
>   Partition=compute AllocNode:Sid=trig-login01:1848577
>   ReqNodeList=(null) ExcNodeList=(null)
>   NodeList=trig0012
>   BatchHost=trig0012
>   NumNodes=1 NumCPUs=24 NumTasks=1 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
>   ReqTRES=cpu=1,mem=192500M,node=1,billing=1,gres/gpu=1
>   AllocTRES=cpu=24,mem=192500M,node=1,billing=1,gres/gpu=1
>   Socks/Node=* NtasksPerN:B:S:C=0:0:*:* CoreSpec=*
>   MinCPUsNode=1 MinMemoryNode=192500M MinTmpDiskNode=0
>   Features=(null) DelayBoot=00:00:00
>   OverSubscribe=OK Contiguous=0 Licenses=(null) Network=(null)
>   Command=/scratch/<username>/unox/HPC_GPU_slurm.sh
>   WorkDir=/scratch/<username>/unox
>   Comment=/opt/slurm/bin/sbatch --export=NONE --get-user-env=L --job-name=example_job HPC_GPU_slurm.sh -j example_job -i default -t test -v 1 -c trillium
>   StdErr=/scratch/<username>/unox/HPC_runs/example_job/log_199403.txt
>   StdIn=/dev/null
>   StdOut=/scratch/<username>/unox/HPC_runs/example_job/log_199403.txt
>   CpusPerTres=gpu:24
>   TresPerNode=gres/gpu:1
>   MailUser=<your_email@domain> MailType=INVALID_DEPEND,BEGIN,END,FAIL,REQUEUE,STAGE_OUT
> ```

I highly recommend setting up a rule in your email client to automatically send emails from the scheduler to it's own folder so they don't clog up your main inbox.
You will not receive emails before the job has started and, depending on the day and how long you allot for the job to run, it can spend a significant time in the queue.

Once a job completes, you will receive an email like the one below:
> Subject line: Trillium-GPU slurm Job_id=199403 Name=example_job Ended, Run time 00:44:00, COMPLETED, ExitCode 0
> 
> Body of message:
> ```console
> scontrol show jobid 199403
> JobId=199403 JobName=example_job
>   UserId=<username>(<user_ID>) GroupId=<username>(<user_ID>) MCS_label=N/A
>   Priority=958038 Nice=0 Account=def-dylan QOS=normal
>   JobState=COMPLETED Reason=None Dependency=(null)
>   Requeue=0 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
>   RunTime=00:44:00 TimeLimit=01:00:00 TimeMin=N/A
>   SubmitTime=2026-01-13T14:13:03 EligibleTime=2026-01-13T14:13:03
>   AccrueTime=2026-01-13T14:13:03
>   StartTime=2026-01-13T14:13:04 EndTime=2026-01-13T14:57:04 Deadline=N/A
>   SuspendTime=None SecsPreSuspend=0 LastSchedEval=2026-01-13T14:13:04 Scheduler=Main
>   Partition=compute AllocNode:Sid=trig-login01:1848577
>   ReqNodeList=(null) ExcNodeList=(null)
>   NodeList=trig0012
>   BatchHost=trig0012
>   NumNodes=1 NumCPUs=24 NumTasks=1 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
>   ReqTRES=cpu=1,mem=192500M,node=1,billing=1,gres/gpu=1
>   AllocTRES=cpu=24,mem=192500M,node=1,billing=1,gres/gpu=1
>   Socks/Node=* NtasksPerN:B:S:C=0:0:*:* CoreSpec=*
>   MinCPUsNode=1 MinMemoryNode=192500M MinTmpDiskNode=0
>   Features=(null) DelayBoot=00:00:00
>   OverSubscribe=OK Contiguous=0 Licenses=(null) Network=(null)
>   Command=/scratch/<username>/unox/HPC_GPU_slurm.sh
>   WorkDir=/scratch/<username>/unox
>   Comment=/opt/slurm/bin/sbatch --export=NONE --get-user-env=L --job-name=example_job HPC_GPU_slurm.sh -j example_job -i default -t test -v 1 -c trillium
>   StdErr=/scratch/<username>/unox/HPC_runs/example_job/log_199403.txt
>   StdIn=/dev/null
>   StdOut=/scratch/<username>/unox/HPC_runs/example_job/log_199403.txt
>   CpusPerTres=gpu:24
>   TresPerNode=gres/gpu:1
>   MailUser=<your_email@domain> MailType=INVALID_DEPEND,BEGIN,END,FAIL,REQUEUE,STAGE_OUT
> 
> 
> sacct -j 199403
> JobID           JobName    Account    Elapsed  MaxVMSize     MaxRSS  SystemCPU    UserCPU ExitCode
> ------------ ---------- ---------- ---------- ---------- ---------- ---------- ---------- --------
> 199403       write_doc+  def-dylan   00:44:00                        04:10.694  15:13.927      0:0
> 199403.batch      batch  def-dylan   00:44:00          0  69889304K  04:10.692  15:13.927      0:0
> 199403.exte+     extern  def-dylan   00:44:00          0        28K  00:00.001   00:00:00      0:0
> ```

#### Scheduler queue monitoring

To monitor the jobs you have submitted, including those in the queue, you can use the [`squeue` command](https://slurm.schedmd.com/squeue.html) and add the `-u` flag with your username. 
To make this command easy to execute, I recommend adding this line to your `~/.bashrc` file on HPC:
```bash
# .bashrc
...
alias mysq='squeue -u <username>'
...
```
Then, monitoring the queue looks like this:
```console
username@HPC: unox$ mysq
  JOBID           USER      ACCOUNT         NAME  ST  TIME_LEFT  PARTITION NODES  TRES_PER_NODE NODELIST (REASON)
 199403     <username>    def-dylan  example_job   R      40:24    compute     1     gres/gpu:1 trig0012 (None)
```

The output is formatted to be very wide, so to make the columns line up correctly, you need to make your console window wide enough. 

The `ST` column give the status, which is usually `R` for running or `PD` for pending.
Once a job completes, it will no longer show up in this queue and you should get an email to notify you that it is done.
The `TIME_LEFT` column gives the amount of allocated time left that the job can use. 
Jobs will run until they complete or they hit this limit.

If you need to cancel a job, use the [`scancel` command](https://slurm.schedmd.com/scancel.html) with the job ID.
```console
username@HPC: unox$ scancel 199403
scancel: Terminating job 199403
```

### Log file monitoring

The last way to monitor a job is by the log file that is being continuously updated as the job is running. 
These logs will be in `HPC_runs/<name_of_run>/log_<job_ID>.txt` and capture everything that would go to the standard output from the code like `echo` and `print` statements.
If you open this file in VSCodium, it will update every time you navigate back to that tab.
This can be a useful way to see what part of the code a particular run is currently in. 
Note that the log files are very extensive, reaching 10's of thousands of lines.

<details>

<summary>Expand for relevant sections of an example log file</summary>

```txt
===== Begin HPC_slurm.sh =====
-j, Name specified, using JOBNAME=example_job
-i, Input files specified, using CONFIG_FILE=default
-t, Run type specified, using TYPE=test
    Using CODEFILE=src/unox/HPC/run_model.py
-c, Using cluster: trillium

Loading modules for Trillium HPC environment
-v 1, using updated code
Activating virtualenv from /home/<username>/.virtualenvs/unoxTrilliumNC/bin/activate

Directory for job HPC_runs/example_job already exists

Running src/unox/HPC/run_model.py with savedir HPC_runs/example_job

2026-01-13 14:13:22.248220: I tensorflow/core/util/port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
2026-01-13 14:13:23.058670: E external/local_xla/xla/stream_executor/cuda/cuda_fft.cc:485] Unable to register cuFFT factory: Attempting to register factory for plugin cuFFT when one has already been registered
2026-01-13 14:13:23.304601: E external/local_xla/xla/stream_executor/cuda/cuda_dnn.cc:8454] Unable to register cuDNN factory: Attempting to register factory for plugin cuDNN when one has already been registered
2026-01-13 14:13:23.380209: E external/local_xla/xla/stream_executor/cuda/cuda_blas.cc:1452] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
2026-01-13 14:13:23.980752: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F AVX512_VNNI AVX512_BF16 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
2026-01-13 14:13:31.845597: I tensorflow/core/common_runtime/gpu/gpu_device.cc:2021] Created device /job:localhost/replica:0/task:0/device:GPU:0 with 78763 MB memory:  -> device: 0, name: NVIDIA H100 80GB HBM3, pci bus id: 0000:06:00.0, compute capability: 9.0

===== Begin run_model.py =====
Current working directory: /scratch/<username>/unox
Using input arguments:
	argv[1], savedir: HPC_runs/example_job/
	argv[2], config_file: inputfiles/_input_configs/sample_config.json
	argv[3], version: 1
	Shape of first xtrain file: (364, 56, 120, 9)
	Shape of first ytrain file: (364, 56, 120, 1)
After concatenation:
	Shape of xtrain: (5096, 56, 120, 9)
	Shape of ytrain: (5096, 56, 120, 1)
After data split:
	Shape of xtrain: (4586, 56, 120, 9)
	Shape of ytrain: (4586, 56, 120, 1)
	Shape of xvalid: (510, 56, 120, 9)
	Shape of yvalid: (510, 56, 120, 1)
Done loading data sets for stage 1
(56, 120, 9)
	Shape of model input layer to build: ((56, 120, 9))
Model: "functional"
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Layer (type)        ┃ Output Shape      ┃    Param # ┃ Connected to      ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ model_input         │ (None, 56, 120,   │          0 │ -                 │
│ (InputLayer)        │ 9)                │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block1_Conv1        │ (None, 56, 120,   │     10,496 │ model_input[0][0] │
│ (Conv2D)            │ 128)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block1_Conv2        │ (None, 56, 120,   │    295,168 │ Block1_Conv1[0][… │
│ (Conv2D)            │ 256)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block1_MaxPool      │ (None, 28, 60,    │          0 │ Block1_Conv2[0][… │
│ (MaxPooling2D)      │ 256)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block2_Conv1        │ (None, 28, 60,    │    590,080 │ Block1_MaxPool[0… │
│ (Conv2D)            │ 256)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block2_Conv2        │ (None, 28, 60,    │  1,180,160 │ Block2_Conv1[0][… │
│ (Conv2D)            │ 512)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block2_MaxPool      │ (None, 14, 30,    │          0 │ Block2_Conv2[0][… │
│ (MaxPooling2D)      │ 512)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block3_Conv1        │ (None, 14, 30,    │  2,359,808 │ Block2_MaxPool[0… │
│ (Conv2D)            │ 512)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block3_Conv2        │ (None, 14, 30,    │  4,719,616 │ Block3_Conv1[0][… │
│ (Conv2D)            │ 1024)             │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block3_MaxPool      │ (None, 7, 15,     │          0 │ Block3_Conv2[0][… │
│ (MaxPooling2D)      │ 1024)             │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block4_Conv1        │ (None, 7, 15,     │  9,438,208 │ Block3_MaxPool[0… │
│ (Conv2D)            │ 1024)             │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block4_Conv2        │ (None, 7, 15,     │  9,438,208 │ Block4_Conv1[0][… │
│ (Conv2D)            │ 1024)             │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block4_Permute1     │ (None, 1024, 7,   │          0 │ Block4_Conv2[0][… │
│ (Permute)           │ 15)               │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block4_Reshape      │ (None, 1024, 105) │          0 │ Block4_Permute1[… │
│ (Reshape)           │                   │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block4_Permute2     │ (None, 105, 1024) │          0 │ Block4_Reshape[0… │
│ (Permute)           │                   │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ LSTM1 (LSTM)        │ (None, 105, 1024) │  8,392,704 │ Block4_Permute2[… │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ LSTM2 (LSTM)        │ (None, 105, 1024) │  8,392,704 │ LSTM1[0][0]       │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block5_Reshape      │ (None, 7, 15,     │          0 │ LSTM2[0][0]       │
│ (Reshape)           │ 1024)             │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block5_UpConv       │ (None, 14, 30,    │  2,097,664 │ Block5_Reshape[0… │
│ (Conv2DTranspose)   │ 512)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ lambda (Lambda)     │ (None, 14, 30,    │          0 │ Block5_UpConv[0]… │
│                     │ 512)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ lambda_1 (Lambda)   │ (None, 14, 30,    │          0 │ Block2_Conv2[0][… │
│                     │ 512)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ concatenate         │ (None, 14, 30,    │          0 │ lambda[0][0],     │
│ (Concatenate)       │ 2048)             │            │ Block3_Conv2[0][… │
│                     │                   │            │ lambda_1[0][0]    │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block5_Conv1        │ (None, 14, 30,    │  4,718,848 │ concatenate[0][0] │
│ (Conv2D)            │ 256)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block5_Conv2        │ (None, 14, 30,    │    590,080 │ Block5_Conv1[0][… │
│ (Conv2D)            │ 256)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block6_UpConv       │ (None, 28, 60,    │    262,400 │ Block5_Conv2[0][… │
│ (Conv2DTranspose)   │ 256)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ lambda_2 (Lambda)   │ (None, 28, 60,    │          0 │ Block6_UpConv[0]… │
│                     │ 256)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ lambda_3 (Lambda)   │ (None, 28, 60,    │          0 │ Block1_Conv2[0][… │
│                     │ 256)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ concatenate_1       │ (None, 28, 60,    │          0 │ lambda_2[0][0],   │
│ (Concatenate)       │ 1024)             │            │ Block2_Conv2[0][… │
│                     │                   │            │ lambda_3[0][0]    │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block6_Conv1        │ (None, 28, 60,    │  1,179,776 │ concatenate_1[0]… │
│ (Conv2D)            │ 128)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block6_Conv2        │ (None, 28, 60,    │    147,584 │ Block6_Conv1[0][… │
│ (Conv2D)            │ 128)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block7_UpConv       │ (None, 56, 120,   │     65,664 │ Block6_Conv2[0][… │
│ (Conv2DTranspose)   │ 128)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ lambda_4 (Lambda)   │ (None, 56, 120,   │          0 │ Block7_UpConv[0]… │
│                     │ 128)              │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ concatenate_2       │ (None, 56, 120,   │          0 │ lambda_4[0][0],   │
│ (Concatenate)       │ 384)              │            │ Block1_Conv2[0][… │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block7_Conv1        │ (None, 56, 120,   │    221,248 │ concatenate_2[0]… │
│ (Conv2D)            │ 64)               │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ Block7_Conv2        │ (None, 56, 120,   │     36,928 │ Block7_Conv1[0][… │
│ (Conv2D)            │ 64)               │            │                   │
├─────────────────────┼───────────────────┼────────────┼───────────────────┤
│ model_output        │ (None, 56, 120,   │         65 │ Block7_Conv2[0][… │
│ (Conv2D)            │ 1)                │            │                   │
└─────────────────────┴───────────────────┴────────────┴───────────────────┘
 Total params: 54,137,409 (206.52 MB)
 Trainable params: 54,137,409 (206.52 MB)
 Non-trainable params: 0 (0.00 B)

#### Begin training stage 1 ####
Epoch 1/250
2026-01-13 14:13:42.012413: I external/local_xla/xla/stream_executor/cuda/cuda_dnn.cc:531] Loaded cuDNN version 8905
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
W0000 00:00:1768331622.661541 3933740 gpu_timer.cc:114] Skipping the delay kernel, measurement accuracy will be reduced
...
W0000 00:00:1768331626.336762 3933742 gpu_timer.cc:114] Skipping the delay kernel, measurement accuracy will be reduced

[1m  1/153[0m [37m━━━━━━━━━━━━━━━━━━━━[0m [1m20:16[0m 8s/step - loss: 109.0138 - msenonzero: 109.0138 - r2_keras: -0.0754
[1m  3/153[0m [37m━━━━━━━━━━━━━━━━━━━━[0m [1m6s[0m 44ms/step - loss: 108.5387 - msenonzero: 108.5387 - r2_keras: -0.0764 
...

Epoch 250: val_loss did not improve from 7.37319

[1m55/55[0m [32m━━━━━━━━━━━━━━━━━━━━[0m[37m[0m [1m3s[0m 46ms/step - loss: 5.4319 - msenonzero: 5.4319 - r2_keras: 0.9313 - val_loss: 7.3870 - val_msenonzero: 7.3870 - val_r2_keras: 0.9012
Generating predictions for year: 2019

[1m 1/12[0m [32m━[0m[37m━━━━━━━━━━━━━━━━━━━[0m [1m0s[0m 36ms/step
[1m 5/12[0m [32m━━━━━━━━[0m[37m━━━━━━━━━━━━[0m [1m0s[0m 13ms/step
[1m 9/12[0m [32m━━━━━━━━━━━━━━━[0m[37m━━━━━[0m [1m0s[0m 13ms/step
[1m12/12[0m [32m━━━━━━━━━━━━━━━━━━━━[0m[37m[0m [1m0s[0m 14ms/step
Generating predictions for year: 2020

[1m 1/12[0m [32m━[0m[37m━━━━━━━━━━━━━━━━━━━[0m [1m0s[0m 40ms/step
[1m 5/12[0m [32m━━━━━━━━[0m[37m━━━━━━━━━━━━[0m [1m0s[0m 13ms/step
[1m 9/12[0m [32m━━━━━━━━━━━━━━━[0m[37m━━━━━[0m [1m0s[0m 13ms/step
[1m12/12[0m [32m━━━━━━━━━━━━━━━━━━━━[0m[37m[0m [1m0s[0m 14ms/step
output_metadata: {'savedir': 'HPC_runs/example_job/', 'config_path': 'inputfiles/_input_configs/sample_config.json', 'config_dict': {'input_set': 'no2_lsm6', 'x_vars': ['no2', 'no2_tm1', 'u10', 'v10', 'blh', 'sp', 'skt', 't2m', 'ssrd'], 'stage_2': True, 'stage_2_cutoff': 2013, 'lsm_vars': [], 'grid_size': [56, 120]}, 'version': 1, 'n_epochs': 250, 'model_fmt': 'keras', 'input_fmt': 'nc', 'split_year': 2019, 'split_value': 0.9, 'train_years': {'stage1': [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018], 'stage2': [2014, 2015, 2016, 2017, 2018]}, 'pred_years': {'stage1': [2019, 2020], 'stage2': [2019, 2020]}, 'unet_build_shape': (56, 120, 9)}

Done running test_unet.py

scontrol show job 199403
JobId=199403 JobName=example_job
   UserId=<username>(<user_ID>) GroupId=<username>(<user_ID>) MCS_label=N/A
   Priority=958038 Nice=0 Account=def-dylan QOS=normal
   JobState=COMPLETING Reason=None Dependency=(null)
   Requeue=0 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
   RunTime=00:44:00 TimeLimit=01:00:00 TimeMin=N/A
   SubmitTime=2026-01-13T14:13:03 EligibleTime=2026-01-13T14:13:03
   AccrueTime=2026-01-13T14:13:03
   StartTime=2026-01-13T14:13:04 EndTime=2026-01-13T14:57:04 Deadline=N/A
   SuspendTime=None SecsPreSuspend=0 LastSchedEval=2026-01-13T14:13:04 Scheduler=Main
   Partition=compute AllocNode:Sid=trig-login01:1848577
   ReqNodeList=(null) ExcNodeList=(null)
   NodeList=trig0012
   BatchHost=trig0012
   NumNodes=1 NumCPUs=24 NumTasks=1 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
   ReqTRES=cpu=1,mem=192500M,node=1,billing=1,gres/gpu=1
   AllocTRES=cpu=24,mem=192500M,node=1,billing=1,gres/gpu=1
   Socks/Node=* NtasksPerN:B:S:C=0:0:*:* CoreSpec=*
   MinCPUsNode=1 MinMemoryNode=192500M MinTmpDiskNode=0
   Features=(null) DelayBoot=00:00:00
   OverSubscribe=OK Contiguous=0 Licenses=(null) Network=(null)
   Command=/scratch/<username>/unox/HPC_GPU_slurm.sh
   WorkDir=/scratch/<username>/unox
   Comment=/opt/slurm/bin/sbatch --export=NONE --get-user-env=L --job-name=example_job HPC_GPU_slurm.sh -j example_job -i default -t test -v 1 -c trillium 
   StdErr=/scratch/<username>/unox/HPC_runs/example_job/log_199403.txt
   StdIn=/dev/null
   StdOut=/scratch/<username>/unox/HPC_runs/example_job/log_199403.txt
   CpusPerTres=gpu:24
   TresPerNode=gres/gpu:1
   MailUser=<your_email@domain> MailType=INVALID_DEPEND,BEGIN,END,FAIL,REQUEUE,STAGE_OUT
   

sacct -j 199403
JobID           JobName    Account    Elapsed  MaxVMSize     MaxRSS  SystemCPU    UserCPU ExitCode 
------------ ---------- ---------- ---------- ---------- ---------- ---------- ---------- -------- 
199403       write_doc+  def-dylan   00:44:00                         00:00:00   00:00:00      0:0 
199403.batch      batch  def-dylan   00:44:00                         00:00:00   00:00:00      0:0 
199403.exte+     extern  def-dylan   00:44:00                         00:00:00   00:00:00      0:0 

```

</details>

The end of the log file contains the same information as in the email notification that the job finished running. 

---
<a id='get_output'></a>
[back to top](#top)

## Gathering model output

Once the job has completed running sucessfully, the next step is to get the relevant output back to Animus for analysis.

<a id='from_HPC_to_animus'></a>
[back to top](#top)

### From HPC to Animus

The script `HPC_to_animus.sh` is set up to facilitate the transfer of job outputs so you do not need to remember how to format a `scp` command. 
It works by taking in the following arguments:
- `-f`: Filename
    - The name of the file to transfer.
    - Can be used individually, adding a `-f` flag for each file to transfer.
- `-j`: HPC job
    - If specified, it will look for a repository within `HPC_runs/` with the name given in the `-f` flag.
    - This flag does not accept any input, it is just a binary.
- `-c`: Cluster
    - The name of the cluster to transfer to, the default being `trillium`.
- `-m`: Model
    - Whether to transfer the model (`.keras`) files. Note, these files are large.
    - The default behavior will not transfer model files.
    - This flag does not accept any input, it is just a binary.

Here is an example of transferring the `example_job` model run from Animus to Trillium:

```console
(uplt) username@animus-c:~/unox$ bash HPC_to_animus.sh -f example_job -j 
-c, No cluster specified, defaulting to trillium
-j, Copying full HPC job directory for example_job from trillium to Animus
Enter passphrase for key '/home/<username>/.ssh/<GH_id>': 
(<username>@trillium.alliancecan.ca) Duo two-factor login for <username>

Enter a passcode or select one of the following options:

 1. Duo Push to <mobile device>

Passcode or option (1-1): 1
Success. Logging you in...
Completed file transfer to Animus
```

Now that the output from the model run is back on Animus, it can be analyzed.
See the {doc}`Analysis <analysis>` page for details.