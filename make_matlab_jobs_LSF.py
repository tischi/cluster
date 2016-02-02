import sys
import os
import time
import shutil
import signal
import subprocess
import re
import random
import argparse
import itertools
import pdb


''' example calls:

python-2.7 /g/almf/software/scripts/cluster/cluster--fiji--20151118/make_jobs_LSF.py --xvfb "xvfb-run -a" --host_group intelavx --software "/g/emcf/software/Fiji/Fiji.app/ImageJ-linux64 -batch" --script /g/arendt/PrImR/PrImR48/Scripts/LifExt_Split.ijm --input_dir /g/arendt/PrImR/PrImR48/0lif/
/g/almf/software/scripts/cluster/matlab/make_matlab_jobs_LSF.py --


'''
 
NUM_JOBS_MAX = 100

def ensure_empty_dir(path):
    if os.path.isdir(path):
        print("Removing contents of {}".format(path))
        for entry in os.listdir(path):
            abspath = os.path.join(path, entry)
            if os.path.isdir(abspath):
                shutil.rmtree(abspath)
            elif os.path.isfile(abspath):
                os.remove(abspath)
            elif os.path.lexists(abspath):
                raise Exception(
                    "The path {} already exists. " \
                    "Please remove it manually.".format(abspath)
                )
    elif os.path.isfile(path):
        os.remove(path)
    elif os.path.lexists(path):
        raise Exception(
            "The path {} already exists. Please remove it manually." \
            .format(path)
        )
    else:
        print("Creating new folder {}".format(path))
        os.mkdir(path)

#
#/scratch/Nils/allframes/
 
#def make_jobs(xvfb, software, script, input_dir, output_dir, batch_size, max_jobs, memory, queue, host_group):    
def make_jobs(args):
    
    # how to make this nicer?
    xvfb = args.xvfb
    software = args.software
    script = args.script # not needed as "software" is software and script compiled into one file
    script_arguments = args.script_arguments
    input_dir = args.input_dir # /scratch/Nils/firstframe/ and then /scratch/Nils/allframes/
    output_dir = args.output_dir # just for internal use
    batch_size = args.batch_size
    max_jobs = args.max_jobs
    memory = args.memory
    queue = args.queue
    host_group = args.host_group
    matlab_version = args.matlab_version    
   
    print ''
    print 'make_matlab_jobs_LSF:'
    print ''
                
    # create directories
    input_dir = input_dir.rstrip(os.path.sep) # remove trailing slash if exists
    output_dir = input_dir + '--cluster'
    print('Cluster directory: {}'.format(output_dir))
   
    log_dir = os.path.join(output_dir, "log")  # contains information about job status
    job_dir = os.path.join(output_dir, "jobs") # contains the actual job scripts

    # create directories
    ensure_empty_dir(output_dir)
    ensure_empty_dir(log_dir)
    ensure_empty_dir(job_dir)

    #
    # get files or folders to analyze
    #
    files_or_folders_for_analysis = []
    files_or_folders = os.listdir(input_dir)
    #for root, directories, filenames in os.walk(input_dir):
    #  print "sub folders:", directories
    print "\nChecking {} input files...".format(len(files_or_folders))
    for file_or_folder in files_or_folders:
      if ("DS_Store" in file_or_folder):
        print "Skipping .DS_Store"
      elif ("humbs.db" in file_or_folder):
        print "Skipping Thumbs.db"
      else:
        files_or_folders_for_analysis.append(file_or_folder)
      
    nJobs = len(files_or_folders_for_analysis)
    
    for iJob in range(nJobs):

        # write the jobs to files
        script_name = "job_{}.sh".format(iJob + 1)
        script_name = os.path.join(job_dir, script_name)
        script_file = file(script_name, "w")

        # information to LSF
        txt = ['#!/bin/bash',
                '#BSUB -oo "{}/job_{}--out.txt"'.format(log_dir,iJob+1),
                '#BSUB -eo "{}/job_{}--err.txt"'.format(log_dir,iJob+1),
                '#BSUB -M {}'.format(memory),
                '#BSUB -R select[mem>{}] -R rusage[mem={}]'.format(memory,memory)
                ]
        txt = '\n'.join(txt)
        txt = txt + '\n'
        script_file.write(txt)

        if queue:
          script_file.write(
            '#BSUB -q {}\n'.format(queue)
          )        
          
        if host_group:
          script_file.write(
            '#BSUB -m {}\n'.format(host_group)
          )
          
        # set environment 
        if matlab_version == "8.3":
          txt = ['',
                 '# set ENVIRONMENT',
                 'MCRROOT=/g/software/linux/pack/matlab_runtime-8.3/bin/v83',
                 'LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/runtime/glnxa64',
                 'LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/bin/glnxa64',
                 'LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/sys/os/glnxa64',
                 'export LD_LIBRARY_PATH',
                 'XAPPLRESDIR=${MCRROOT}/X11/app-defaults',
                 'export XAPPLRESDIR'
                 ]
        elif matlab_version == "8.5":
          txt = ['',
                 '# set ENVIRONMENT',
                 'MCRROOT=/g/software/linux/pack/matlab-8.5',
                 'LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/runtime/glnxa64',
                 'LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/bin/glnxa64',
                 'LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/sys/os/glnxa64',
                 'LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/sys/opengl/lib/glnxa64',                 
                 'export LD_LIBRARY_PATH',
                 'XAPPLRESDIR=${MCRROOT}/X11/app-defaults',
                 'export XAPPLRESDIR'
                 ]        
        txt = '\n'.join(txt)
        txt = txt + '\n'
        script_file.write(txt)
        
        script_file.write(
            'echo "starting job"\n'
        )        

        # write a file to be able to check from the outside that the job has started
        script_file.write(
            'touch "{}/job_{}--started.touch"\n'.format(log_dir,iJob+1)
        )

        # do not produce core dumps  
        script_file.write(
            'ulimit -c 0\n'
        )        
                
        txt = ['echo "hostname:"',
               'hostname',
               'echo "number of cores:"',
               'nproc',
               'echo "total RAM:"',
               'head -1 /proc/meminfo'
               ]
        txt = '\n'.join(txt)
        txt = txt + '\n'
        script_file.write(txt)

        # commands to help mounting file shares
        #script_file.write(
        #    'ls /g/software/linux/pack/jdk-6u18/jre/lib/amd64/server\n'
        #)
       
        #software_with_quotation = r'"{}"'.format(software)
        #script_with_quotation = r'"{}"'.format(script)
        #script_arguments__input_file = r'"{} {}"'.format(script_arguments, os.path.join(input_dir, files_or_folders_for_analysis[iJob]))
      
        input_file = os.path.join(input_dir, files_or_folders_for_analysis[iJob])
        
        # generate the actual command that is run on the node
        cmd = [software,
               input_file,
               script_arguments]
        cmd = ' '.join(cmd)
        script_file.write(cmd + '\n')

        script_file.write(
            'echo "job finished"\n'
        )        

        # this is the last line in the script, because this will be displayed as the job name by LSF
        script_file.write(
            '# job {}\n'.format(iJob)
        )        
        
        script_file.close()
        
        # make script executable
        os.system('chmod a+x {}'.format(script_name))

    return job_dir, nJobs



