# Usage instructions for EMBL Heidelberg
- ssh onto submaster1
- type following command:
- python-2.7 /g/almf/software/scripts/cluster/cluster--fiji--20151118/make_jobs_LSF.py --xvfb "xvfb-run -a" --software "/g/emcf/software/Fiji/Fiji.app/ImageJ-linux64 -batch" --script __your_fiji_script__ --input_dir __your_folder_with_data__ 
- replacing __your_fiji_script__ and __your_folder_with_data__ by a script that is executable in Fiji and that can handle the files or sub-folders in your_folder_with_data 
