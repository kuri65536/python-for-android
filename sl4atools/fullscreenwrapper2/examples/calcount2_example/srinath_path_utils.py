import sys
import os
import os.path

def get_filepath_in_exec_file_dir(filename):
    return os.path.join(get_exec_file_dir(), filename)
    
def get_exec_file_dir():
    return os.path.dirname(unicode(sys.argv[0]))
    
def get_exec_file_parent_dir():
    return os.path.split(unicode(os.path.dirname(sys.argv[0])))[0]

def get_extension(filename):
    return os.path.splitext(unicode(filename))[1]

def get_extension_lowercase(filename):
    return get_extension(unicode(filename)).lower()

def get_filename_without_extension_or_path(filename):
    i = os.path.split(filename)[1]
    return os.path.splitext(i)[0]

def walk_filenames_by_extension(root, extension_list):
    """
    Walks down the root directory & matches files with specified extensions. Returns list of file-paths
    IMPORTANT: This converts extensions to lowercase before comparison (windows behavior)
    """
    ret = []
    for extension in extension_list:
        if(extension[0]!="."):
            use_ext = "."+extension
        else:
            use_ext = extension
            
        for dirpath, dirnames,  filenames in os.walk(root):
            for filename in filenames:
                if get_extension_lowercase(filename)==use_ext.lower():
                    ret.append(os.path.join(dirpath,filename))
                    
    return ret
        
    

