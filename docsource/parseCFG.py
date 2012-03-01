#!/usr/bin/python

# read in a config cfg file, produce restructuredText files extracted from the comments


import os
import re

def parseFile (lines, options):
    comment = []
    lastsection = ""
    
    for l in lines:
        # a comment line? 
        if re.match ('^# ', l):
            comment.append(l[2:].strip(' '))
            continue
        
        # a new section? 
        m = re.match (r'\[(.*)\]', l)
        if m:
            lastsection = m.group(1).strip().lstrip()
            print
            print ".. index::"
            print "   single: ", os.path.basename(options.inputfile), "; ", lastsection
            print options.prechar*len(lastsection)
            print lastsection
            print options.postchar*len(lastsection)
            print '.. program:: ', lastsection
            print 
            print ''.join(comment)
            comment = []
            continue

        # starting with a whitespace? continuation of an assignment?
        m = re.match (r'^\s+(.+)', l)
        if m:
            print '   ', re.sub('\\\\', '\\\\\\\\', m.group(1))
            continue 

        # an assignment? 
        m = re.match (r'^(.*)=(.*)', l)
        if m:
            print 
            print '.. describe:: %s' % (m.group(1).strip())
            ## print '   :index:`index entries <pair: %s; %s>`' % (lastsection,
            ##                                                     m.group(1).strip())
            print 
            print '   ', '    '.join(comment)
            print '   ', "Default: ", re.sub('\\\\', '\\\\\\\\', m.group(2), re.MULTILINE)
            comment = []
            continue


if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option ("-i", "--input", dest="inputfile",
                       help="the input .cfg file to be parsed")
    parser.add_option ("-d", "--directory", dest="outputdir",
                       help="the output directory",
                       default = "")
    parser.add_option ("-b", "--before", dest="prechar",
                       help="which character to be used BEFORE a heading",
                       default="")
    parser.add_option ("-a", "--after", dest="postchar",
                       help="which character to be used AFTER  a heading",
                       default="")
    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="print lot's of debugging information",
                       action="store_true", default=False)
    (options, args) = parser.parse_args()
    
    lines =  open(options.inputfile, 'r').readlines()

    parseFile (lines, options) 
