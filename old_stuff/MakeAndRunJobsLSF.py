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

JAVA_VM_RUNNING = False
LOOP_WAIT_TIME = 60
NUM_JOBS_MAX = 100
JOB_FILE_PATTERN = 'job_{}.sh'
WAIT_BETWEEN_JOB_SUBMISSIONS = 0.2 # seconds


JOB_NAME_PATTERN = re.compile('.*<(?P<jobnr>)>.*')


def run_jobs(jobcount, jobDir, logDir):
    for i in range(1,jobcount+1): # jobcount+1
        jobFile = "job_{}.sh".format(i)
        jobPath = os.path.join(jobDir,jobFile)
        cmd = 'bsub < "{}"'.format(jobPath)
        time.sleep(WAIT_BETWEEN_JOB_SUBMISSIONS)
        os.system(cmd)
    return 0
    

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




def prepare_jobs(delete=True, num_jobs_max=200):    
     
    
    # create cluster directories
    output_dir = input_dir + '--batchRunner'
    print('Output directory: {}'.format(output_dir))
   
    dirLog = os.path.join(output_dir, "log")  # contains information about job status
    dirJobs = os.path.join(output_dir, "jobs") # contains the actual job scripts

    if delete:
        ensure_empty_dir(output_dir)
        ensure_empty_dir(dirLog)
        ensure_empty_dir(dirJobs)

    
    # create the job files

    # you somehow have to compute how many jobs you will have
    nJobs = 
    
    for iJob in range(0, nJobs):
    
        # header for the scripts of the individual jobs
        head = ['#!/bin/bash',
                '#BSUB -oo "{}/job_{}--out.txt"'.format(dirTxtOut,iJob+1),
                '#BSUB -eo "{}/job_{}--err.txt"'.format(dirTxtOut,iJob+1),
                '#BSUB -M 8000',
                '#BSUB -R select[mem>8000] -R rusage[mem=8000]'
                ]
        head = '\n'.join(head)
        head = head + '\n'

        # write the jobs to files
        script_name = JOB_FILE_PATTERN.format(iJob + 1)
        script_name = os.path.join(dirJobs, script_name)
        script_file = file(script_name, "w")

        script_file.write(head)

        script_file.write(
            'sleep {}\n'.format((iJob+1)*0.2)
        )
                
        script_file.write(
            'ulimit -c 0\n'
        )        
                
        script_file.write(
            'ls /g/software/linux/pack/jdk-6u18/jre/lib/amd64/server\n'
        )

        script_file.write(
            'echo "The job started:"\n'
        )        
        
        script_file.write(
            'touch "{}/job_{}--started.touch"\n'.format(dirTxtOut,iJob+1)
        )

        # ???
        script_file.write(content)
        
        script_file.write(
            'echo "FIJI started:"\n'
        )
      
        #if len(grouping_keys) > 0:
        # grouping => all images of one group together
        input_directory_option = ""
        if input_dir is not None:
            input_directory_option = \
                "-i {}".format(input_dir)
        output_directory_option = \
            "-o {}".format(output_dir)
        plugin_directory_option = ""
        if cp_plugin_directory is not None:
            plugin_directory_option = \
                "--plugins-directory={}".format(cp_plugin_directory)
        
        # add the line to the script that executes the program (e.g., CellProfiler or FIJI)
        def make_command(fiji_binary, fiji_script, ...):
            cmd = [
                fiji_binary,
                "--headless",
                "--mem=1000m",
                "{}".format(fiji_script),
                input_directory,
                output_directory
            ]
            return ' '.join(cmd)
      
        cmd = make_cp_command(start, end)  # 
        script_file.write(cmd + '\n')

    # now, we have written all the scripts with the single jobs.
    
    return len(jobStartImages), dirTxtOut, dirJobs


def output_job_listing(nFinishedJobs, nFailedJobs, nTotalJobs, runningJobs):
    shmFile = '/dev/shm/.qstat_file_{:03d}'.format(random.randint(0, 999))
    try:
        os.system('qstat -twu $USER > {}'.format(shmFile))
        f = open(shmFile, 'r')
        lines = f.readlines()
        f.close()
        if len(lines) > 0:
            while not lines[0].startswith('-'):
                del lines[0]
            del lines[0]
    finally:
        if os.path.isfile(shmFile):
            os.remove(shmFile)

    jobStates = {}
    for line in lines:
        line = line.strip()
        if len(line) > 0:
            fields = line.split()
            jobName = fields[0].split('.')[0]
            if jobName in runningJobs:
                assert len(fields) > 9
                jobState = fields[9]
                if jobState in jobStates:
                    jobStates[jobState] += 1
                else:
                    jobStates[jobState] = 1

    qjobs = 0
    rjobs = 0
    #ejobs = 0
    xjobs = 0
    #hjobs = 0
    sjobs = 0
    otherjobs = 0
    if 'Q' in jobStates:
        qjobs = jobStates['Q']
    if 'R' in jobStates:
        rjobs = jobStates['R']
    #if 'E' in jobStates:
    #    ejobs = jobStates['E']
    if 'X' in jobStates:
        xjobs = jobStates['X']
    #if 'H' in jobStates:
    #    hjobs = jobStates['H']
    if 'S' in jobStates:
        sjobs = jobStates['S']
    for k in jobStates.keys():
        if k not in 'QREXHS':
            otherjobs += jobStates[k]

    #if (qjobs == 0) and (rjobs == 0) and (hjobs == 0):
    #    wait = False

    if otherjobs > 0:
        print("R={}, Q={}, X={}, S={}, O={} | " \
              "done={}, fail={}, total={}".format(
                  rjobs, qjobs, xjobs, sjobs, otherjobs,
                  nFinishedJobs, nFailedJobs, nTotalJobs))
    else:
        print("R={}, Q={}, X={}, S={} | " \
              "done={}, fail={}, total={}".format(
                  rjobs, qjobs, xjobs, sjobs,
                  nFinishedJobs, nFailedJobs, nTotalJobs))

    sys.stdout.flush()


