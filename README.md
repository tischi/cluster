# cluster
Scripts for managing distributed computing. 

## brief description
The scripts will make, submit and monitor jobs on LSF.
make_fiji_jobs_LSF.py and make_matlab_jobs_LSF.py will generate job files which are then submitted by run_jobs_LSF.py and monitored by check_jobs_LSF.py.


## make_matlab_jobs_LSF.py

__python-2.7 make_matlab_jobs_LSF.py --help__  
  
usage: make_matlab_jobs_LSF.py [-h] [--software SOFTWARE]  
                               [--input_dir INPUT_DIR]  
                               [--matlab_version MATLAB_VERSION]  
                               [--script_arguments SCRIPT_ARGUMENTS]  
                               [--xvfb XVFB] [--memory MEMORY] [--queue QUEUE]  
                               [--host_group HOST_GROUP]  
  
Prepares LSF jobs for running complied MATLAB scripts on each file (or folder)
in the input_dir. For each job one file will be stored in an automatically
generated folder, which will have the name of your --input_dir + "--
cluster/jobs". It is very instructive to inspect the job files, which are
simple text, e.g. to determine sources of errors. Once job generation is
finished this script will print a command to run the jobs (using
run_jobs_LSF.py); you may simply copy and paste this command and press enter
to execute it.  
  
optional arguments:  
  -h, --help            show this help message and exit  
  --software SOFTWARE   (required) full path to your compiled matlab script.
                        (default: )  
  --input_dir INPUT_DIR  
                        (required) full path to the folder containing the data
                        to be analyzed. (default: )  
  --matlab_version MATLAB_VERSION  
                        (required) specify matlab version (currently installed
                        are "8.3", "8.5"). this ensures that the correct MCR
                        (MATLAB Compiler Runtime) will be used for your jobs.
                        (default: 8.3)  
  --script_arguments SCRIPT_ARGUMENTS  
                        arguments/options that your MATLAB script takes (in
                        addition to the file/folder to be analyzed, which will
                        be determined from the --input_dir for each job
                        automatically.) (default: )  
  --xvfb XVFB           specify software providing a virtual frame buffer
                        ("xvfb-run -a"); normally not necessary for MATLAB
                        scripts. (default: )  
  --memory MEMORY       memory that you want to allocate on the cluster node
                        in MB. (default: 16000)  
  --queue QUEUE         select a specific queue to submit your jobs to; this
                        selects a subset of the available nodes with specific
                        properties, e.g. "bigmem" selects nodes with a lot of
                        memory. (default: )  
  --host_group HOST_GROUP  
                        select a specific group of nodes to submit your jobs
                        to. (default: intelavx)  

## make_fiji_jobs.py  

__python-2.7 make_fiji_jobs_LSF.py --help__  
  
usage: make_fiji_jobs_LSF.py [-h] [--software SOFTWARE]  
                             [--input_dir INPUT_DIR] [--script SCRIPT]  
                             [--script_arguments SCRIPT_ARGUMENTS]  
                             [--xvfb XVFB] [--memory MEMORY] [--queue QUEUE]  
                             [--host_group HOST_GROUP]  
  
Prepares LSF jobs for running Fiji scripts on each file (or folder) in the
input_dir. For each job one file will be stored in an automatically generated
folder, which will have the name of your --input_dir + "--cluster/jobs". It is
very instructive to inspect the job files, which are simple text, e.g. to
determine sources of errors. Once job generation is finished this script will
print a command to run the jobs (using run_jobs_LSF.py); you may simply copy
and paste this command and press enter to execute it.  
  
