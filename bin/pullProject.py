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
def getProposalStructure (masterPage, pullInstance, config, wikidir, parser):
    """Extract all the relevant files for the actual proposal text from the wiki."""

    t = parser.getSection(masterPage, "Proposal structure", 2)
    pages = parser.getList (t)

    for p in pages:
        # print p
        t = pullInstance.getPage (p)
        utils.writefile (t, os.path.join(wikidir, p))


############################
def getWorkpackages (masterPage, pullInstance, config, wikidir, parser):
    """Identify all the workpackages and download them""" 

    t = parser.getSection(masterPage, "Workpackages", 2)
    pages = parser.getList (t)

    for p in pages:
        # print p
        t = pullInstance.getPage (p)
        utils.writefile (t, os.path.join(wikidir, "wp", p))


############################
def getPartners (masterPage, pullInstance, config, wikidir, parser):
    """get all the partner description files"""

    t = parser.getSection(masterPage, "Partner data", 2)
    table = parser.getTable (t) 
    # pp(table)

    for p in table:
        pw = str(p['Wiki'])
        t = pullInstance.getPage (pw)
        utils.writefile (t, os.path.join(wikidir, pw))
        
    
    ## TODO: build the XML file for partners
    
    
if __name__ == "__main__":

############################
    # get command line options 
    parser=OptionParser()
    parser.add_option ("-s", "--settings", dest="settingsfile",
                       help="the settings file")
    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="print lot's of debugging information",
                       action="store_true", default=False)
    (options, args) = parser.parse_args()
    

    config = settings.getSettings(options.settingsfile) 

    wikidir = config.get('PathNames', 'wikipath')
    projectname = config.get('Wiki','projectName')
    wikiParser = wikiParser.wikiParserFactory(config)

    ### main file: 
    pullInstance = pullWiki.pullFactory (config, options.verbose)
    masterPage = pullInstance.getPage(projectname)
    utils.writefile (masterPage, os.path.join(wikidir, projectname))

    getProposalStructure (masterPage, pullInstance, config, wikidir, wikiParser)
    getWorkpackages (masterPage, pullInstance, config, wikidir, wikiParser)
    getPartners (masterPage, pullInstance, config, wikidir, wikiParser)
    
