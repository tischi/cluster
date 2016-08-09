### Authors: Volker Hilsenstein and Christian Tischer (almf@embl.de)


import sys
from os import path
import thread
import os
import csv
import argparse

def find_csvs_in_folder(folder, pattern):
    print("")
    print("Searching files...")
    csvs = []
    count = 0
    #level = len(folder.split(os.sep)) - 1
    for root,dir,files in os.walk(folder):
        for f in files:
            tmp=path.join(root, f)
            #print(level)
            #print(tmp.split(os.sep))
            count += 1
            if f.endswith(pattern):
                csvs.append(tmp)
    print("total files scanned: " + str(count))
    print("found files: " + str(len(csvs)))       
    return csvs

def concatenate_files(indir,csvs,outputfile):
    #set progressbar limits
    #self.progress.setMinimum(0)
    #self.progress.setMaximum(len(self.csvs)-1)
    #self.progress.setValue(0)
    
    print("")
    print("Concatenating the files...")
        
    # open first file to get field names
    with open(csvs[0],"rb") as f:
        reader = csv.DictReader(f,delimiter=",",quotechar='"')
        fieldnames = reader.fieldnames

        # open outputfile for writing
        with open(outputfile, "wb") as of:
            i=0
            writer=csv.DictWriter(of, delimiter=",", quotechar='"', fieldnames=fieldnames)
            # write header
            writer.writerow(dict((fn,fn) for fn in fieldnames))
            # concatenate all images
            for fname in csvs:
                #print("Current file: " +fname)      
                with open(fname,"rb") as f:
                    reader = csv.DictReader(f,delimiter=",",quotechar='"')
                    for row in reader:
                        writer.writerow(row)
                        #self.progress.setValue(i)
                        i+=1            
    print("")
    print("Saving concatenated table as: "+ outputfile)         
            
def concatenate(indir, pattern):
  # find files
  if indir is not None:
    if path.exists(indir):
      csvs = find_csvs_in_folder(indir, pattern)
      if len(csvs)==0:
        print("No files found")
      else:	
        pattern_without_ending = pattern.split(".")[0]
        outfile = indir + os.sep + pattern_without_ending + "_concat.csv"
        concatenate_files(indir,csvs,outfile)
    else:
      print("Error: Does not exist: "+indir)     
        
def main():
	parser = argparse.ArgumentParser(description='Concatenate CellProfiler objects tables.')
	parser.add_argument('--tabledir', dest='tabledir', default='')
	parser.add_argument('--table_ending', dest='table_ending', default='')
	args = parser.parse_args()
	indir = args.tabledir
	pattern = args.table_ending
	print("")
	print("##########################################")
	print("Input directory: "+indir)
	print("Pattern in table files: "+pattern)
	concatenate(indir, pattern)
	print("##########################################")
	print("")
    

if __name__ == '__main__':
    main()