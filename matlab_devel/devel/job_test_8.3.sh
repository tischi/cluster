#!/bin/bash
#BSUB -oo "/g/almf/software/scripts/cluster/matlab/devel/job_1--out.txt"
#BSUB -eo "/g/almf/software/scripts/cluster/matlab/devel/job_1--err.txt"
#BSUB -M 8000
#BSUB -R select[mem>8000] -R rusage[mem=8000]

echo $LD_LIBRARY_PATH
echo ""

# matlab runtime libraries
MCRROOT=/g/software/linux/pack/matlab_runtime-8.3/bin/v83 
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/runtime/glnxa64
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/bin/glnxa64
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/sys/os/glnxa64
# LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/sys/opengl/lib/glnxa64
export LD_LIBRARY_PATH

XAPPLRESDIR=/g/software/linux/pack/matlab_runtime-8.3/bin/v83/X11/app-defaults
export XAPPLRESDIR

echo $LD_LIBRARY_PATH

echo "starting job"
touch "/g/almf/software/scripts/cluster/matlab/devel/job_test--started.touch"

# run the code
/scratch/Nils/LFdeconvolution/test1/main_reconstruct_single /scratch/Nils/20151029_6dpf_40x_095NA_air_100ms_LED23_pos20_lowOxygen_1__T0.tif /scratch/Nils/LFdeconvolution/test1/output /scratch/Nils/PSF_40x095NAair.mat 1269.7 1082.05 22.645 is_first_frame  1