if __name__ == '__main__':

    exit_code = 0

    try:

        # parse arguments
        parser = argparse.ArgumentParser(
                    description='Start CellProfiler PBS jobs.')
        parser.add_argument('--version', dest='version', default='11047')
        parser.add_argument('--pipeline', dest='pipeline')
        parser.add_argument('--job-array', dest='job_array', default=None)
        parser.add_argument('--input-dir', dest='input_dir')
        parser.add_argument('--output-dir', dest='output_dir')
        parser.add_argument('--only-check', dest='only_check',
                            action='store_const', const=True, default=False)
        parser.add_argument('--force-start', dest='force_start',
                            action='store_const', const=True, default=False)
        parser.add_argument('--no-start', dest='no_start',
                            action='store_const', const=True, default=False)
        parser.add_argument('--single-runs', dest='single_runs',
                            action='store_const', const=True, default=False)
        parser.add_argument('--batch-size', dest='batch_size', type=int,
                            default=-1)
        parser.add_argument('--max-jobs', dest='max_jobs', type=int,
                            default=NUM_JOBS_MAX)
        parser.add_argument('--job-id-file', dest='job_id_file', default=None)
        parser.add_argument('--custom-script', dest='custom_script',
                            default=None)
        args = parser.parse_args()

    

        pipeline_file = args.pipeline
        jobArrayFile = args.job_array

        
        # create the jobs
        logDir, totalJobCount = prepare_jobs(CELLPROFILERBINARY, pipeline_file,
                                   delete=not args.only_check,
                                   num_jobs_max=args.max_jobs,
                                   single_runs=args.single_runs,
                                   custom_script=args.custom_script)

        # print some information about the jobs
        
        
        # run the jobs
        answer = raw_input('Do you want to start {} jobs? (y/n) ' .format(totalJobCount))
            if answer.lower() in ('y', 'yes'):
                start = True

            if start:
                print 'Spawning jobs...'
                jobName = run_jobs(totalJobCount, jobDir, logDir)
                
                #with open(runningJobIdFileName, 'a') as f:
                #    for jobNumber in xrange(1, totalJobCount + 1):
                #        runningJobs['{}[{}]'.format(jobName, jobNumber)] \
                #            = jobNumber
                #        f.write('+{}[{}]: {}\n'.format(
                #            jobName, jobNumber, jobNumber))
                print ''
                print ''
                print 'to see how many jobs you have running or pending use:'
                print ''
                print 'bjobs'
                print ''                    
                print 'for viewing your job stati and resubmitting failed jobs use below command;'
                print 'please report back to ALMF staff about failed jobs!'
                print ''
                print 'python-2.7 /g/almf/software/CP2C/checkjobs.py --logdir',logDir
                print ''
                
                                            
                else:
                    sys.exit(0)

        if False: #(start and not args.no_start) or args.only_check:
            # disable for the moment ... need to understand what's happening
             #print runningJobs

            allFinishedJobList = []
            allFailedJobList = []
            while len(allFinishedJobList) < totalJobCount:

                finishedJobList, failedJobList = check_for_jobs(logDir)
                allFinishedJobList.extend(finishedJobList)
                allFailedJobList.extend(failedJobList)
                #print 'finishedJobs: %d, failedJobs: %d' \
                    #% (len(finishedJobList), len(failedJobList))

                if len(failedJobList) > 0:
                    print '\nFailed jobs:', len(failedJobList)
                    # how to connect restarted jobs that failed again,
                    # to their job number
                    restartJobList = []
                    for failedJob in failedJobList:
                        jobName = failedJob
                        if jobName in runningJobs:
                            jobNumber = runningJobs[jobName]
                            assert jobNumber >= 0
                            restartJobList.append(jobNumber)
                    result = run_jobs(restartJobList, jobDir)
                    with open(runningJobIdFileName, 'a') as f:
                        for jobName, jobNumber in result:
                            runningJobs[jobName] = jobNumber
                            f.write('+{}: {}\n'.format(jobName, jobNumber))

                elif len(allFinishedJobList) < totalJobCount:
                    output_job_listing(len(allFinishedJobList),
                                       len(allFailedJobList),
                                       totalJobCount, runningJobs)
                    time.sleep(LOOP_WAIT_TIME)

                with open(runningJobIdFileName, 'a') as f:
                    # also iterate over failedJobList
                    for jobName in itertools.chain(finishedJobList,
                                                   failedJobList):
                        match = JOB_NAME_PATTERN.match(jobName)
                        jobName = match.group(1)
                        if jobName in runningJobs:
                            jobNumber = runningJobs[jobName]
                            assert jobNumber >= 0
                            del runningJobs[jobName]
                            f.write('-{}: {}\n'.format(jobName, jobNumber))

            sys.stdout.write('\n')
            sys.stdout.flush()

    except:
        import traceback
        traceback.print_exc()
        exit_code = -1

    finally:

        if JAVA_VM_RUNNING:
            try:
                import cellprofiler.utilities.jutil
                #print 'Trying to kill JAVA VM'
                cellprofiler.utilities.jutil.kill_vm()
            except:
                print "Softly killing the JAVA VM failed..." \
                      "Trying it hard now..."
                os.kill(os.getpid(), signal.SIGINT)
                raise

    sys.exit(exit_code)
