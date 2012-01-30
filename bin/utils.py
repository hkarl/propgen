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
     


