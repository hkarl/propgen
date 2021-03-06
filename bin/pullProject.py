#!/usr/bin/python

""" Pull the raw wiki files from wherever is specified in
settings.cfg. Store the raw wiki syntax in the wikipath directory. """

import pullWiki
import os 
from optparse import OptionParser
import wikiParser 
from pprint import pprint as pp
import utils



############################
def getProposalStructure (masterPage, pullInstance, config, parser, verbose=False):
    """Extract all the relevant files for the actual proposal text from the wiki."""

    t = parser.getSection(masterPage, "Proposal structure", 2)
    pages = parser.getList (t)

    for p in pages:
        if verbose:
            print "Now pulling page: "  + p
        t = pullInstance.getPage (p)
        utils.writefile (t,
                         os.path.join(config.get("PathNames", "wikipath"), p))


############################
def getWorkpackages (masterPage, pullInstance, config, parser, verbose=False):
    """Identify all the workpackages and download them""" 

    t = parser.getSection(masterPage, "Workpackages", 2)
    pages = parser.getList (t)

    for p in pages:
        if verbose:
            print "Now pulling workpackge: " + p
        t = pullInstance.getPage (p)
        utils.writefile (t,
                         os.path.join(config.get("PathNames", "wikiwppath"), p))


############################
def getPartners (masterPage, pullInstance, config, parser, verbose=False):
    """get all the partner description files"""

    t = parser.getSection(masterPage, "Partner data", 2)
    table = parser.getTable (t) 
    # pp(table)

    for p in table:
        pw = str(p['Wiki'])
        if verbose:
            print "Now pulling partner: " + pw 
        t = pullInstance.getPage (pw)
        utils.writefile (t,
                         os.path.join(config.get("PathNames", "wikipartnerpath"), pw))
        
    
    ## TODO: build the XML file for partners
    
############################

def ensureDirectories(config):
    """A small helper function that makes sure that all the
    directories that are mentioned in settings.cfg PathNames section
    actually exist. This can be useful after a make clean or in case
    directories have been manually and inadvertently removed. """
    paths = config.options("PathNames")
    for p in paths:
        if not os.access (config.get("PathNames", p), os.F_OK):
            os.mkdir (config.get("PathNames", p))
    
############################
if __name__ == "__main__":

    # get command line options 
    parser=OptionParser()
    parser.add_option ("-s", "--settings", dest="settingsfile",
                       help="the settings file")
    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="print lot's of debugging information",
                       action="store_true", default=False)
    (options, args) = parser.parse_args()
    

    config = utils.getSettings(options.settingsfile) 

    projectname = config.get('Wiki','projectName')
        
    wikiParser = wikiParser.wikiParserFactory(config)

    ### Ensure that all directories exist!
    ensureDirectories (config) 

    ### main file: 
    pullInstance = pullWiki.pullFactory (config, options.verbose)
    if options.verbose:
        print "Pulling main project page: " + projectname
    masterPage = pullInstance.getPage(projectname)
    utils.writefile (masterPage,
                     os.path.join(config.get('PathNames', 'wikipath'),
                                  projectname))

    getProposalStructure (masterPage, pullInstance, config, wikiParser, options.verbose)
    getWorkpackages (masterPage, pullInstance, config, wikiParser, options.verbose)
    getPartners (masterPage, pullInstance, config, wikiParser, options.verbose)
    