if __name__ == '__main__':

    #python-2.7 /g/almf/software/scripts/cluster/20151118--HernandoMartinez--Fiji/make_jobs_LSF.py --xvfb xvfb --software "/g/almf/software/Fiji.app/ImageJ-linux64 -macro" --script /g/almf/tischer/Hernando/Scripts/FolderRigidOrient.ijm --input_dir /g/almf/tischer/Hernando/OrientedDapi
    ''' example calls:
    python-2.7 /g/almf/software/scripts/cluster/make_matlab_jobs_LSF.py  --host_group intelavx --software "/scratch/Nils/LFdeconvolution/test1/main_reconstruct_single" --matlab_version 8.3 --input_dir /scratch/Nils/LFdeconvolution/test1/inputfiles/ --script_arguments "/scratch/Nils/LFdeconvolution/test1/output /scratch/Nils/PSF_40x095NAair.mat 1269.7 1082.05 22.645 is_first_frame 1" 
    '''

    description = '''
    Prepares LSF jobs for running complied MATLAB scripts on each file (or folder) in the input_dir. 
    For each job one file will be stored in an automatically generated folder, 
    which will have the name of your --input_dir + "--cluster/jobs". It is very instructive to inspect the job files, which are simple text, e.g. to determine sources of errors.
    Once job generation is finished this script will print a command to run the jobs (using run_jobs_LSF.py);
    you may simply copy and paste this command and press enter to execute it.
    '''
   
    # parse arguments
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #
    parser.add_argument('--software', dest='software', default='',
                        help='(required) full path to your compiled matlab script.')
    parser.add_argument('--input_dir', dest='input_dir', default='',
                        help='(required) full path to the folder containing the data to be analyzed.')
    parser.add_argument('--matlab_version', dest='matlab_version', default='8.3',
                        help='(required) specify matlab version (currently installed are "8.3", "8.5"). this ensures that the correct MCR (MATLAB Compiler Runtime) will be used for your jobs.')
    #parser.add_argument('--script', dest='script', default='',
    #                    help='(required) full path to the fiji script that you want to run.')
    parser.add_argument('--script_arguments', dest='script_arguments', default='',
                        help='arguments/options that your MATLAB script takes (in addition to the file/folder to be analyzed, which will be determined from the --input_dir for each job automatically.)')
    parser.add_argument('--xvfb', dest='xvfb', default='', 
                        help='specify software providing a virtual frame buffer ("xvfb-run -a"); normally not necessary for MATLAB scripts.')            
    #parser.add_argument('--output_dir', dest='output_dir', default='')
    parser.add_argument('--memory', dest='memory', default='16000',
                        help='memory that you want to allocate on the cluster node in MB.')
    #parser.add_argument('--batch_size', dest='batch_size', type=int, default=-1)
    #parser.add_argument('--max_jobs', dest='max_jobs', type=int,
    #                    default=NUM_JOBS_MAX)
    parser.add_argument('--queue', dest='queue', default='',
                        help='select a specific queue to submit your jobs to; this selects a subset of the available nodes with specific properties, e.g. "bigmem" selects nodes with a lot of memory.') # bigmem
    parser.add_argument('--host_group', dest='host_group', default='intelavx',
                           help='select a specific group of nodes to submit your jobs to.') 

                    
    args = parser.parse_args()
    
    supported_matlab_runtime_versions = ["8.3","8.5"]
    if not args.matlab_version:
      print "you need to specify --matlab_version, currently we have",supported_matlab_runtime_versions
    elif not args.matlab_version in supported_matlab_runtime_versions:
      print "matlab_version",args.matlab_version,"is not supported!"
      sys.exit(-1)
      
    # create the jobs
    #job_dir, nJobs = make_jobs(args.xvfb, args.software, args.script, args.input_dir, args.output_dir, args.batch_size, args.max_jobs, args.memory, args.queue, args.host_group)
    job_dir, nJobs = make_jobs(args)
    
    # print some information about the jobs
    print ''
    print 'Number of jobs:',nJobs
    print 'Job directory:',job_dir
    print ''
    print 'Command to spawn jobs on cluster:'
    print 'python-2.7 /g/almf/software/scripts/cluster/run_jobs_LSF.py --job_dir',job_dir
    print ''

