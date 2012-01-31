#!/usr/bin/python


import settings
import sys
import os
import codecs

#############################
#
# write file to right outfile

def writefile (t, f):
    """Write text t into file f. If flag utf8conversion is set,
    try to run a conversion into UTF-8."""

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

    config = settings.getSettings ("")
    f = open (os.path.join(config.get ("PathNames", 'genlatexpath'),
                           "warnings.tex"), 'a')
    out =  ("Warning: " + w).strip()
    print >> sys.stderr, out
    
    print >> f,  "\\item " + out
    f.close 
     


#####################
# resolve include commands:

def deepExpandInclude (prefix, infile):
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

    prefOut = os.path.join (prefix, outfile)
    
    fout = codecs.open (prefOut, 'w', 'utf-8')
    tout = deepExpandInclude (prefix, infile)

    for t in tout:
        fout.write(t)
    fout.close()


