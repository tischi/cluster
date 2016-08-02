#!/bin/bash
#BSUB -oo "/g/almf/software/scripts/cluster/cellprofiler_devel/example-data--cluster/log/job_1--out.txt"
#BSUB -eo "/g/almf/software/scripts/cluster/cellprofiler_devel/example-data--cluster/log/job_1--err.txt"
#BSUB -M 16000
#BSUB -R select[mem>16000] -R rusage[mem=16000]
#BSUB -R span[hosts=1]
#BSUB -m fujitsu
echo "starting job"
touch "/g/almf/software/scripts/cluster/cellprofiler_devel/example-data--cluster/log/job_1--started.touch"
ulimit -c 0
echo "hostname:"
hostname
echo "number of cores:"
nproc
echo "total RAM:"
head -1 /proc/meminfo
CellProfiler-2.0.11047 -c -b -r -p /g/almf/software/scripts/cluster/cellprofiler_devel/Batch_data.mat -f 1 -l 4
echo "job finished"
