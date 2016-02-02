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


def run_jobs(job_dir, bsub_options):
  
  jobfiles = os.listdir(job_dir)
    
  for jobfile in jobfiles:
    job_path = os.path.join(job_dir,jobfile)
    cmd = 'bsub {} < "{}"'.format(bsub_options,job_path)
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
        parser.add_argument('--bsub_options', dest='bsub_options', default='') # this is not good as it cannot be known by the resubmission script! better put as #BSUB in the job.sh scripts

        args = parser.parse_args()
         
        job_dir = args.job_dir.rstrip(os.path.sep) # remove trailing slash if exists
    
        
        print 'Spawning jobs...'
        run_jobs(job_dir, args.bsub_options)
        
        log_dir = os.path.join(os.path.split(job_dir)[0],"log")
		
        print ''
        print 'Command to check and resubmit failed jobs:'
        print 'python-2.7 /g/almf/software/scripts/cluster/cluster--fiji--20151118/check_jobs_LSF.py --log_dir',log_dir
        print ''
        
                               
    except:
        import traceback
        traceback.print_exc()
        exit_code = -1

    finally:
        print ""
        
    sys.exit(exit_code)
