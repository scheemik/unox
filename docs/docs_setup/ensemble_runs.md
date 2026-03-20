<a id='top'></a>
# Running ensemble models

The documentation below describes how to run the U-net model with multiple ensemble members, then aggregate and analyze their results.
This guide assumes you have followed the instructions on the {doc}`Running the model <run_model>` to be familiar with submitting single model runs and, additionally, worked through the guide on {doc}`Analyzing model output <analysis>` for a familiarity on how to plot different variables.
<!-- Note: for linking between documents, use the `doc` role defined in the [Sphinx documentation](https://docs.readthedocs.com/platform/stable/guides/cross-referencing-with-sphinx.html#the-doc-role). 
TLDR: Create a link to a different document by typing `{doc}`, followed by the name of the file surrounded by backticks, excluding the extension. If you would like to change the rendered link text of the link, surround the desired link text in backticks, then add the name of the file in angle brackets, in the format: "{doc}`Click here <filename>`".  -->

## Contents

- [Introduction](#intro)
- [Running ensembles](#run_ensemble)
    - [Preparing ensemble runs](#prep_ensemble)
    - [Submitting ensemble runs](#submit_ensemble)
    - [Monitoring ensemble jobs](#monitor_ensemble)
    - [Collecting ensemble results](#collect_results)
- [Analyzing ensemble output](#analyze_ensemble)
    - [Plotting ensemble members](#plot_ensemble_member)
    - [Box and whisker plots](#BaW_plots)
- [Example: Assessing impact of regularizers](#regularizers)
    - [What is a regularizer?](#what_is_regularizer)
    - [Configuring regularizer ensemble runs](#config_reg_ens)
    - [Plotting regularizer impact](#plot_reg_impact)

---
<a id='intro'></a>
[back to top](#top)

## Introduction

The U-net model is stochastic, meaning that when running it multiple times, even with the exact same input and parameters, the results will always differ, if only slightly.
This randomness is integral to how the U-net works, in contrast to models which are deterministic.
If you were to run the model twice with slightly different input, it would be difficult to say whether any differences in the output would be due to those differences in input, or simply due to the expected variability of the randomness.
To get an idea of what the spread of the stochastic variability is, we can run the U-net multiple times with the same configuration.
This is called an ensemble run.

For this project, each ensemble run is submitted as a separate job to HPC, equivalent to following the procedure in the guide to {doc}`Running the model <run_model>`.
Below, we will work through an example of how to use the infrastructure in this code to [avoid needing to submit each ensemble member separately](#submit_ensemble). 
Afterwards, I'll show how to use the plotting functions in this repository to [analyze ensemble run outputs](#analyze_ensemble), both using the functions shown in {doc}`Analyzing model output <analysis>` as well as functions specifically designed for plotting ensemble runs.
Lastly, I'll detail how ensemble runs can be used to assess a particular aspect of the model, in particular [the regularizer function](#regularizers).

---
<a id='run_ensemble'></a>
[back to top](#top)

## Running ensembles

<a id='prep_ensemble'></a>
[back to top](#top)

### Preparing ensemble runs

The preparation for ensemble runs is nearly identical to preparing a single model run, as described in the {doc}`Running the model <run_model>` guide.
The key difference is that you will use the `-e` flag on the `HPC_job_submit.sh` script to tell it to create and submit multiple ensemble members at once.

Ensure that the input configuration file you want to use exists on HPC in `inputfiles/_input_configs/`. 
For this example, I'll use the default configuration file, `inputfiles/_input_configs/sample_config.json`, the contents of which are shown below.

```{literalinclude} ../../inputfiles/_input_configs/sample_config.json
```

The attributes of this file are explained in {doc}`Running the model <run_model>`.
Make sure your desired configuration file is **<ins>on HPC</ins>**.
For the example that follows, I'll assume a custom configuration file called `my_new_config.json`.

<a id='submit_ensemble'></a>
[back to top](#top)

### Submitting ensemble runs

The `HPC_job_submit.sh` script includes a dedicated `-e` flag to handle ensemble submissions. 
This single command automatically:

- Creates the correct directory structure for all ensemble members
- Copies the configuration file to each member's directory
- Submits all jobs to the HPC scheduler with appropriate naming

To submit 5 ensemble members with the job name `no2_ens_test` using the `my_new_config` input configuration, run this **<ins>on HPC</ins>**:

```console
username@HPC: unox$ bash HPC_job_submit.sh -j no2_ens_test -i my_new_config -e 5
===== Begin HPC_job_submit.sh =====
-j, Name specified, using JOBNAME=no2_ens_test
-e, Ensemble size specified, using ENSEMBLE_SIZE=5
    Ensemble size is a valid integer from 1 to 99.
-i, Config files specified, using CONFIG_FILE=my_new_config
    Configuration file inputfiles/_input_configs/my_new_config.json found.
-t, No run type specified, using TYPE=test
    Using LAUNCHER=HPC_GPU_slurm.sh
-v, No version specified, using VERSION=1
-c, Using cluster: trillium
Creating directory for job no2_ens_test
    Creating subdirectories /01_no2_ens_test -- /05_no2_ens_test
Sending HPC notifications to email: <your_email@domain>
Submitted batch job 199501
Submitted batch job 199502
Submitted batch job 199503
Submitted batch job 199504
Submitted batch job 199505
```

The script creates this directory structure:

```
HPC_runs/
└── no2_ens_test/
    ├── ENSEMBLE_SIZE.txt          # Contains "5"
    ├── 01_no2_ens_test/
    │   └── input_config.json      # Copy of my_new_config.json
    ├── 02_no2_ens_test/
    │   └── input_config.json      # Same copy
    ├── 03_no2_ens_test/
    │   └── input_config.json      # Same copy
    ├── 04_no2_ens_test/
    │   └── input_config.json      # Same copy
    └── 05_no2_ens_test/
        └── input_config.json      # Same copy
```

Each subdirectory will accumulate output files (model, predictions, log files, etc.) as its corresponding job runs.

<a id='monitor_ensemble'></a>
[back to top](#top)

### Monitoring ensemble jobs

To see all your ensemble jobs in the queue, use the `mysq` alias created in the {doc}`Running the model <run_model>` guide (which amounts to `squeue -u <username>`) **<ins>on HPC</ins>**:

```console
username@HPC: unox$ mysq
  JOBID     USER      ACCOUNT                  NAME  ST  TIME_LEFT  PARTITION NODES  TRES_PER_NODE NODELIST (REASON)
 199501  <username>    def-dylan  no2_ens_test/01_n   R      58:32    compute     1     gres/gpu:1 trig0001 (None)
 199502  <username>    def-dylan  no2_ens_test/02_n   R      58:45    compute     1     gres/gpu:1 trig0002 (None)
 199503  <username>    def-dylan  no2_ens_test/03_n  PD         --    compute     1     gres/gpu:1 (Dependency)
 199504  <username>    def-dylan  no2_ens_test/04_n  PD         --    compute     1     gres/gpu:1 (QOSMaxJobsPerUserLimit)
 199505  <username>    def-dylan  no2_ens_test/05_n  PD         --    compute     1     gres/gpu:1 (QOSMaxJobsPerUserLimit)
```

Note that jobs may initially be in the `PD` (pending) state if there are queue limitations. 
They will start as earlier jobs complete.

If you are running multiple ensembles at the same time, you can filter the output with `grep` to just show lines for one particular ensemble.
Note that this will not show the column headings.

```console
username@HPC: unox$ mysq | grep no2_ens_test
 199501  <username>    def-dylan  no2_ens_test/01_n   R      58:32    compute     1     gres/gpu:1 trig0001 (None)
 199502  <username>    def-dylan  no2_ens_test/02_n   R      58:45    compute     1     gres/gpu:1 trig0002 (None)
 199503  <username>    def-dylan  no2_ens_test/03_n  PD         --    compute     1     gres/gpu:1 (Dependency)
 199504  <username>    def-dylan  no2_ens_test/04_n  PD         --    compute     1     gres/gpu:1 (QOSMaxJobsPerUserLimit)
 199505  <username>    def-dylan  no2_ens_test/05_n  PD         --    compute     1     gres/gpu:1 (QOSMaxJobsPerUserLimit)
```

As discussed in the {doc}`Running the model <run_model>` guide, you can also monitor the jobs by opening their individual log files and checking your email. 

<a id='collect_results'></a>
[back to top](#top)

### Collecting ensemble results

Once all ensemble jobs have completed, transfer the entire ensemble output directory back to Animus by running the following command **<ins>on Animus</ins>**:

```console
(uplt) username@animus-c:~/unox$ bash HPC_to_animus.sh -j -f no2_ens_test
-c, No cluster specified, defaulting to trillium
-j, Copying full HPC job directory for no2_ens_test from trillium to Animus
Directory ./HPC_runs/no2_ens_test does not exist, creating it.
Enter passphrase for key '/home/<username>/.ssh/<GH_id>': 
(<username>@trillium.alliancecan.ca) Duo two-factor login for <username>

Enter a passcode or select one of the following options:

1. Duo Push to <mobile device>

Passcode or option (1-1): 1
Success. Logging you in...
Checking ./HPC_runs/no2_ens_test for ensemble predictions to combine...
    Found ./HPC_runs/no2_ens_test/ENSEMBLE_SIZE.txt
    Combining predictions from ensemble run for no2_ens_test
===== Begin combine_predictions.py =====
Current working directory: /home/<username>/unox
Given input arguments:
        argv[1], jobname:    no2_ens_test (no2_ens_test)
                 savedir:    HPC_runs/no2_ens_test/
All `input_config.json` files match across the 5 ensemble members.
        Saving `input_config.json` to HPC_runs/no2_ens_test/
All `output_metadata.json` files match across the 5 ensemble members.
        Saving `output_metadata.json` to HPC_runs/no2_ens_test/
Combining predictions from 5 ensemble members...
        Removing redundant file: HPC_runs/no2_ens_test/01_no2_ens_test/predictions.nc
        Removing redundant file: HPC_runs/no2_ens_test/02_no2_ens_test/predictions.nc
        Removing redundant file: HPC_runs/no2_ens_test/03_no2_ens_test/predictions.nc
        Removing redundant file: HPC_runs/no2_ens_test/04_no2_ens_test/predictions.nc
        Removing redundant file: HPC_runs/no2_ens_test/05_no2_ens_test/predictions.nc
===== End combine_predictions.py =====

Checking ./HPC_runs/no2_ens_test/01_no2_ens_test for ensemble predictions to combine...
    No predictions within ./HPC_runs/no2_ens_test/01_no2_ens_test to combine
Checking ./HPC_runs/no2_ens_test/02_no2_ens_test for ensemble predictions to combine...
    No predictions within ./HPC_runs/no2_ens_test/02_no2_ens_test to combine
Checking ./HPC_runs/no2_ens_test/03_no2_ens_test for ensemble predictions to combine...
    No predictions within ./HPC_runs/no2_ens_test/03_no2_ens_test to combine
Checking ./HPC_runs/no2_ens_test/04_no2_ens_test for ensemble predictions to combine...
    No predictions within ./HPC_runs/no2_ens_test/04_no2_ens_test to combine
Checking ./HPC_runs/no2_ens_test/05_no2_ens_test for ensemble predictions to combine...
    No predictions within ./HPC_runs/no2_ens_test/05_no2_ens_test to combine
Completed file transfer to Animus
```

This single command transfers the entire `HPC_runs/no2_ens_test/` directory with all 5 ensemble members and their outputs back to Animus, then automatically runs `combine_predictions.py`.
That Python script will find all the individual `.nc` files from each ensemble member and combine them together.
During that process, the prediction variable names will have their ensemble number appended to them such that you can easily distinguish the predictions of each ensemble member later.
Finally, it deletes the now-redundant `.nc` files in each ensemble member's directory.
This will save on the storage space required on Animus.