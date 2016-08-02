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
                        to. (default: intelavx)  

