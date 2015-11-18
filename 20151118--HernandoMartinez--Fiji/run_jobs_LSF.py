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
NUM_JOBS_MAX = 1000
WAIT_BETWEEN_JOB_SUBMISSIONS = 0.1 # seconds

JOB_NAME_PATTERN = re.compile('.*<(?P<jobnr>)>.*')


def run_jobs(job_dir):
  
  jobfiles = os.listdir(job_dir)
    
  for jobfile in jobfiles:
    job_path = os.path.join(job_dir,jobfile)
    cmd = 'bsub < "{}"'.format(job_path)
    time.sleep(WAIT_BETWEEN_JOB_SUBMISSIONS)
    os.system(cmd)
  
  return 0
    

if __name__ == '__main__':

    exit_code = 0

    try:

        # parse arguments
        parser = argparse.ArgumentParser(
                    description='Running all LSF jobs in one directory.')
        parser.add_argument('--job_dir', dest='job_dir', default='')
        args = parser.parse_args()

        if args.job_dir[-1] == os.path.sep:  # remove trailing slash if exists
          job_dir = args.job_dir[:-1] 
        else:
          job_dir = args.job_dir
          
        print 'Spawning jobs...'
        run_jobs(job_dir)
        
        log_dir = os.path.join(os.path.split(job_dir)[0],"log")
		
        print ''
        print ''
        print 'to see how many jobs you have running or pending use:'
        print ''
        print 'bjobs'
        print ''                    
        print 'for viewing your job stati and resubmitting failed jobs use below command;'
        print 'please report back to ALMF staff about failed jobs!'
        print ''
        print 'python-2.7 /g/almf/software/CP2C/checkjobs.py --log_dir',log_dir
        print ''
        
                               
    except:
        import traceback
        traceback.print_exc()
        exit_code = -1

    finally:
        print ""
        
    sys.exit(exit_code)
