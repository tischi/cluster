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
 
NUM_JOBS_MAX = 100

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

 
def make_jobs(args):
    
    # how to make this nicer?
    xvfb = args.xvfb
    software = args.software
    script = args.script
    script_arguments = args.script_arguments
    memory = args.memory
    queue = args.queue
    host_group = args.host_group    
    num_jobs_max = 1000
    
    print ''
    print 'make_cellprofiler_jobs_LSF:'
    print ''
                

    #
    # determine files to analyze
    #
    
    CELLPROFILERDIR = '/g/software/linux/pack/cellprofiler-2.0.11047/lib'
    sys.path.insert(0, CELLPROFILERDIR)
    # try importing cellprofiler modules
    global cellprofiler
    import cellprofiler
    import cellprofiler.pipeline
    import cellprofiler.workspace
    import cellprofiler.measurements
    import cellprofiler.cpimage

    # LOAD PIPELINE
    pipeline_file = script
    if not os.path.isfile(pipeline_file):
        raise Exception("-- ERROR: pipeline file not found")

    cp_plugin_directory = None
    if 'CP_PLUGIN_DIRECTORY' in os.environ:
        cp_plugin_directory = os.environ['CP_PLUGIN_DIRECTORY']

    pipeline = cellprofiler.pipeline.Pipeline()

    def error_callback(event, caller):
        if (isinstance(event, cellprofiler.pipeline.LoadExceptionEvent) or
            isinstance(event, cellprofiler.pipeline.RunExceptionEvent)):
            sys.stdout.write("Handling exception: {}\n".format(event))
            sys.stdout.write(traceback.format_exc())
            sys.sydout.flush()
    pipeline.add_listener(error_callback)

    # pipeline.remove_listener(error_callback)

    # GET NUMBER OF IMAGES AND GROUPS

    # check wether we have a new or an old version of CellProfiler

    import inspect
    argspec = inspect.getargspec(pipeline.prepare_run)
    if argspec[0][1] == 'workspace' or len(argspec[0]) == 2:
        print 'New CellProfiler version'
        new_version = True
    else:
        print 'Old CellProfiler version'
        new_version = False

    if new_version:
        # this should work for plain pipeline files ...
        try:
            pipeline.load(pipeline_file)
            image_set_list = cellprofiler.cpimage.ImageSetList()
            measurements = cellprofiler.measurements.Measurements()
            workspace = cellprofiler.workspace.Workspace(
                pipeline, None, None, None,
                measurements, image_set_list
            )
            grouping_argument = workspace
            result = pipeline.prepare_run(workspace)
            grouping_keys, groups = pipeline.get_groupings(
                grouping_argument
            )
            pipeline.prepare_group(
                grouping_argument, groups[0][0], groups[0][1])
            num_sets = image_set_list.count()
        except:
            import traceback
            traceback.print_exc()
            raise Exception('Unable to load pipeline file:', pipeline_file)
            # ... and this should work for files created with
            # the CreateBatchFile module
            measurements = cellprofiler.measurements.load_measurements(
                pipeline_file
            )
            print 'Obtaining list of image sets...this can take a while...'
            image_set_list = measurements.get_image_numbers()
            grouping_keys = []
            num_sets = len(image_set_list)
    else:
        try:
            pipeline.load(pipeline_file)
        except:
            import traceback
            traceback.print_exc()
            raise Exception('Unable to load pipeline file:', pipeline_file)

        workspace = None
        grouping_argument = workspace

        print 'Obtaining list of image sets...this can take a while...'
        result = pipeline.prepare_run(workspace)
        if not result:
            raise Exception("Failed to prepare running the pipeline")

        if not new_version:
            grouping_argument = result
            image_set_list = result

        grouping_keys, groups = pipeline.get_groupings(grouping_argument)

        if new_version:
            pipeline.prepare_group(
                grouping_argument, groups[0][0], groups[0][1])

        num_sets = image_set_list.count()

    print("Image sets: {}".format(num_sets))
    if num_sets == 0:
        print 'No image sets to process...finished'
        sys.exit(0)

    # GET IMAGE PATH
    input_dir = None # could be also an directory with image files if one does not use Batch_data.mat....
    if input_dir is None:
        loadimage_module_name = 'LoadImages'
        cp_modules = pipeline.modules()
        loadimage_module = None
        for module in cp_modules:
            if module.module_name == loadimage_module_name:
                loadimage_module = module
                break
        if loadimage_module:
            input_dir = str(loadimage_module.location).partition('|')[2]
            print("Image path: {}".format(input_dir))
        else:
            print '-- WARNING: The LoadImage module is not used in this' \
                  ' pipeline. Default input folder is undefined'
            #print('-- ERROR: Could not load the image module!')
            #sys.exit(1)

    # CREATE BATCHES
    jobStartImages = []
    jobEndImages = []
    jobLengths = []

    if len(grouping_keys) > 0:
        print('Using groupings to assign the jobs to {} groups.'.format(
            len(groups)))
        for group in groups:
            #print 'group length',len(group[1])
            #print group[1][1]
            jobStartImages.append(group[1][0])
            jobEndImages.append(group[1][-1])
            jobLengths.append(len(group[1]))
        #batch_size_max = max(jobLengths)
        print 'Starting images:'
        print jobStartImages
    else:
        print "No groupings assigned => " \
              "images will be randomly assigned to the jobs."
        if int(args.batch_size) > 0:
            batch_size = int(args.batch_size)
        else:
            batch_size = max(4 , int(num_sets / float(num_jobs_max)) + 1)
        #batch_size = 4 #int(round(num_sets/num_jobs_max)+1)
        jobStartImages = range(1, num_sets + 1, batch_size)
        for x in jobStartImages:
            jobEndImages.append(x + batch_size - 1)
        jobEndImages[-1] = num_sets
        #batch_size_max = batch_size
    
    #
    # create directories
    #
    input_dir = input_dir.rstrip(os.path.sep) # remove trailing slash if exists
    output_dir = input_dir + '--cluster'
    print('Cluster directory: {}'.format(output_dir))
   
    log_dir = os.path.join(output_dir, "log")  # contains information about job status
    job_dir = os.path.join(output_dir, "jobs") # contains the actual job scripts

    # create directories
    ensure_empty_dir(output_dir)
    ensure_empty_dir(log_dir)
    ensure_empty_dir(job_dir)

    
    #
    # write the job files
    #
    
    for iJob in range(0, len(jobStartImages)):
        
        # chose image subset
        start = jobStartImages[iJob]
        end = jobEndImages[iJob]
        if end > num_sets:
            end = num_sets
   
        # write the jobs to files
        script_name = "job_{}.sh".format(iJob + 1)
        script_name = os.path.join(job_dir, script_name)
        script_file = file(script_name, "w")

        # information to LSF
        txt = ['#!/bin/bash',
                '#BSUB -oo "{}/job_{}--out.txt"'.format(log_dir,iJob+1),
                '#BSUB -eo "{}/job_{}--err.txt"'.format(log_dir,iJob+1),
                '#BSUB -M {}'.format(memory),
                '#BSUB -R select[mem>{}] -R rusage[mem={}]'.format(memory,memory),
                '#BSUB -R span[hosts=1]'
                ]
        txt = '\n'.join(txt)
        txt = txt + '\n'
        script_file.write(txt)


        if queue:
          script_file.write(
            '#BSUB -q {}\n'.format(queue)
          )        
          
        if host_group:
          script_file.write(
            '#BSUB -m {}\n'.format(host_group)
          )        

        
        script_file.write(
            'echo "starting job"\n'
        )        

        # write a file to be able to check from the outside that the job has started
        script_file.write(
            'touch "{}/job_{}--started.touch"\n'.format(log_dir,iJob+1)
        )

        # do not produce core dumps  
        script_file.write(
            'ulimit -c 0\n'
        )        
                
        txt = ['echo "hostname:"',
               'hostname',
               'echo "number of cores:"',
               'nproc',
               'echo "total RAM:"',
               'head -1 /proc/meminfo'
               ]
        txt = '\n'.join(txt)
        txt = txt + '\n'
        script_file.write(txt)

        # generate the actual command      
        def make_command(software, script, script_arguments):
            cmd = [
               software,
               "-c -b -r",
               "-p {}".format(script),
               script_arguments
            ]
            return ' '.join(cmd)

        script_arguments = "-f {} -l {}".format(start, end)
        
        # using software without quotation as it does not work with
        cmd = make_command(software, script, script_arguments)
        script_file.write(cmd + '\n')

        script_file.write(
            'echo "job finished"\n'
        )        
        
        # this is the last line in the script, because this will be displayed as the job name by LSF
        '''
        script_file.write(
            'echo "# job {}"\n'.format(iJob)
        )  
        '''
        script_file.close()
        
        # make script executable
        os.system('chmod a+x {}'.format(script_name))

    return job_dir, len(jobStartImages)



