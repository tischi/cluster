#!/bin/bash
#BSUB -oo "test--cluster/log/job_2--out.txt"
#BSUB -eo "test--cluster/log/job_2--err.txt"
#BSUB -M 16000
#BSUB -R select[mem>16000] -R rusage[mem=16000]
ulimit -c 0
The job started.echo "hostname:"
hostname
echo "number of cores:"
nproc
echo "total RAM:"
touch "test--cluster/log/job_2--started.touch"
xvfbfiji script some_file
