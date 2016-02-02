require(tcltk)
pathname = tk_choose.dir(default = "", caption = "Select folder")
filename_imageTable_python = "images_concat.csv"
filename_objectTable_python = "objects_concat.csv"
cmd = paste("python-2.7 '/g/almf/software/scripts/cluster/hepp_import_cp2.py' ", pathname," '()(.*)(\\.csv)' "," 'image' "," 'objects' '",pathname,"/",filename_imageTable_python,"' '",pathname,"/",filename_objectTable_python,"'", sep="")
print(cmd); 
system(cmd);
