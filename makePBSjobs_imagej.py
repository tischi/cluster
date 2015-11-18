import sys
import os
import time
import shutil
import signal
import re
import random
import argparse
import itertools

NUM_JOBS_MAX = 500

JOB_FILE_PATTERN = 'job_{}.sh'
JOB_NAME_PATTERN = re.compile('(([0-9]+)(\[([0-9]+)\])?)(\..*)?')

#python2.7 /g/almf/software/scripts/cluster/makePBSjobs_imagej.py --prg-binary /g/almf/software/bin2/fiji --prg-plugins-dir=/g/almf/software/fiji_tischi/plugins --prg-script=/g/almf/software/scripts/imagej/tischi_gwen--stitch_edf_headless--2012_10_19.py --data-in-dir=/g/almf/group/ALMFstuff/Tischi/projects/GwendolynEich/data --data-out-dir=/g/almf/group/ALMFstuff/Tischi/projects/GwendolynEich/data--fiji-out
#python2.7 /g/almf/software/scripts/cluster/makePBSjobs_imagej_gwen2012.py --prg-binary /g/almf/software/bin2/fiji --prg-plugins-dir=/g/almf/software/fiji_tischi/plugins --prg-script=/g/almf/software/scripts/imagej/tischi_gwen--stitch_edf_headless--2012_10_19.py --data-in-dir=/g/almfscreen/Gwen/2012-08-14--tifs

def prepare_jobs(prg_binary, prg_plugins_dir, prg_script, data_in_dir, delete=True,
                 num_jobs_max=500):
                    
    # create output directories
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

    
    if data_in_dir is None:
        raise Exception("You need to specify an input directory!")
    else:
        output_dir = data_in_dir + '--cluster'

    print('Cluster output directory: {}'.format(output_dir))
    dirTxtOut = os.path.join(output_dir, "log")
    dirJobs = os.path.join(output_dir, "jobs")
    dirStatus = os.path.join(output_dir, "status")

    if delete:
        ensure_empty_dir(output_dir)
        ensure_empty_dir(dirStatus)
        ensure_empty_dir(dirTxtOut)
        ensure_empty_dir(dirJobs)


    def writeJobHeader(iJob):
        # header for the scripts of the individual jobs
        head = ["#!/bin/bash",
                "#PBS -q clng_new",
                "#PBS -o {}".format(dirTxtOut),
                "#PBS -e {}".format(dirTxtOut),
                "#PBS -l select=1:ncpus=1:mem=2gb",
                ""]
        head = '\n'.join(head)
        head = head + '\n'
        # write the jobs to files
        script_name = JOB_FILE_PATTERN.format(iJob + 1)
        script_name = os.path.join(dirJobs, script_name)
        script_file = file(script_name, "w")
        script_file.write(head)
        return script_file,script_name
  

    # Loop over batches, check status file, print out commands

    ######################################################
    ## THIS PART IS PROGRAMME AND PROJECT SPECIFIC: START
        
    ps = 1
    pe = 1
    ts = 11
    te = 12
    
    iJob = 0
    dt=2
    for p in range(ps,pe+1):
        for t in range(ts,te+1,dt):
        
            script_file,script_name = writeJobHeader(iJob)
            print script_name
            
            expname = "Experiment-28-"
            cmd = [
                prg_binary,
                "--headless",
                "-cp {}".format(prg_plugins_dir),
                "{}".format(prg_script),
                os.path.join(data_in_dir,expname+str(p)+".tif_files"),
                output_dir, 
                expname,
                "{}".format(p),
                "{}".format(p),
                "{}".format(t),
                "{}".format(t+dt-1),
                " "
            ]
            
            
            ## THIS PART IS PROGRAMME AND PROJECT SPECIFIC: END
            ######################################################
            
            cmd = ' '.join(cmd)

            script_file.write(cmd + '\n')
     
            # add this line to later check whether the job was finished
            script_file.write(
                'touch "{}/${{PBS_JOBID}}.touch"\n'.format(dirTxtOut)
            )
            script_file.write('\n')
            script_file.close()

            # make the script executable
            # (if not, the cluster node cannot call it)
            os.system('chmod a+x {}'.format(script_name))
            iJob += 1 	

        
    # now, we have written all the scripts with the single jobs.
    # now, an array script has to be written that calls them.

    array_script_name = os.path.join(dirJobs, "jobarray.sh")
    main_script_file = file(array_script_name, 'w')
    jobFile = JOB_FILE_PATTERN.format('$PBS_ARRAY_INDEX')
    main_content = [
        "#!/bin/bash",
        "#PBS -J 1-{}".format(iJob),
        "#PBS -q clng_new",
        "#PBS -o {}".format(dirTxtOut),
        "#PBS -e {}".format(dirTxtOut),
        "{}/{}".format(dirJobs, jobFile),
    ]
    main_content = '\n'.join(main_content)
    main_script_file.write(main_content)
    main_script_file.close()


if __name__ == '__main__':

    exit_code = 0

    if 1: #try:

        # parse arguments
        parser = argparse.ArgumentParser(
                    description='Create ImageJ PBS jobs.')
        parser.add_argument('--prg-binary', dest='prg_binary', default='/g/almf/software/bin2/fiji')
        parser.add_argument('--prg-plugins-dir', dest='prg_plugins_dir', default='/g/almf/software/fiji_tischi_plugins')
        parser.add_argument('--prg-script', dest='prg_script', default='')
        parser.add_argument('--data-in-dir', dest='data_in_dir')
        #parser.add_argument('--data-out-dir', dest='data_out_dir')
        parser.add_argument('--batch-size', dest='batch_size', type=int,
                            default=-1)
        parser.add_argument('--max-jobs', dest='max_jobs', type=int,
                            default=NUM_JOBS_MAX)
        parser.add_argument('--job-id-file', dest='job_id_file', default=None)
        args = parser.parse_args()

	## tell the user which programme and version is used
        #print("Using CellProfiler version 2.0.{}".format(args.version))

        ## prepare the jobs
        prepare_jobs(args.prg_binary, args.prg_plugins_dir, args.prg_script, args.data_in_dir, True, args.max_jobs)
    
    else: #except:    
        print "something went wrong!"    
        exit_code = -1
    
    sys.exit(exit_code)  