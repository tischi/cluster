CellProfiler Pipeline: http://www.cellprofiler.org
Version:1
SVNRevision:11047

LoadImages:[module_num:1|svn_version:\'11031\'|variable_revision_number:11|show_window:False|notes:\x5B\x5D]
    File type to be loaded:individual images
    File selection method:Text-Exact match
    Number of images in each group?:3
    Type the text that the excluded images have in common:Do not use
    Analyze all subfolders within the selected folder?:None
    Input image file location:Elsewhere...\x7C/g/almf/software/scripts/cluster/cellprofiler_devel/example-data
    Check image sets for missing or duplicate files?:Yes
    Group images by metadata?:No
    Exclude certain files?:No
    Specify metadata fields to group by:
    Select subfolders to analyze:
    Image count:1
    Text that these images have in common (case-sensitive):.tif
    Position of this image in each group:1
    Extract metadata from where?:None
    Regular expression that finds metadata in the file name:^(?P<Plate>.*)_(?P<Well>\x5BA-P\x5D\x5B0-9\x5D{2})_s(?P<Site>\x5B0-9\x5D)
    Type the regular expression that finds metadata in the subfolder path:.*\x5B\\\\/\x5D(?P<Date>.*)\x5B\\\\/\x5D(?P<Run>.*)$
    Channel count:1
    Group the movie frames?:No
    Grouping method:Interleaved
    Number of channels per group:3
    Load the input as images or objects?:Images
    Name this loaded image:tubulin
    Name this loaded object:Nuclei
    Retain outlines of loaded objects?:No
    Name the outline image:LoadedImageOutlines
    Channel number:1
    Rescale intensities?:Yes

Smooth:[module_num:2|svn_version:\'11025\'|variable_revision_number:1|show_window:True|notes:\x5B\x5D]
    Select the input image:tubulin
    Name the output image:FilteredImage
    Select smoothing method:Gaussian Filter
    Calculate artifact diameter automatically?:No
    Typical artifact diameter, in  pixels:30
    Edge intensity difference:0.1

RescaleIntensity:[module_num:3|svn_version:\'6746\'|variable_revision_number:2|show_window:True|notes:\x5B\x5D]
    Select the input image:FilteredImage
    Name the output image:RescaledBlue
    Select rescaling method:Stretch each image to use the full intensity range
    How do you want to calculate the minimum intensity?:Custom
    How do you want to calculate the maximum intensity?:Custom
    Enter the lower limit for the intensity range for the input image:0
    Enter the upper limit for the intensity range for the input image:1
    Enter the intensity range for the input image:0.000000,1.000000
    Enter the desired intensity range for the final, rescaled image:0.000000,1.000000
    Select method for rescaling pixels below the lower limit:Mask pixels
    Enter custom value for pixels below lower limit:0
    Select method for rescaling pixels above the upper limit:Mask pixels
    Enter custom value for pixels below upper limit:0
    Select image to match in maximum intensity:None
    Enter the divisor:1
    Select the measurement to use as a divisor:None

SaveImages:[module_num:4|svn_version:\'11042\'|variable_revision_number:7|show_window:True|notes:\x5B\x5D]
    Select the type of image to save:Image
    Select the image to save:RescaledBlue
    Select the objects to save:None
    Select the module display window to save:None
    Select method for constructing file names:From image filename
    Select image name for file prefix:tubulin
    Enter single file name:OrigBlue
    Do you want to add a suffix to the image file name?:No
    Text to append to the image name:
    Select file format to use:jpeg
    Output file location:Same folder as image\x7CNone
    Image bit depth:8
    Overwrite existing files without warning?:Yes
    Select how often to save:Every cycle
    Rescale the images? :Yes
    Save as grayscale or color image?:Grayscale
    Select colormap:gray
    Store file and path information to the saved image?:No
    Create subfolders in the output folder?:No

CreateBatchFiles:[module_num:5|svn_version:\'11025\'|variable_revision_number:4|show_window:False|notes:\x5B\x5D]
    Store batch files in default output folder?:No
    Output folder path:/g/almf/software/scripts/cluster/cellprofiler_devel
    Are the cluster computers running Windows?:No
    Hidden\x3A in batch mode:No
    Hidden\x3A default input folder at time of save:/home/tischer
    Hidden\x3A SVN revision number:0
    Local root path:/home/tischer
    Cluster root path:/home/tischer
