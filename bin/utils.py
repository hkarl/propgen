#!/usr/bin/python

"""A module with assorted helper and ultility functions and classes."""


import sys
import os
import codecs
import ConfigParser

#############################
#
# write file to right outfile

def writefile (t, f):
    """Write text t into file f. Main point: use utf-8 encoding for
    output. Just a shorthand. And empty t parameter causes the file to
    be overwritten with an empty file!"""

    if not t:
        t = ""

    # fp = open (f, 'w')
    fp = codecs.open (f, 'w', encoding='utf-8')
    ## print f
    ## print "writing: ", type(t)
    ## print t
    
    ## if isinstance (t, unicode):
    ##     # print "dealing with unicode"
    ##     pass
    ## else:
    ##     t = unicode (t, "utf-8")

    fp.write(t)
    fp.close 


################
# warning

def warning (w):
    """Append the warning text w to warnings.tex"""
    
    config = getSettings ("")
    f = open (os.path.join(config.get ("PathNames", 'genlatexpath'),
                           "warnings.tex"), 'a')
    out =  ("Warning: " + w).strip()
    print >> sys.stderr, out
    
    print >> f,  "\\item " + out
    f.close 
     


#####################
# resolve include commands:

def deepExpandInclude (prefix, infile):
    """Recursively expaned #include commands in XML files. Make sure
    UTF-8 is used for writing."""

    fin = codecs.open (os.path.join(prefix, infile),
                       'r', 'utf-8')
    tout = []
    tin = fin.readlines()
    for t in tin:
        if t.find('#include', 0,8) == 0:
            l=t.find('<')
            r=t.find('>')
            newfile = t[l+1:r]
            newfile = newfile.strip()
            tt = deepExpandInclude(prefix, newfile)
            tout.append(tt)
        else:
            tout.append(t)
    fin.close()
    return ' '.join(tout)
    
def expandInclude (prefix, infile, outfile):
    """Expand an xML file, make sure UTF-8 is used for reading."""
    
    prefOut = os.path.join (prefix, outfile)
    
    fout = codecs.open (prefOut, 'w', 'utf-8')
    tout = deepExpandInclude (prefix, infile)

    for t in tout:
        fout.write(t)
    fout.close()


################
# mapReduce a la google

def mapReduce (l, reducefct):
    """Perform a map reduce operation on a list of (key, value)
    pairs. Apply the reducefct in the reduce step.

    This is mostly used for building pie charts but might be generally
    useful.
    """
    
    return [reduce ( lambda a,b: (a[0], reducefct(a[1], b[1])), ll) \
           for ll in [filter (lambda x: x[0]==nn, l) \
                      for nn in set([ll[0] for ll in l])] \
           ]

######
# treeReduce: 

def treeReduce (l, reducefct):
    """Recursively apply a reduce function to a nested list structure.
    Atomic elements must be boolean values."""
    
    if isinstance(l, bool):
        return l
    else:
        ll = map (lambda x: treeReduce (x, reducefct), l)
        return reduce (reducefct, ll)

#####

def searchListOfDicts (l, key, value, returnkey):
    """Search a list l which contains dictionaries for an entry
    where key has value, and return the value of returnkey."""


    for ll in l:
        if ll[key] == value:
            return ll[returnkey]


#####
def roundPie  (l):
    """ round the values to 100%, input: list of (name, value) tuples"""

    v = [ll[1]*1.0 for ll in l] 
    s = sum(v)


    if s > 0:
        percents = [ vv*100./s for vv in v]

        rounded = [ int(vv) for vv in percents]

        while (sum(rounded) < 100):
            # which is point of largest rounding error?
            dif = [percents[i]-rounded[i] for i in range(len(rounded))]
            [maxval, maxind] = max([x, y] for y,x in enumerate(dif))

            rounded[maxind] += 1
    else:
        rounded = [0] * len(l)

    # return [ (l[i][0], str(rounded[i])) for i in range(len(rounded)) ]
    return ', '.join([ "%d/%s" %  (rounded[i], l[i][0]) for i in range(len(rounded)) ])


        
##############################################

class documentedDict(dict):
    """A slightly extended dict class. It has a property
    keydoc. Assigning a string to this property stroes a keydoc
    for the most recently assigned key in a class dictionary. Reading
    this property returns a dictionary of these keydocs."""
    
    keydocs = dict()

    def __init__ (self, *args, **kwargs):
        self.lastkey = ""
        self.update(*args, **kwargs)

    def __setitem__ (self, key, value):
        super(documentedDict, self).__setitem__ (key,value)
        self.lastkey = key

    @property
    def keydoc(self):
        return documentedDict.keydocs

    @keydoc.setter
    def keydoc(self, v):
        documentedDict.keydocs[self.lastkey] = v 



def docuDict (s, d, fp):
    """For documentation purposes: print a rest header using s, and
    then print the dictionary as a description list via dictAsRest()."""
    

    fp.write ( ''*len(s) + "\n")
    fp.write ( s + "\n" )
    fp.write ( '='*len(s) + "\n") 
    fp.write ('\n')

    dictAsRest (d, fp)
    
def dictAsRest (d, fp):
    """Given a dictionary, print key/values as a description list in
    reStructuredText syntax. Checks if the dictionary is a
    documentedDict and then pulls the corresponding keydoc and prints
    it as documentation of the key/value example. """

    import re 
    for k in sorted(d.keys()):
        v = d[k]
        if v:
            # v = re.sub('\\\\', '\\\\\\\\', v)
            fp.write ( "**"+ k + "**\n") 
            fp.write ( "   **Type**: " + str(type(v)) + "\n")
            fp.write ( "\n")

            ## print '--------------------'
            ## print k
            ## print type(v)
            ## print v

            if isinstance (d, documentedDict):
                if k in d.keydoc:
                    # print "documentedDict with key " + k 
                    tmp = re.sub('\\\\', '\\\\\\\\', d.keydoc[k])
                    fp.write ( '   **Documentation**: ' +
                               '\n   '.join(map(lambda x: x.strip(),
                                                tmp.lstrip().split('\n'))) + "\n\n")

            if isinstance (v, str) or isinstance(v, unicode):
                # duplicating backslashes is necessary to convince
                # sphinx to typeset them correctly in outpu
                tmp = re.sub('\\\\', '\\\\\\\\', v)
                fp.write ( '   **Example**: ' +
                           '\n   '.join(map(lambda x: x.strip(),
                                            tmp.lstrip().split('\n'))) + "\n")
            else:
                # print v
                fp.write ( "   **Example**: "+ str(v) + "\n")
            fp.write ( "\n")



#########################

def getSettings(filename):
    """Try to find the settings file, turn it into a configParser
    object, and do some first preprocessing on it."""

    if not filename:
        filename = "../settings.cfg"

    c = ConfigParser.SafeConfigParser()
    c.optionxform = str  # to make option names case sensitive! 

    if not c.read(filename):
        print "Settings file not found, was looking at: " + filename
        print "Serious problem - giving up"
        exit

    # add a .. prefix if pathNames appear
    if c.has_section('PathNames'):
        for o in c.options('PathNames'):
            if not o == 'bindir':
                c.set ('PathNames', o, os.path.join ('..', c.get('PathNames', o)))
                # print o, c.get('PathNames', o)


    return c 

##############################

def myFormat (x):
    """Take a number, either int or float, and return a string with the
    decimal point only present if necessary. E.g.,
    - myFormat(23) -> '23'
    - myFormat(23.5) -> '23.5'
    - myFormat(23.78) -> '23.8'
    """


    return '{0:.0f}'.format(x) if int(x)==x else  '{0:.1f}'.format(x)
