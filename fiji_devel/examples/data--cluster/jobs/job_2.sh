#!/bin/bash
#BSUB -oo "/g/almf/software/scripts/cluster/fiji_devel/examples/data--cluster/log/job_2--out.txt"
#BSUB -eo "/g/almf/software/scripts/cluster/fiji_devel/examples/data--cluster/log/job_2--err.txt"
#BSUB -M 16000
#BSUB -R select[mem>16000] -R rusage[mem=16000]
#BSUB -R span[hosts=1]
#BSUB -m fujitsu
echo "starting job"
touch "/g/almf/software/scripts/cluster/fiji_devel/examples/data--cluster/log/job_2--started.touch"
ulimit -c 0
echo "hostname:"
hostname
echo "number of cores:"
nproc
echo "total RAM:"
head -1 /proc/meminfo
xvfb-run -a /g/emcf/software/Fiji/Fiji.app/ImageJ-linux64 -batch "/g/almf/software/scripts/cluster/fiji_devel/examples/macro_1image.ijm" "/g/almf/software/scripts/cluster/fiji_devel/examples/data/im2.png"
echo "job finished"
