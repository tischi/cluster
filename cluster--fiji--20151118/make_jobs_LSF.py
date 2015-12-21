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

 
#def make_jobs(xvfb, software, script, input_dir, output_dir, batch_size, max_jobs, memory, queue, host_group):    
def make_jobs(args):
    
    # how to make this nicer?
    xvfb = args.xvfb
    software = args.software
    script = args.script
    script_arguments = args.script_arguments
    input_dir = args.input_dir 
    output_dir = args.output_dir
    batch_size = args.batch_size
    max_jobs = args.max_jobs
    memory = args.memory
    queue = args.queue
    host_group = args.host_group    
   
    print ''
    print 'make_jobs_LSF:'
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
    for file_or_folder in files_or_folders:
      if not (("humbs.db" or ".DS_store") in file_or_folder):
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

        
        # generate the actual command
        ## examples
        ##   software: "ImageJ-linux64 -macro"
        ##   script: "
        def make_command(xvfb, software, script, script_arguments):
            cmd = [xvfb,
                software,
                script,
                script_arguments
            ]
            return ' '.join(cmd)

        #print script_arguments
        software_with_quotation = r'"{}"'.format(software)
        script_with_quotation = r'"{}"'.format(script)
        script_arguments__input_file = r'"{} {}"'.format(script_arguments, os.path.join(input_dir, files_or_folders_for_analysis[iJob]))
        #print script_arguments__input_file
        
        cmd = make_command(xvfb, software_with_quotation, script_with_quotation, script_arguments__input_file)
        script_file.write(cmd + '\n')

        script_file.write(
            'echo "job finished"\n'
        )        
        
        script_file.close()
        
        # make script executable
        os.system('chmod a+x {}'.format(script_name))

    return job_dir, nJobs



if __name__ == '__main__':

    #python-2.7 /g/almf/software/scripts/cluster/20151118--HernandoMartinez--Fiji/make_jobs_LSF.py --xvfb xvfb --software "/g/almf/software/Fiji.app/ImageJ-linux64 -macro" --script /g/almf/tischer/Hernando/Scripts/FolderRigidOrient.ijm --input_dir /g/almf/tischer/Hernando/OrientedDapi/

    try:

        # parse arguments
        parser = argparse.ArgumentParser(
                    description='Make LSF jobs.')
        parser.add_argument('--xvfb', dest='xvfb', default='')            
        parser.add_argument('--software', dest='software', default='')
        parser.add_argument('--script', dest='script', default='')
        parser.add_argument('--script_arguments', dest='script_arguments', default='')
        parser.add_argument('--input_dir', dest='input_dir', default='')
        parser.add_argument('--output_dir', dest='output_dir', default='')
        parser.add_argument('--memory', dest='memory', default='8000')
        parser.add_argument('--batch_size', dest='batch_size', type=int,
                            default=-1)
        parser.add_argument('--max_jobs', dest='max_jobs', type=int,
                            default=NUM_JOBS_MAX)
        parser.add_argument('--queue', dest='queue', default='') # bigmem
        parser.add_argument('--host_group', dest='host_group', default='') # intelavx
        
            
                            
        args = parser.parse_args()
       
        # create the jobs
        #job_dir, nJobs = make_jobs(args.xvfb, args.software, args.script, args.input_dir, args.output_dir, args.batch_size, args.max_jobs, args.memory, args.queue, args.host_group)
        job_dir, nJobs = make_jobs(args)
        
        # print some information about the jobs
        print ''
        print 'Number of jobs:',nJobs
        print 'Job directory:',job_dir
        print ''
        print 'Command to spawn jobs on cluster:'
        print 'python-2.7 /g/almf/software/scripts/cluster/cluster--fiji--20151118/run_jobs_LSF.py --job_dir',job_dir
        print ''
    
    except:
        import traceback
        traceback.print_exc()
        exit_code = -1
        
    finally:
        print ""
