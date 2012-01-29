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
import utils 


def projectXML(wiki, parser):
    """Produce the main project file"""

    mainData = parser.getListAsDict(parser.getSection (wiki, "Main data", 2))

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
def dictAsXML (d, parser=None, specialFields=[]):
    """Turn a dict into an XML string. specialFields is a list of keys where the
    content should be split up into individual fields."""

    t = ""
    for k, v in d.iteritems():
        if k in specialFields:
            kk= k.strip('s')
            kk= kk.strip('(s)') 
            for vv in v.split(','):
                # is it the main contributor?
                vvv = vv.lstrip(parser.boldfaceDelimiter()).strip(parser.boldfaceDelimiter())
                if vv==vvv:
                    t += "<" + kk + " main=0>" + str(vv.strip()) + "</" + kk + ">\n"
                else:
                    t += "<" + kk + " main=1>" + str(vvv) + "</" + kk + ">\n"
        else:
            t += "<" + k + ">" + str(v) + "</" + k + ">\n"

    return t 

####################################
def singleWorkpackageXML (wp, wpwiki, parser, wpcount):
    # print "analyzing wp: " + wp
    # print "wiki code: \n" + wpwiki

    ### main adminstration information: 
    wpMain = parser.getListAsDict(parser.getSection (wpwiki,
                                               "Administrative information", 2))
    wpMain['Number'] = wpcount 

    #### get the deliverables
    wpDelXML = ""
    for deliv in parser.getTable(parser.getSection (wpwiki, "Deliverables", 3)): 
        wpDelXML += '<deliverable id="' + deliv["Label"] +'">\n'  + \
                    dictAsXML(deliv, parser, ["Contributors", "Producing task(s)"]) + \
                    "</deliverable>\n"

    ## get the milestones
    wpMilestonesXML = "" 
    for ms in parser.getTable(parser.getSection (wpwiki, "Milestones", 3)): 
        wpMilestonesXML += '<milestone id="' + ms["Label"] + '">\n'  + \
                    dictAsXML(ms, parser, ["Contributors", "Producing task(s)"]) + \
                    "</milestone>\n"

    ## get the tasks
    wpTasksXML = "" 
    for task in parser.getTable(parser.getSection (wpwiki, "Tasks", 3)): 
        wpTasksXML += '<task id="' + task["Label"] + '">\n'  + \
                    dictAsXML(task) + \
                    "</task>\n"
        
    ## get the effort - that's a little bit more difficult: 
    wpEffortXML = ""
    for effort in parser.getTable(parser.getSection (wpwiki, "Effort", 3)):
        wpEffortXML += '<partner id="' + effort["Partner"] + '">\n'
        for k,v in effort.iteritems():
            if not k=="Partner":
                wpEffortXML += "<taskeffort><task>" + k + \
                               "</task><resources>" + v + \
                               "</resources></taskeffort>\n"
                # a bit of error checking:
                if not k in wpTasksXML:
                    print "Warning: assigning effort to task " + k + " which is not defined in this wp " + wp 
        wpEffortXML += '</partner>\n'
        

    ## and the final workpackage string 
    wpXML =  '<workpackage id="' + wp + '">' + \
            dictAsXML (wpMain) + \
            "<objectives>\n" + parser.getSection(wpwiki, "Objectives", 2).strip() + "</objectives>\n" + \
            wpDelXML + \
            wpMilestonesXML + \
            wpTasksXML + \
            wpEffortXML + \
            "</workpackage>"

    utils.writefile (wpXML, 
                     os.path.join(config.get('PathNames', 'xmlwppath'),
                                  wp + '.xml'))


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
    wpCount = 1
    for wp in wplist:
        wpwiki = open(os.path.join(config.get('PathNames', 'wikiwppath'),
                                   wp),
                      'r').read()
        singleWorkpackageXML (wp, wpwiki, parser, wpCount)
        wpCount += 1 
        wpIncluder += "\\input{wp/"+ wp + ".tex}\n"

    utils.writefile (wpIncluder, 
                     os.path.join(config.get('PathNames', 'genlatexwppath'),
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

    utils.writefile (xml, 
                     os.path.join(config.get('PathNames', 'xmlpath'),
                                  'partners.xml'))

    utils.writefile (partnerIncluder, 
                     os.path.join(config.get('PathNames', 'genlatexpartnerspath'),
                                  'partnersIncluder.tex'))



####################################

if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option ("-s", "--settings", dest="settingsfile",
                       help="the settings file")
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
    
    utils.writefile (tree,
                     os.path.join(config.get('PathNames', 'xmlpath'),
                                  'main.xml'))
    
    partnerXML (projectWiki, wikiParser) 