optional arguments:  
  -h, --help            show this help message and exit  
  --software SOFTWARE   (required) full path to your fiji installation,
                        including options for running it. (default:
                        /g/emcf/software/Fiji/Fiji.app/ImageJ-linux64 -batch)  
  --input_dir INPUT_DIR  
                        (required) full path to the folder containing the data
                        to be analyzed. (default: )  
  --script SCRIPT       (required) full path to the fiji script that you want
                        to run. (default: )  
  --script_arguments SCRIPT_ARGUMENTS  
                        arguments/options that your script takes (in addition
                        to the file/folder to be analyzed, which will be
                        determined from the --input_dir for each job
                        automatically.) (default: )  
  --xvfb XVFB           specify software providing a virtual frame buffer;
                        this is necessary to handle possible graphics output
                        of fiji. (default: "xvfb-run -a")  
  --memory MEMORY       memory that you want to allocate on the cluster node
                        in MB. (default: 16000)  
  --queue QUEUE         select a specific queue to submit your jobs to; this
                        selects a subset of the available nodes with specific
                        properties, e.g. "bigmem" selects nodes with a lot of
                        memory. (default: )  
  --host_group HOST_GROUP  
                        select a specific group of nodes to submit your jobs
                        to. (default: fujitsu)  


## EMBL specific information

The scripts are hosted on: /g/almf/software/scripts/cluster

### Example of calling fiji scripts on the cluster at EMBL Heidelberg

- log onto submaster1
  - open terminal (on mac: in-built; on windows: install cygwin)   
  - ssh username@submaster1 
  - to get help type:
     ```python-2.7 /g/almf/software/scripts/cluster/make_fiji_jobs_LSF.py --help```
  - to start it type for instance:
     ```python-2.7 /g/almf/software/scripts/cluster/make_fiji_jobs_LSF.py --xvfb "xvfb-run -a" --software "/g/emcf/software/Fiji/Fiji.app/ImageJ-linux64 -batch" --script /g/my_group/my_script.ijm --input_dir /g/my_group/my_folder_with_data/```

#### Specific call for data in fiji_devel/examples folder

```python-2.7 /g/almf/software/scripts/cluster/make_fiji_jobs_LSF.py --memory 16000 --xvfb "xvfb-run -a" --software "/g/emcf/software/Fiji/Fiji.app/ImageJ-linux64 -batch" --script "/g/almf/software/scripts/cluster/fiji_devel/examples/macro_1image.ijm" --input_dir "/g/almf/software/scripts/cluster/fiji_devel/examples/data"```

### Running CellProfiler on the EMBL compute cluster

Note that the EMBL compute cluster only has access to 'tier1' file-servers

#### Configure your pipeline

- open a terminal window (on Windows use Cygwin, on a Mac just the normal one)

```ssh -Y YOUR_USER_NAME@submaster1```
- it may ask you a question, if so, answer: yes
- enter your password
- now you are on the submaster computer, next you run CellProfiler as an interactive cluster job:
```bsub -XF -Is CellProfiler-2.0.11047```
- it may ask you a question, if so, answer: yes
- you may have to enter your password again
- the CellProfiler GUI should open
- if it asks you to download new versions say SKIP THIS VERSION
- load your pipeline (it has to be on a tier1 network drive, e.g. on /g/almfscreen/username)
- in the __LoadImages__ module at the bottom of the settings: __Input image file location__: __Elsewhere__ select the folder with your image data
- using CellProfiler's __[Test > Start Test Run]__ adapt all necessary module paramters
- specifically, in the last module __CreateBatchFiles__ select an __Output folder path__ on your server  
- __[Analyze images]__
  - this will not yet analyse your data but just create the __Batch_data.mat__ file to be spawn on the cluster (s. b.)
  - remember where the __Batch_data.mat__ file is stored (you'll need it soon)
- Exit CellProfiler

#### Distribute jobs on the cluster

- you have to be on __submaster1__ (s.a.)
  - (tech note: you need the graphics forwarding '-Y' also for this step) 
- execute: ```/g/almf/software/scripts/cluster/make_cellprofiler_jobs_LSF.sh --software CellProfiler-2.0.11047 --script /g/YOUR_FOLDER_LOCATION/Batch_data.mat``
  - this will prepare the jobs but not run them yet.
  - now, follow all instructions printed to the terminal window (i.e. copy and paste and execute some commands), to:
    - spawn the jobs
    - monitor the jobs
    - concatenate the output tables

