"""

vtfswapper.py
By DKY

Version 0.0.0

This program randomly swaps the names of every *.vtf file in a Source Engine 
mod's \materials folder, resulting in completely FUBAR'd textures.

Why you would actually want to do this, I have no idea.

"""

import os
import sys
from itertools import izip
from random import SystemRandom

import vdfutils

_r = SystemRandom()

_REMAP_FILE_NAME = 'vtfRemap.txt'


def find_vtfs(path):
    """ Takes a directory and returns all the *.vtf files in that directory 
    and its sub-directories.
    
    """
    
    vtfs = []
    for item in os.listdir(path):
        itemPath = os.path.join(path, item)
        if os.path.isdir(itemPath):
            vtfs += find_vtfs(itemPath)
        elif item.endswith('.vtf'):
            vtfs.append(itemPath)
            
    return vtfs
    
    
def rename_vtfs(remapDict):
    """ Renames every *.vtf file in the given remap dictionary to its 
    corresponding shuffled name.
    
    """
    
    def underscored(path):
        ''' Returns the name of the file at the given path, except with an 
        underscore prepended to the filename. The returned value is also a 
        full path to that file.
        
        '''
        
        fileName = os.path.basename(path)
        fileDir = os.path.dirname(path)
        
        return os.path.join(fileDir, '_{}'.format(fileName))
        
    # Prepend all of the existing filenames with underscores, to prevent 
    # renaming conflicts.
    for vtfPath in remapDict:
        os.rename(vtfPath, underscored(vtfPath))
        
    print "\t... Pass 1 complete."
    
    # Rename all the files to their corresponding new names
    for vtfPath, newName in remapDict.iteritems():
        os.rename(underscored(vtfPath), newName)
        
    print "\t... Pass 2 complete."
    
    
def main():
    print "Finding VTF files...",
    here = os.getcwd()
    materialsDir = os.path.join(here, 'materials')
    vtfs = find_vtfs(materialsDir)
    
    print "Found {} files.".format(len(vtfs))
    
    print "Shuffling names..."
    shuffledNames = vtfs[:]
    _r.shuffle(shuffledNames)
    
    print "Building name remap dictionary..."
    # Dictionary that maps names to shuffled names
    remapDict = dict(izip(vtfs, shuffledNames))
    
    print "Renaming VTF files..."
    rename_vtfs(remapDict)
    
    print "Saving name remap dictionary for future restoration..."
    remapFilePath = os.path.join(here, _REMAP_FILE_NAME)
    with open(remapFilePath, 'w') as f:
        f.write(vdfutils.format_vdf({'remap' : remapDict}))
        
    print "Done! Enjoy your FUBAR'd textures!"
    
    raw_input("Press [ENTER] to continue...")
    
    return 0
    
    
if __name__ == '__main__':
    sys.exit(main())
    
    