'''
Created on Jul 24, 2012

@author: Admin
'''

import os.path
import srinath_path_utils

RESOURCE_TYPE_LAYOUT = ["res","layout"]
RESOURCE_TYPE_DRAWABLE = ["res","drawable"]
RESOURCE_TYPE_DATA = ["data",]

def get_resource_pathname(resource_filename, resource_type):
    retpath = srinath_path_utils.get_exec_file_dir()
    for subdir in resource_type:
        retpath = os.path.join(retpath,subdir)
        
    return os.path.join(retpath,resource_filename)

def get_drawable_pathname(drawable_filename):
    return "file://"+get_resource_pathname(drawable_filename, RESOURCE_TYPE_DRAWABLE)

def get_layout_pathname(layout_filename):
    return get_resource_pathname(layout_filename, RESOURCE_TYPE_LAYOUT)

def get_data_pathname(data_filename):
    return get_resource_pathname(data_filename, RESOURCE_TYPE_DATA)

def read_layout_xml(layout_filename):
    fil = open(get_layout_pathname(layout_filename))
    xmldata = fil.read()
    fil.close()
    return xmldata

if __name__ == '__main__':
    print get_data_pathname("abc.db3")
