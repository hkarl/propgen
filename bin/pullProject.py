#!/usr/bin/python

# goal: pull all the files pertaining to a project from the wiki

import pullWiki
import settings
import os 
from optparse import OptionParser
import wikiParser 
from pprint import pprint as pp
import utils



############################
def getProposalStructure (masterPage, pullInstance, config, parser):
    """Extract all the relevant files for the actual proposal text from the wiki."""

    t = parser.getSection(masterPage, "Proposal structure", 2)
    pages = parser.getList (t)

    for p in pages:
        # print p
        t = pullInstance.getPage (p)
        utils.writefile (t,
                         os.path.join(config.get("PathNames", "wikipath"), p))


############################
def getWorkpackages (masterPage, pullInstance, config, parser):
    """Identify all the workpackages and download them""" 

    t = parser.getSection(masterPage, "Workpackages", 2)
    pages = parser.getList (t)

    for p in pages:
        # print p
        t = pullInstance.getPage (p)
        utils.writefile (t,
                         os.path.join(config.get("PathNames", "wikiwppath"), p))


############################
def getPartners (masterPage, pullInstance, config, parser):
    """get all the partner description files"""

    t = parser.getSection(masterPage, "Partner data", 2)
    table = parser.getTable (t) 
    # pp(table)

    for p in table:
        pw = str(p['Wiki'])
        t = pullInstance.getPage (pw)
        utils.writefile (t,
                         os.path.join(config.get("PathNames", "wikipartnerpath"), pw))
        
    
    ## TODO: build the XML file for partners
    
############################

def ensureDirectories(c):
    paths = c.options("PathNames")
    for p in paths:
        # print p, c.get("PathNames", p)  
        if not os.access (c.get("PathNames", p), os.F_OK):
            os.mkdir (c.get("PathNames", p))
    
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
    

    config = settings.getSettings(options.settingsfile) 

    projectname = config.get('Wiki','projectName')
    wikiParser = wikiParser.wikiParserFactory(config)

    ### Ensure that all directories exist!
    ensureDirectories (config) 

    ### main file: 
    pullInstance = pullWiki.pullFactory (config, options.verbose)
    masterPage = pullInstance.getPage(projectname)
    utils.writefile (masterPage,
                     os.path.join(config.get('PathNames', 'wikipath'),
                                  projectname))

    getProposalStructure (masterPage, pullInstance, config, wikiParser)
    getWorkpackages (masterPage, pullInstance, config, wikiParser)
    getPartners (masterPage, pullInstance, config, wikiParser)
    
