#!/bin/bash

# add wxWidgets to LD_LIBRARY_PATH
WXDIR=/g/software/linux/pack/wxPython-2.8.12.0
WXLD_LIBRARY_PATH=$WXDIR/wxWidgets/lib
export LD_LIBRARY_PATH="${WXLD_LIBRARY_PATH}:${LD_LIBRARY_PATH}"
# add wxPython to PYTHONPATH
WXPYTHONPATH=$WXDIR/lib/python2.7/site-packages/wx-2.8-gtk2-unicode:$WXDIR/lib/python2.7/site-packages
export PYTHONPATH="${WXPYTHONPATH}:${PYTHONPATH}"

#export PYTHONPATH=${CELLPROFILERDIR}:${PYTHONPATH}

export PATH=/g/software/linux/pack/jdk-6u18/bin:$PATH

python-2.7 /g/almf/software/scripts/cluster/make_cellprofiler_jobs_LSF.py $@