if __name__ == '__main__':

    ''' example calls:
    python-2.7 /g/almf/software/scripts/cluster/make_fiji_jobs_LSF.py --xvfb "xvfb-run -a" --software "/g/emcf/software/Fiji/Fiji.app/ImageJ-linux64 -batch" --script /g/arendt/PrImR/PrImR48/Scripts/LifExt_Split.ijm --input_dir /g/arendt/PrImR/PrImR48/0lif/
    python-2.7 /g/almf/software/scripts/cluster/make_fiji_jobs_LSF.py --xvfb "xvfb-run -a" --software "/g/emcf/software/Fiji/Fiji.app/ImageJ-linux64 -batch" --script /g/almf/group/ALMFstuff/Tischi/projects/LukasAnneser/CI_MIP_Macr.ijm --input_dir /g/almf/group/ALMFstuff/Tischi/projects/LukasAnneser/TEST
    '''

    description = '''
    Prepares LSF jobs for running Fiji scripts on each file (or folder) in the input_dir. 
    For each job one file will be stored in an automatically generated folder, 
    which will have the name of your --input_dir + "--cluster/jobs". It is very instructive to inspect the job files, which are simple text, e.g. to determine sources of errors.
    Once job generation is finished this script will print a command to run the jobs (using run_jobs_LSF.py);
    you may simply copy and paste this command and press enter to execute it.
    '''
    
    # parse arguments
    
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--software', dest='software', default='CellProfiler-2.0.11047',
                        help='(required) full path to your fiji installation, including options for running it.')
    parser.add_argument('--input_dir', dest='input_dir', default='',
                        help='(required) full path to the folder containing the data to be analyzed.')
    parser.add_argument('--script', dest='script', default='',
                        help='(required) full path to the fiji script that you want to run.')
    parser.add_argument('--script_arguments', dest='script_arguments', default='',
                        help='arguments/options that your script takes (in addition to the file/folder to be analyzed, which will be determined from the --input_dir for each job automatically.)')
    parser.add_argument('--xvfb', dest='xvfb', default='"xvfb-run -a"', 
                        help='specify software providing a virtual frame buffer; this is necessary to handle possible graphics output of fiji.')            
    #parser.add_argument('--output_dir', dest='output_dir', default='')
    parser.add_argument('--memory', dest='memory', default='16000',
                        help='memory that you want to allocate on the cluster node in MB.')
    #parser.add_argument('--batch_size', dest='batch_size', type=int, default=-1)
    #parser.add_argument('--max_jobs', dest='max_jobs', type=int,
    #                    default=NUM_JOBS_MAX)
    parser.add_argument('--queue', dest='queue', default='',
                        help='select a specific queue to submit your jobs to; this selects a subset of the available nodes with specific properties, e.g. "bigmem" selects nodes with a lot of memory.') # bigmem
    parser.add_argument('--host_group', dest='host_group', default='fujitsu',
                           help='select a specific group of nodes to submit your jobs to.') 
    parser.add_argument('--batch_size', dest='batch_size', default='0',
                           help='number of image sets per job.') 

    args = parser.parse_args()
   
    # create the jobs
    #job_dir, nJobs = make_jobs(args.xvfb, args.software, args.script, args.input_dir, args.output_dir, args.batch_size, args.max_jobs, args.memory, args.queue, args.host_group)
    job_dir, nJobs = make_jobs(args)
    
    # print some information about the jobs
    print ''
    print 'Number of jobs:',nJobs
    print 'Job directory:',job_dir
    print ''
    print 'Command to spawn jobs on cluster:'
    print 'python-2.7 /g/almf/software/scripts/cluster/run_jobs_LSF.py --job_dir',job_dir
    print ''


    # below is necessary to finish the script

    try:
        import cellprofiler.utilities.jutil
        #print 'Trying to kill JAVA VM'
        cellprofiler.utilities.jutil.kill_vm()
    except:
        os.kill(os.getpid(), signal.SIGINT)
       