#!/bin/bash
#BSUB -oo "/g/almf/software/scripts/cluster/cluster--fiji--20151118/examples/data--cluster/log/job_5--out.txt"
#BSUB -eo "/g/almf/software/scripts/cluster/cluster--fiji--20151118/examples/data--cluster/log/job_5--err.txt"
#BSUB -M 8000
#BSUB -R select[mem>8000] -R rusage[mem=8000]
echo "starting job"
touch "/g/almf/software/scripts/cluster/cluster--fiji--20151118/examples/data--cluster/log/job_5--started.touch"
ulimit -c 0
echo "hostname:"
hostname
echo "number of cores:"
nproc
echo "total RAM:"
head -1 /proc/meminfo
xvfb-run -a "/g/emcf/software/Fiji/Fiji.app/ImageJ-linux64 -batch" "/g/almf/software/scripts/cluster/cluster--fiji--20151118/test--cluster/macro_with_arguments.ijm" "arg1 arg2 /g/almf/software/scripts/cluster/cluster--fiji--20151118/examples/data/macro_2arguments_1image.ijm"
echo "job finished"
