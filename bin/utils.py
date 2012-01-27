#!/usr/bin/python


#############################
#
# write file to right outfile

def writefile (t, f):
    fp = open (f, 'w')
    # print type(f)
    fp.write(t)
    fp.close 
