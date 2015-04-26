"""

vdfutils.py

Utilities for processing Valve KeyValue data formats.

"""

from collections import OrderedDict

VALID_CHARS = (
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '0123456789'
    '-_.'
)

WHITESPACE = ' \r\n\t'

# Byte that gets appended to keys to ensure uniqueness
UNIQUEIFIER = '\x1d'


class VDFConsistencyFailure(Exception):
    """ You have a bad VDF file. :( """
    
    BAD_VDF_MSG = "You have a bad VDF file. :("
    
    def __str__(self):
        return "{}\nError is: {}".format(self.BAD_VDF_MSG, self.message)
        
        
def parse_vdf(inData, ordered=True, duplicates=False):
    """ Parse a string in VDF format and return a dictionary representing the
    data.
    
    ordered:        Preserve ordering
    duplicates:     Allow duplicate keys (may cause Unicode problems)
    
    """
    
    class States:
        ''' Holds state variables for the parser. '''
        
        quoteStart = -1
        quoteEnd = -1
        
        wordStart = -1
        wordEnd = -1
        
        key = ''
        
        bracketStart = -1
        bracketEnd = -1
        
        isCommented = False
        
    def find_bracket_end(inData, bracketStart):
        ''' Find and return the index of a matched closing bracket, given the 
        start index of an opening bracket.
        
        '''
        
        pairCount = 0
        isCommented = False
        inQuotes = False
        
        for i, c in enumerate(inData[bracketStart:]):
            if not isCommented:
                if c == '{':
                    pairCount += 1
                    
                elif c == '}':
                    
                    # This must hold because we return when pairCount == 1,
                    # and the first bracket is necessarily an opening bracket.
                    assert pairCount > 0
                    
                    if pairCount == 1:
                        return bracketStart + i
                        
                    elif pairCount > 1:
                        pairCount -= 1
                        
                elif c == '"':
                    inQuotes = not inQuotes
                    
                elif c == '/':
                    if not inQuotes and inData[bracketStart:][i + 1] == '/':
                        isCommented = True
                        
            elif c == '\n':
                isCommented = False
                
        raise VDFConsistencyFailure("Mismatched brackets!")
        
    def get_word(i):
        ''' Set wordEnd to the current index and grab the word at this
        position, assuming that the wordStart index has been found already.
        
        '''
        
        # This is a function precondition.
        assert States.wordStart != -1
        
        States.wordEnd = i
        
        word = inData[States.wordStart:States.wordEnd]
        if States.key:
            data[States.key] = word
            States.key = ''
            
        else:
            States.key = word
            
            while duplicates and (States.key in data):
                # Ensures that dictionary States.keys are unique, if 
                # duplicates are being allowed.
                States.key += UNIQUEIFIER
                
        States.wordStart = -1
        States.wordEnd = -1
        
    def get_quotes(i):
        ''' Set quoteEnd to the current index and grab the entry at this
        position, assuming that the quoteStart index has been found already.
        
        '''
        
        # This is a function precondition.
        assert States.quoteStart != -1
        
        States.quoteEnd = i
        
        quoteContents = inData[States.quoteStart + 1:States.quoteEnd]
        
        if States.key:
            data[States.key] = quoteContents
            States.key = ''
            
        else:
            States.key = quoteContents
            
            while duplicates and (States.key in data):
                # Ensures that dictionary States.keys are unique, if 
                # duplicates are being allowed.
                States.key += UNIQUEIFIER
                
        States.quoteStart = -1
        States.quoteEnd = -1
        
    ######################
    # Main function body #
    ######################
    
    if ordered:
        data = OrderedDict()
    else:
        data = {}
        
    i = 0
    while 1:
        # This is a while loop instead of a for loop because we need to be
        # able to jump the index forward by arbitrary amounts.
        
        try:
            c = inData[i]
        except IndexError:
            if States.wordStart != -1:
                get_word(i)
                
            if States.key:
                raise VDFConsistencyFailure("Key without value!")
                
            break
            
        if not States.isCommented:
            if c in VALID_CHARS:
                if States.quoteStart == -1 and States.wordStart == -1:
                    States.wordStart = i
                    
            elif c in WHITESPACE:
                if States.wordStart != -1:
                    get_word(i)
                    
            elif c == '"':
                if States.wordStart != -1:
                    get_word(i)
                    
                elif States.quoteStart != -1:
                    get_quotes(i)
                    
                else:
                    States.quoteStart = i
                    
            elif c == '{':
                if not States.key:
                    raise VDFConsistencyFailure("Brackets have no heading!")
                
                States.bracketStart = i
                States.bracketEnd = find_bracket_end(inData, i)
                
                # Recursion is fun!
                data[States.key] = parse_vdf(
                        inData[States.bracketStart + 1:States.bracketEnd],
                        ordered=ordered,
                        duplicates=duplicates,
                    )
                
                States.key = ''
                
                i = States.bracketEnd
                
                States.bracketStart = -1
                States.bracketEnd = -1
                
            elif c == '}':
                raise VDFConsistencyFailure("Mismatched brackets!")
                
            elif c == '/':
                try:
                    nextChar = inData[i + 1]
                except IndexError:
                    break
                    
                if States.quoteStart == -1 and nextChar == '/':
                    States.isCommented = True
                    
        elif c == '\n':
            States.isCommented = False
            
        i += 1
        
    return data
    
    
def format_vdf(data, indentLevel=0):
    """ Take dictionary data and return a string representing that data in VDF 
    format.
    
    """
    
    SINGLE_INDENT = ' ' * 4
    INDENT = SINGLE_INDENT * indentLevel
    
    outData = []
    
    for key, item in data.iteritems():
        key = key.replace(UNIQUEIFIER, '')
        
        if type(item) is str or type(item) is unicode:
            outData += (
                INDENT,
                '"{}"'.format(key),
                SINGLE_INDENT,
                '"{}"'.format(item),
                '\n',
            )
            
        else:
            outData += (
                INDENT, '"{}"'.format(key),
                '\n', INDENT, '{\n',
                format_vdf(item, indentLevel + 1),  # Recursion is fun!
                '\n', INDENT, '}\n',
            )
            
    return ''.join(outData)
    
    