#!/usr/bin/python

"""Make sure that the symbolic links from the manual to the generated
subtree exist, unless there is already a real file there. """

import settings


def createLinks (config):
    """Look into config, in the Paths section, for any directory
    with generated as prefix, and has a corresponding manual directory as peer.
    Put symbolic links there if necessary to all files in generated."""


    import re
    import sys, os
    import glob
    
    opts = config.options("PathNames")
    for o in opts:
        if re.match ("gen", o):
            target =  "manual" + o[3:]
            if target in opts:
                # go over all files in o
                origindir = os.path.abspath(config.get ("PathNames", o))
                targetdir = config.get ("PathNames", target)
                originfiles =  glob.glob (os.path.join (origindir,  "*.tex"))
                originfiles.extend(glob.glob (os.path.join (origindir,  "*.pdf")))

                ## abstargetdir = os.path.abspath(targetdir)
                ## print "absorigindir: ", origindir
                ## print "abstargetdir: ", abstargetdir
                ## print os.path.commonprefix([origindir, abstargetdir])
                relpath = os.path.relpath (origindir, targetdir)
                ## print relpath 
                for of in originfiles:
                    f = os.path.basename(of)

                    # does a corresponding target file exist?
                    targetfile = os.path.join (targetdir, f)

                    if not os.path.exists (targetfile):
                        # if still might be a brokem symlink?
                        if not os.path.lexists (targetfile):
                            #  create a symbolic link to of
                            ## print "Creating symlink from " + \
                            ##       os.path.abspath(targetfile) + " to " + \
                            ##       os.path.join(relpath, f)
                            os.symlink (os.path.join(relpath, f),
                                        os.path.abspath(targetfile))
                        else:
                            print "Warning: " + targetfile + " seems to be a broken symblink" 
                
                

if __name__ == '__main__':
    import sys

    from optparse import OptionParser
    parser = OptionParser("Check existence of all required symbolic links, create if necessary.")
    parser.add_option ("-s", "--settings", dest="settingsfile",
                       help="the settings file")
    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="print lot's of debugging information",
                       action="store_true", default=False)
    (options, args) = parser.parse_args()

    config = settings.getSettings(options.settingsfile)

    createLinks (config)
    
