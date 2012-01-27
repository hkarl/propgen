#!/usr/bin/python

# Goal: Read in the wiki text and prodcue the required XML files
# Basis are:
# - the project main wiki file
# - the workpackage wiki files

from pprint import pprint as pp
import wikiParser
import settings
import os 
from xml.etree.ElementTree import ElementTree, dump, SubElement, Element
from string import Template
from utils import *


def projectXML(wiki, parser):
    """Produce the main project file"""

    tmp = parser.getList(parser.getSection (wiki, "Main data", 2))
    tmp = [x.split(':') for x in tmp]
    tmp = [(x[0], x[1].strip()) for x in tmp]
    mainData = dict(tmp)

    ## pp(mainData)

    ## tree=Element("project")
    ## tmp = SubElement (tree, "duration")
    ## tmp.text = mainData["Duration (in months)"]

    ## dump(tree)

    t = Template("""
  <projectname> ${Projectname} </projectname> 
  <projectshort> ${Acronym}  </projectshort>
  <duration> ${Duration} </duration>
  <call> ${Call}  </call> 
  <instrument> ${Instrument} </instrument> 
  <topics> ${Topics}</topics>
  <coordinator>
    <name> ${CoordinatorName}</name>
    <email>${CoordinatorEmail}</email>
    <tel> ${CoordinatorPhone}</tel>
  </coordinator>
#include<partners.xml>
    """)

    res = t.substitute (mainData)
    # print res 
    return res


####################################
def singleWorkpackageXML (wp, wpwiki, parser):
    print "analyzing wp: " + wp
    print "wiki code: \n" + wpwiki

    if not wpwiki:
        return 

####################################

def workpackageXML(wiki, parser):
    """Produce the workpackage-related XML structure.
    - The include commands in the project-wide XML
    - The per-workpackage XML
    """

    wplist = parser.getList(parser.getSection (wiki, "Workpackages", 2))
    # print wplist

    wpIncluder = "" 
    t = "<workpackages>\n"
    for wp in wplist:
        t += "#include<" + wp + ".xml>\n"
    t+="</workpackages>\n"

    # and generate the individual wps:
    for wp in wplist:
        wpwiki = open(os.path.join(config.get('PathNames', 'wppath'),
                                   wp),
                      'r').read()
        singleWorkpackageXML (wp, wpwiki, parser)
        wpIncluder += "\\input{wp/"+ wp + ".tex}\n"

    writefile (wpIncluder, 
               os.path.join(config.get('PathNames', 'wppath'),
                            'wpIncluder.tex'))
    
    return t
    

####################################
    
def partnerXML(wiki, parser):
    """Produce the partner XML file. And while we are at it, as produce the
    Partner includer file for latex"""

    partnerDict = parser.getTable(parser.getSection (wiki, "Partner data", 2))

    # pp(partnerDict) 

    partnerIncluder = "" 
    xml = "<allpartners>\n"
    for partner in partnerDict:
        xml += "\t<partnerdescription>\n"
        for k,v in partner.iteritems():
            xml += "\t\t<" + k + "> " + v + "</" + k + ">\n"  
        xml += "\t</partnerdescription>\n"
        partnerIncluder += "\\input{partners/" + partner["Wiki"] + ".tex}\n" 
    xml += "</allpartners>\n"

    writefile (xml, 
               os.path.join(config.get('PathNames', 'xmlpath'),
                            'partners.xml'))

    writefile (partnerIncluder, 
               os.path.join(config.get('PathNames', 'partnerspath'),
                            'partnersIncluder.tex'))



####################################

if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option ("-s", "--settings", dest="settingsfile",
                       help="the settings file")
    parser.add_option ("-p", "--page", dest="page",
                       help="which page to pull from the wiki")
    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="print lot's of debugging information",
                       action="store_true", default=False)
    (options, args) = parser.parse_args()

    config = settings.getSettings(options.settingsfile)

    # read in the main project wiki file
    projectWiki = open(os.path.join(config.get('PathNames', 'wikipath'),
                                    config.get('Wiki', 'projectName')), 'r').read()

    # print projectWiki

    wikiParser = wikiParser.wikiParserFactory (config)

    tree = "<project>" + \
           projectXML (projectWiki, wikiParser) + \
           workpackageXML (projectWiki, wikiParser) + \
           "</project>"
    
    writefile (tree,
               os.path.join(config.get('PathNames', 'xmlpath'),
                            'main.xml'))
    
    partnerXML (projectWiki, wikiParser) 
