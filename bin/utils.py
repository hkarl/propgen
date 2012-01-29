#!/usr/bin/python


import settings
import sys
import os


#############################
#
# write file to right outfile

def writefile (t, f):
    fp = open (f, 'w')
    # print type(f)
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
     


