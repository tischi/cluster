# -*- coding: utf-8 -*-

"""
import_cp2_csv.py -- Importer for CellProfiler 2.0 CSV files.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
# 
# Copyright 2011 Benjamin Hepp

import csv
import re
import numpy
import sys
import os
import traceback

OBJ_IMAGE_ID_IDENTIFIER = 'Image_ImageNumber'
IMG_IMAGE_ID_IDENTIFIER = 'Image_ImageNumber'

def fill_data(data, working_dict, image_data, object_data):

    # update feature-tables
    #update_pdc(pdc, image_data, object_data)

    # fill yaca_data_structure

    images, image_column_names = image_data

    o0, ocn = object_data[0]
    if len(data['objects']) == 0:
        for k in xrange(len(object_data)):
            data['objects'].append([])

    old_num_of_images = len(data['images'])

    if 'img_image_id_index' not in working_dict:
        try:
            i = image_column_names.index(IMG_IMAGE_ID_IDENTIFIER)
        except:
            i = -1
            image_column_names.insert(0, IMG_IMAGE_ID_IDENTIFIER)
        working_dict['img_image_id_index'] = i

    if 'obj_image_id_index' not in working_dict:
        try:
            i = ocn.index(OBJ_IMAGE_ID_IDENTIFIER)
        except:
            i = -1
            ocn.insert(0, OBJ_IMAGE_ID_IDENTIFIER)
        working_dict['obj_image_id_index'] = i

    if data['image_header'] is None:
        data['image_header'] = image_column_names

    if data['object_header'] is None:
        data['object_header'] = ocn

    last_image_id = old_num_of_images + len(images)

    for i in xrange(len(images)):

        row = images[i]
        if working_dict['img_image_id_index'] < 0:
            row.insert(0, str(old_num_of_images + 1))
        else:
            row[working_dict['img_image_id_index']] = str(int(row[working_dict['img_image_id_index']]) + old_num_of_images)
            last_image_id = row[working_dict['img_image_id_index']]

    data['images'].extend(images)

    for i in xrange(len(o0)):

        row = o0[i]

        found_img_id = False

        n = 0
        for k in xrange(len(object_data)):

            o, ocn = object_data[k]

            try:
                #TODO: It seems that the CellProfiler output changed with revision 11429
                #image_id = image_id_extrac tor( o[i], ocn ) + old_num_of_images
                # assume a single image per tuple of input files
                image_id = -1
                obj_image_id = last_image_id
                found_img_id = True
            except:
                pass

        if working_dict['obj_image_id_index'] < 0:
            row.insert(0, str(obj_image_id))
        else:
            row[working_dict['obj_image_id_index']] = obj_image_id

    for k in xrange(len(object_data)):
        data['objects'][k].extend(object_data[k][0])



def import_cp2_csv_results_recursive(path, data, working_dict, file_pattern, image_str, object_strs,
                                     csv_delimiter):

    print 'entering %s ...' % path
    sys.stdout.write('.')
    sys.stdout.flush()
    
    
    # recursive image and object counter
    current_num_of_images = 0
    current_num_of_objects = 0

    files = os.listdir( path )
    files.sort()

    for file in files:

        tmp_file = os.path.join( path, file )

        if os.path.isdir(tmp_file):
            # recurse into directory
            tmp_path = os.path.join( path, file )
            num_of_images, num_of_objects = import_cp2_csv_results_recursive(
                tmp_file, data, working_dict,
                file_pattern, image_str, object_strs,
                csv_delimiter
            )
            current_num_of_images += num_of_images
            current_num_of_objects += num_of_objects

        elif os.path.isfile(tmp_file):

            mo = file_pattern.match(file)
            if mo is not None and mo.group(2) == image_str:

                pre, post = mo.group(1), mo.group(3)

                # check for all necessary CSV files
                is_valid_csv_file = True
                for object_str in object_strs:
                    filename = os.path.join(path, pre + object_str + post)
                    #print 'filename:', filename
                    if not os.path.isfile(filename):
                        is_valid_csv_file = False

                if is_valid_csv_file:

                    #print 'importing image file %s...' % tmp_file
                    image_data = read_cp2_csv_file(tmp_file, csv_delimiter, 'single_line')
                    (images, img_column_names) = image_data

                    object_data = []
                    for object_str in object_strs:
                        #print 'importing object file %s...' % object_file_postfix
                        object_file = os.path.join(path, pre + object_str + post)
                        object_data.append(read_cp2_csv_file(object_file, csv_delimiter, 'double_line'))

                    # some consistency control
                    o0, ocn0 = object_data[0]
                    for o, ocn in object_data:
                        if len(o) != len(o0):
                            raise Exception( 'invalid objects input files' )

                    fill_data(data, working_dict, image_data, object_data)
                    #all_image_data.append( ( images,img_column_names,img_column_types ) )
                    #all_object_data.append( object_data )

                    current_num_of_images += len( images )
                    current_num_of_objects += len( o0 )

    return current_num_of_images, current_num_of_objects

# Import results (CSV-files) as exported from CellProfiler2.
# Returns an yaca_data_container.
# Input parameters:
#   path: path in which to look for .csv files
#   file_pattern: a regular expression describing the filenames of input csv file:
#       '(prefix)(name)(postfix)' whereas name is e.g. 'image' or 'cells'
#   image_str: the name in the pattern for image files, e.g. 'image'
#   object_strs: a list of names in the pattern for image files, e.g. ['cells']

def import_cp2_csv_results(path, file_pattern, image_str, object_strs,
                           csv_delimiter=','):

    print 'importing results'

    file_pattern = re.compile(file_pattern)

    # create data container
    data = {'images':[], 'objects':[], 'image_header':None, 'object_header':None}

    # recurse into all subfolders

    working_dict = {}

    num_of_images,num_of_objects = import_cp2_csv_results_recursive(path, data, working_dict,
                                                                    file_pattern, image_str, object_strs,
                                                                    csv_delimiter)

    del working_dict

    if len(data['images']) == 0 or len(data['objects']) == 0 \
       or ( len( data['images'] ) != num_of_images ) \
       or ( len( data['objects'][0] ) != num_of_objects ):
        raise Exception( 'Something went wrong when importing the data' )

    #image_table_shape = list( pdc.imgFeatures.shape )
    #if image_table_shape[0] > num_of_images:
    #    image_table_shape[0] = num_of_images
    #    pdc.imgFeatures.resize( image_table_shape )

    #object_table_shape = list( pdc.objFeatures.shape )
    #if object_table_shape[0] > num_of_objects:
    #    object_table_shape[0] = num_of_objects
    #    pdc.objFeatures.resize( object_table_shape )


    print '\n{} image sets and {} objects imported'.format(num_of_images,num_of_objects)

   
    return data

def output_cp2_results(data, images_file, objects_file, csv_delimiter=','):

    print 'creating output files...'

    try:

        image_writer = csv.writer(open(images_file, 'w'), delimiter=csv_delimiter)
        image_writer.writerow(data['image_header'])
        image_writer.writerows(data['images'])
    
        object_writer = csv.writer(open(objects_file, 'w'), delimiter=csv_delimiter)
        object_writer.writerow(data['object_header'])
        object_writer.writerows(data['objects'][0])

    except csv.Error, e:
        print 'CSV ERROR: file %s, line %d: %s' % (file.name, reader.line_num, e)
        raise

    print 'finished'





# Reads a CSV-file as exported from CellProfiler2.
# Returns (rows,column_names,column_types):
#   rows is the raw data from the CSV-file (excluding the header)
#   column_names has a name for each column
#   column_types has a type for each column (float or str)
# Input parameters:
#   file: an open file-descriptor or a filename
def read_cp2_csv_file(file, delimiter=',', HEADER_MODE='single_line'):

    close_file = False

    # open file if a filename was passed
    if type(file) == str:
        try:
            filename = file
            file = open(file,'rb')
            close_file = True
        except IOError, e:
            print 'ERROR: unable to open file %s: %s' % (filename, e)
            raise

    # use the CSV module to read the input file
    reader = csv.reader(file, delimiter=delimiter)

    try:

        # first we read the data from the file
        
        entities = []
        column_names = []
        found_header = False
        if HEADER_MODE == 'double_line':
            column_name_prefixes = []
            header_count = 0

        # this is used to keep the image name for several rows (in case it's not repeated)
        image = ''

        # read file
        for row in reader:

            if not found_header:
                if HEADER_MODE == 'single_line':
                    # we haven't found the row with the column-descriptions yet
                    if len(row[0].strip()) > 0:
                        # found it, write column-descriptions into columnIds
                        found_header = True
                        for name in row:
                            column_names.append(name)
                else:
                    if len(row[0].strip()) > 0:
                        header_count += 1
                        if header_count == 1:
                            for name in row:
                                column_name_prefixes.append(name)
                        else:
                            for name,prefix in zip(row, column_name_prefixes):
                                column_names.append(prefix + '_' + name)
                            found_header = True
            
            else:
                entities.append(row)

        return (entities,column_names)


    except csv.Error, e:
        print 'CSV ERROR: file %s, line %d: %s' % (file.name, reader.line_num, e)
        raise

    # some cleanup
    finally:
        if close_file:
            file.close()
