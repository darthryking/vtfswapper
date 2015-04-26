"""

vtfunswapper.py
By DKY

Version 0.0.0

Given a VDF-formatted file mapping names to swapped names, his program undoes 
the texture carnage caused by vtfswapper.py

"""

import os
import sys

import vdfutils

_DEFAULT_REMAP_FILE_NAME = 'vtfRemap.txt'


def un_rename_vtfs(remapDict):
    """ Given a dictionary mapping original names to remapped names, this 
    function renames the files so that they are back to how they were
    originally.
    
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
    
    # Rename all the files back to their original names.
    for originalName, vtfPath in remapDict.iteritems():
        os.rename(underscored(vtfPath), originalName)
        
    print "\t... Pass 2 complete."
    
    
def main(argv):
    try:
        remapFileName = argv[1]
    except IndexError:
        print "No remap file provided. Trying '{}' by default...".format(
                _DEFAULT_REMAP_FILE_NAME
            )
        remapFileName = _DEFAULT_REMAP_FILE_NAME
        
    print "Reading file {}...".format(remapFileName)
    here = os.getcwd()
    remapFilePath = os.path.join(here, remapFileName)
    try:
        with open(remapFilePath, 'r') as f:
            remapDict = vdfutils.parse_vdf(f.read())['remap']
    except IOError:
        sys.stderr.write(
                "File {} not found! Aborting...\n".format(remapFileName)
            )
        return 1
        
    print "Found {} remap entries.".format(len(remapDict))
    
    print "Un-renaming VTF files..."
    un_rename_vtfs(remapDict)
    
    print "Done! Enjoy your un-FUBAR'd textures!"
    
    raw_input("Press [ENTER] to continue...")
    
    return 0
    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
    
    