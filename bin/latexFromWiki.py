#!/usr/bin/python

"""
Generate LaTeX code from all the plain wiki files.

* This pertains to the plain files as well as to the partner files.

* Uses the settings file to find out relevant directories.

* XML files are not treated here; that is more complicated.

Essentially, this script just creates a WikiParser object via the
libaray and applies it to the corresponding files. 

"""

import wikiParser
import glob
import os 
import codecs
import utils
import re

from pprint import pprint as pp


def handleFile (f, outdir, parser, config, verbose=False):
    """Translate a wiki file with name f to the corresponding LaTeX file.

    Information where and how to translate are giving in config. Parser is
    a parser object for the correct wiki style.

    Exception: if the filename contains bibtex in some capitalization, we append .bib, not .tex. 
    """

    if re.search ('bibtex', f, re.IGNORECASE):
        suffix = ".bib"
    else:
        suffix = ".tex"
        
    fileName = os.path.basename(f)
    inputDir = os.path.dirname(f)
    if verbose:
        print "Generating LaTeX from wiki file " + fileName  + " in dir: " + inputDir
        print " and storing it in " + outdir + " as path " + os.path.join (outdir, fileName)+suffix

    # caution: we have to open that as UTF-8 files!
    wiki = codecs.open (f, 'r', 'utf-8').read()

    # if verbose:
    #     print wiki
    #     print parser.getLaTeX (wiki)

    utils.writefile (parser.getLaTeX (wiki, fileName), os.path.join (outdir, fileName+suffix))


########################################
if __name__ == '__main__':
    import sys

    from optparse import OptionParser
    parser = OptionParser("Turn all the plain wiki files into corresponding LaTeX files")
    parser.add_option ("-s", "--settings", dest="settingsfile",
                       help="the settings file")
    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="print lot's of debugging information",
                       action="store_true", default=False)
    (options, args) = parser.parse_args()

    config = utils.getSettings(options.settingsfile)

    parser = wikiParser.wikiParserFactory (config)


    ##  do the normal wiki files:
    files = glob.glob (os.path.join (config.get("PathNames", "wikipath"),
                                     "*"))
    for f in files:
        if os.path.isdir (f):
            continue

        if config.get("Wiki", "projectName") in f:
            continue
        
        handleFile (f, config.get("PathNames", "genlatexpath"),
                    parser, config, options.verbose)

    ## and the partner files: 
    files = glob.glob (os.path.join (config.get("PathNames", "wikipartnerpath"),
                                     "*"))
    for f in files:
        if os.path.isdir (f):
            continue

        handleFile (f, config.get("PathNames", "genlatexpartnerspath"),
                    parser, config, options.verbose)
