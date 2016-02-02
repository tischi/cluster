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

# python2.7 /g/almf/software/scripts/cluster/runPBSjobs.py --job-array=/g/almfscreen/Gwen/2012-08-14--tifs--cluster/jobs/jobarray.sh
# python2.7 /g/almf/software/scripts/cluster/runPBSjobs.py --cluster-dir=/g/almfscreen/Gwen/2012-08-14--tifs--clust_manage
# python2.7 /g/almf/software/scripts/cluster/runPBSjobs.py --cluster-dir=/g/almfscreen/Gwen/2012-08-16--tifs--clust_manage

JAVA_VM_RUNNING = False
LOOP_WAIT_TIME = 60
NUM_JOBS_MAX = 500
JOB_FILE_PATTERN = 'job_{}.sh'

JOB_NAME_PATTERN = re.compile('(([0-9]+)(\[([0-9]+)\])?)(\..*)?')


def run_job_array(jobArrayFile):
    jobId = subprocess.check_output(
        ["qsub", "-q", "clng_new", jobArrayFile]).strip()
    print 'jobId:', jobId
    match = JOB_NAME_PATTERN.match(jobId)
    jobName = match.group(1)
    print 'Started job array:', jobName
    return jobName


def run_jobs(jobList, jobDir):
    result = []
    for jobNumber in jobList:
        script_name = JOB_FILE_PATTERN.format(jobNumber)
        script_name = os.path.join(jobDir, script_name)
        script_name = os.path.abspath(script_name)
        #print 'Restarting job %d: %s' % (jobId, script_name)
        jobId = subprocess.check_output(
            ["qsub", "-q", "clng_new", script_name]).strip()
        match = JOB_NAME_PATTERN.match(jobId)
        jobName = match.group(1)
        print('Restarted job #{}: {}'.format(jobNumber, jobName))
        result.append((jobName, jobNumber))
    return result


def check_for_jobs(logDir):
    #outjobname_pattern = '(([0-9]+)\[([0-9]+)\]\..+)\.OU'
    #outjobname_pattern = '((([0-9]+)(\[[0-9]+\])?)\..+)\.OU'
    #coutjobname_pattern = re.compile(outjobname_pattern)
    #errjobname_pattern = '(([0-9]+)\[([0-9]+)\]\..+)\.ER'
    errjobname_pattern = '((([0-9]+)(\[[0-9]+\])?)\..+)\.ER'
    cerrjobname_pattern = re.compile(errjobname_pattern)
    error_pattern = '.+/var/spool/PBS/mom_priv/jobs/.+\.SC'
    cerror_pattern = re.compile(error_pattern)

    def list_log_files(path):
        error_l = []
        output_l = []
        for entry in os.listdir(path):
            if entry.endswith('.ER'):
                error_l.append(entry)
            elif entry.endswith('.OU'):
                output_l.append(entry)
        return output_l, error_l

    outputFiles, errorFiles = list_log_files(logDir)
    finishedJobList = []
    failedJobList = []
    for errorFile in errorFiles:
        mo = cerrjobname_pattern.match(errorFile)
        if mo is None:
            raise Exception('Unable to extract job ID from error filename:',
                            errorFile)
        fullJobName = mo.group(1)
        jobName = mo.group(2)
        if jobName in runningJobs:
            f = open(os.path.join(logDir, errorFile), 'r')
            content = f.read()
            f.close()
            if cerror_pattern.match(content) is not None:
                failedJobList.append(jobName)
            else:
                touch_filename = os.path.join(
                    logDir, '{}.touch'.format(fullJobName)
                )
                if not os.path.isfile(touch_filename):
                    failedJobList.append(jobName)
                else:
                    finishedJobList.append(jobName)
    #for outputFile in outputFiles:
        #mo = coutjobname_pattern.match(outputFile)
        #if mo is None:
            #raise Exception(
                #'Unable to extract job ID from output filename: {}'.format(
                    #outputFile))
        #else:
            ##jobName = mo.group(3)
            ##if mo.group(3) in runningJobs:
            #finishedJobList.append(mo.group(2))
    return finishedJobList, failedJobList


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
                    description='Start PBS jobs.')
                    
        parser.add_argument('--cluster-dir', dest='cluster_dir', default=None)
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
        parser.add_argument('--job-id-file', dest='job_id_file', default=None)
        parser.add_argument('--custom-script', dest='custom_script',
                            default=None)
        args = parser.parse_args()


        if args.cluster_dir is not None:
            logDir = os.path.join(args.cluster_dir,"log")
            jobDir = os.path.join(args.cluster_dir,"jobs")
            jobArrayFile = os.path.join(jobDir,"jobarray.sh")
            runningJobIdFileName = jobArrayFile + '.jobids'
            
            totalJobCount = 0
            for fname in os.listdir(jobDir):
                if fname.startswith("job_"):
                    totalJobCount = totalJobCount + 1
        
        #jobArrayFile = args.job_array

        runningJobs = {}
        #runningJobIdFileName = args.job_id_file
        
        if 0: # and (args.only_check or jobArrayFile is not None:
            if runningJobIdFileName is None:
                raise Exception("You need to specify a file " \
                                "containing the running job ids.")
            with open(runningJobIdFileName, 'r') as f:
                lines = f.readlines()
                logDir, jobDir = [line.strip() for line in lines[:2]]
                totalJobCount = int(lines[2].strip())
                lines = lines[3:]
                for line in lines:
                    line = line.strip()
                    if line.startswith('+'):
                        jobName, jobNumber = line[1:].split(': ')
                        runningJobs[jobName] = jobNumber
                    elif line.startswith('-'):
                        jobName, jobNumber = line[1:].split(': ')
                        if jobName in runningJobs:
                            assert jobNumber == runningJobs[jobName]
                            del runningJobs[jobName]
            print('Checking for a total of {} jobs'.format(totalJobCount))

        start = False

        if 1: #not args.only_check or jobArrayFile is not None:

            #import wx

            #if jobArrayFile is None:
            #    application = wx.PySimpleApp()
            #    print 'Select jobarray via dialog.'
            #    dialog = wx.FileDialog(None, style=wx.OPEN)
            #    if dialog.ShowModal() == wx.ID_OK:
            #        jobArrayFile = dialog.GetPath()
            #    else:
            #        print 'No jobarray selected'
            #        sys.exit(1)
            #    dialog.Destroy()

      
            with open(runningJobIdFileName, 'w') as f:
                f.write('{}\n{}\n{}\n'.format(logDir, jobDir, totalJobCount))

            if not args.no_start:
                if args.force_start:
                    start = True
                else:
                    answer = raw_input('Do you want to start {} jobs (y/n)? ' \
                                       .format(totalJobCount))
                    if answer.lower() in ('y', 'yes'):
                        start = True

                if start:
                    print 'Spawning jobs...'
                    jobName = run_job_array(jobArrayFile)
                    with open(runningJobIdFileName, 'a') as f:
                        for jobNumber in xrange(1, totalJobCount + 1):
                            runningJobs['{}[{}]'.format(jobName, jobNumber)] \
                                = jobNumber
                            f.write('+{}[{}]: {}\n'.format(
                                jobName, jobNumber, jobNumber))
                else:
                    sys.exit(0)

        if (start and not args.no_start) or args.only_check:

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
        pass
        
    sys.exit(exit_code)
