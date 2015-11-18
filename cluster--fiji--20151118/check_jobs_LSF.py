import sys
import os
import argparse
import re


def resumbitJob(logdir,jobdir,job):
  
  jobfile = job +".sh"
  jobpath = os.path.join(jobdir,jobfile)
  
  if not os.path.isfile(jobpath):
    print "Error: did not find: "+jobpath
    return 0

  jobStartPath = os.path.join(logdir,job+"--started.touch")                        
  jobOutPath = os.path.join(logdir,job+"--out.txt")
  jobErrPath = os.path.join(logdir,job+"--err.txt")

  # remove job output files
  if os.path.isfile(jobStartPath):  
    cmd = "rm "+jobStartPath                        
    os.system(cmd)
  
  if os.path.isfile(jobOutPath):  
    cmd = "rm "+jobOutPath                        
    os.system(cmd)
                             
  if os.path.isfile(jobErrPath):  
    cmd = "rm "+jobErrPath                        
    os.system(cmd)
                     
  # resubmit job 
  cmd = "bsub < "+jobpath
  #print cmd
  os.system(cmd)
                        


if __name__ == '__main__':

    exit_code = 0

    try:

        # parse arguments
        parser = argparse.ArgumentParser(
                    description='Check LSF jobs.')
        parser.add_argument('--log_dir', dest='logdir', default=None)
        args = parser.parse_args()

        # get directories
        logdir = args.logdir.rstrip('/')
        jobdir = logdir.rpartition("/")[0]+"/jobs"
        
        if logdir==None:
            raise Exception("--log_dir parameter must be specified.")
        if not os.path.isdir(logdir):
            raise Exception("The chosen directory does not exist.")
        
        files = os.listdir(jobdir)
        totalNumberOfJobs = len(files)
        
        files = os.listdir(logdir)
        d = {'started':[], 'not_started':[], 'out_file_incomplete_start':[], 'out_file_incomplete_end':[],  'jvm_dir_not_found':[], 'output':[], 'toucherror':[], 'libjvm_not_found':[], 'libjvm_found':[], 'libjvmerror':[], 'successful':[], 'caterror': [], 'failed':[], 'withError':[], 'unfinished':[], 'jobnumbers':[]}
               
        for f in files:
            if ("--started" in f) or ("--err.txt" in f):
                job = f.split("--")[0]
                jobnum = int(job.split("_")[1])
                info = f.split("--")[1]
                info = info.split(".")[0] 
                if not job in d['started']: # add to list of started jobs
                  d['started'].append(job)
                if not jobnum in d['jobnumbers']: # add to list of all jobs
                  d['jobnumbers'].append(jobnum)
        
        for i in range(1, totalNumberOfJobs+1):   
          if not i in d['jobnumbers']:
            d['not_started'].append("job_"+str(i))
        
        for job in d['started']:  # todo: replace by looping from min to max: this allows for finding "not started"
  
            # print ""
             
            # generate output filename for the started job
            jobOutPath = os.path.join(logdir,job+"--out.txt")
            jobErrPath = os.path.join(logdir,job+"--err.txt")
                       
            
            if os.path.isfile(jobOutPath):  # if this file exists it means the job finished somehow
                # print job,"has produced an output file (finished)."                        
                            
                d['output'].append(job) # list of finished jobs
                outFileContent = file(jobOutPath,"r").read()

                
                # THIS PART IS SPECIFIC TO THE CODE THAT YOU RUN **************************
                
                # getting some information about the job:
                
                p = re.compile("Subject: Job (.*): <#!")
                if p.search(outFileContent):
                    jobNum = p.search(outFileContent).group(1)   
                    #print job,"Jobnum:",jobNum                        
                        
                p = re.compile("admin@(.*)>")
                if p.search(outFileContent):
                    jobNode = p.search(outFileContent).group(1)
                    #print job,"Node:",jobNode
                
                    
                # checking for potential things that could have gone wrong:
                
                if "ALMF: jvm_dir not found auto" in outFileContent:
                    #print job,"jvm_dir not found"
                    d['jvm_dir_not_found'].append(job)
                
                if "ALMF: java NOT found" in outFileContent:
                    #print job,"libjvm.so NOT found"
                    d['libjvm_not_found'].append(job)

                if "ALMF: java found" in outFileContent:
                    #print job,"libjvm.so was found"
                    d['libjvm_found'].append(job)
                
                if "load_using_PIL" in outFileContent:
                    #print job,"used PIL instead of Bioformats"
                    d['PIL'].append(job)
                    if not job in d['failed']:
                      d['failed'].append(job)
                  
                if len(file(jobOutPath,"r").readlines()) < 7:
                    # print job, "has empty output file"
                    if not job in d['failed']:                    
                      d['failed'].append(job)
                    
                p = re.compile("\njob finished")
                if not p.search(outFileContent):
                    # ...
                    if not job in d['failed']:                    
                      d['failed'].append(job)
                    d['out_file_incomplete_end'].append(job)                
                    
                    
                # do some more diagnostics
                if os.path.isfile(jobErrPath):
                    if len(file(jobErrPath,"r").readlines())>0:
                        d['withError'].append(job)
                        errFileContent = file(jobErrPath,"r").read()
                        if "libjvm.so" in errFileContent:
                            # print job,"has libjvm error"
                            d['libjvmerror'].append(job)
                        elif "at: write error:" in errFileContent:
                            # print job,"has cat error"
                            d['caterror'].append([job,jobNum,jobNode])
                        elif "cannot touch" in errFileContent:
                            # print job,"has touch error"
                            d['toucherror'].append([job,jobNum,jobNode])
                        else:
                            a = 1
                            # print job,"has unkown error message"
                    else:
                        a = 1
                        # print job,"has empty error file"
                else: 
                    a = 1
                    # print job,"error file not found!"
            
            # HERE, THE SPECIFIC PART ENDS *********************************** 
                        
            else:
                # print job,"started but no output file yet (unfinished)"
                d['unfinished'].append(job)
            
            

        print ""
        print "##################################################"
        print ""
        print "total:       "+str(totalNumberOfJobs)
        print "started:     "+str(len(d['started']))         
        print "finished:    "+str(len(d['output']))
        print "unfinshed:   "+str(len(d['unfinished']))
        print "not started: "+str(len(d['not_started'])) 
        print "failed:      "+str(len(d['failed'])) 
        print ""
        print "errors and warnings (please report to ALMF staff if non-zero):"  
        print "  failed: "+str(len(d['failed'])) 
        print "  have content in error file: "+str(len(d['withError']))
        #print "    cat error:      "+str(len(d['caterror'])) 
        #print "    touch error:    "+str(len(d['toucherror'])) 
        #print "    libjvm-warning: "+str(len(d['libjvmerror'])) 
        #print "  libjvm not found warning: "+str(len(d['libjvm_not_found'])) 
        #print "  jvm_dir not found warning: "+str(len(d['jvm_dir_not_found'])) 
        #print "  using PIL instead of Bioformats: "+str(len(d['PIL'])) 
        #print "  out_file_incomplete_start: "+str(len(d['out_file_incomplete_start'])) 
        print "  out_file_incomplete_end: "+str(len(d['out_file_incomplete_end'])) 
        
                         
        #if len(d['libjvm_not_found'])>0:
        #    print '\nlibjvm.so not found:'
        #    print d['libjvm_not_found']
           
        #if len(d['jvm_dir_not_found'])>0:
            #print '\njvm_dir not found:'
            #for job in d['jvm_dir_not_found']:
            #    print job       
        
        #if len(d['caterror'])>0:
            #print '\ncat-error jobs:\n'
            #for job in d['caterror']:
            #    print job
                
        #if len(d['out_file_incomplete_start'])>0:
            #print '\noout_file_incomplete_start jobs:\n'
            #for job in d['out_file_incomplete_start']:
            #    print job
                
        #if len(d['out_file_incomplete_end'])>0:
            #print '\nout_file_incomplete_end jobs:\n'
            #for job in d['out_file_incomplete_end']:
            #    print job
                
        if len(d['failed'])>0:
            print '\nfailed jobs:'
            #for job in d['failed']:
            #    print job            
            print d['failed']
            answer = raw_input('\nResubmit failed jobs (YES)? (y/n) ')
            print ""
            if answer.lower() in ('y', 'yes'):
                for job in d['failed']:
                  resumbitJob(logdir,jobdir,job)
                                                                                  
        #if len(d['PIL'])>0:
        #    answer = raw_input('\nResubmit jobs using PIL (Recommended)? (y/n) ')
        #    print ""
        #    if answer.lower() in ('y', 'yes'):
        #        for job in d['PIL']:
        #            resumbitJob(logdir,jobdir,job)
        
        if len(d['unfinished'])>0:
            answer = raw_input('\nResubmit unfinished jobs (please ONLY if STUCK for LONG time)? (y/n) ')
            print ""
            if answer.lower() in ('y', 'yes'):
                for job in d['unfinished']:
                    resumbitJob(logdir,jobdir,job)
      
        if len(d['not_started'])>0:
            print '\nNot started jobs:'
            #for job in d['failed']:
            #    print job            
            print d['not_started']
            answer = raw_input('(Re)submit not started jobs (please ONLY if NOT STARTED for LONG time)? (y/n) ')
            print ""
            if answer.lower() in ('y', 'yes'):
                for job in d['not_started']:
                  resumbitJob(logdir,jobdir,job)
        
                    
        sys.stdout.flush()
       
        
        
    except:
        import traceback
        traceback.print_exc()
        exit_code = -1

    sys.exit(exit_code)
