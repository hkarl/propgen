import settings
import wikiParser
import glob
import os 
import sys 
import codecs
import utils
import re 
from string import Template

from pprint import pprint as pp
from xml.etree.ElementTree import ElementTree, dump


# global variables, to store all the state of the proposal 
allWPDicts= []
allMilestones = []
allDeliverables = []
allTasks = []
allEfforts = []
partnerList = []
titlepage = {}


def dictFromXML (tree):
    return dict ([(x.tag.strip(), x.text.strip()) for x in tree.getchildren()])

def dictFromXMLWithMains (tree):
    d = {}
    ll = [(x.tag.strip(), x.text.strip(), x.attrib) for x in tree.getchildren()]

    for l in ll:
        tag = l[0]
        val = l[1]
        attrib = l[2]
        hasMain = False
        
        if d.has_key(tag):
            # need to think about the arrays
            if attrib.has_key("main"):
                d[tag].append(val)
                hasMain = True
            else:
                print "warning: overwriting key which has no main attribute! - latexFromXML"
                d[tag] = val
        else:
            if attrib.has_key("main"):
                d[tag] = [val]
                hasMain = True
            else:
                d[tag] = val

        if attrib.has_key("main"):
            # note: only support for a SINGLE main entity ! 
            if attrib["main"] == "True":
                d[tag+"Main"] = val
            else:
                d[tag+"Main"] = ""

        if hasMain:
            # TODO: add sorting order here
            # it doesnt make a lot of sense for all things, but useful nonetheless
            d[tag+"String"] = ", ".join([ "\\textbf{" + x + "}" if x == d[tag+"Main"]
                                          else x
                                          for x in sorted(d[tag])])
    return d

def analyzePartners (tree):
    
    global partnerList
    for p in tree.getchildren():
        partnersDict = dictFromXML(p)
        partnerList.append(partnersDict)
    # pp(partnerList)
    return partnerList 


def fixProducingTask (ll):
    """Input is a list of milestones or deliverables. We need to
    fix the ProducingtaskString; dictFromXMLWithMains is not
    specific enough for that job. Replace the task label by the task
    IDs and do proper sorting, keeping in mind the ordering of task ids"""

    global allTasks
    # let's build a little help structure for the task ids, to make access clearer
    taskmap = dict([(t["Label"], t["taskId"]) for t in allTasks])
    taskmap[''] = ''
    # print "taskmap"
    # pp(taskmap)
    for md in ll:
        if md.has_key("Producingtask"):
            tmp = sorted([taskmap[x] for x in md["Producingtask"]])
            # print tmp
            tmp2 = ", ".join([ "\\textbf{" + x + "}"
                               if x == taskmap[md["ProducingtaskMain"]]
                               else x for x in tmp])
            # print tmp2
            md["ProducingtaskString"] = tmp2
        
def analyzeWPs (tree, verbose=False):

    global allWPDicts, allMilestones, allDeliverables, allTasks, allEfforts

    
    for wp in tree.getchildren():
        # look at each wp individually
        # print wp
        wpDict = dictFromXML(wp)
        allWPDicts.append(wpDict)
        
        # analyze tasks
        tasks = wp.findall("task")
        # print tasks
        tasknumber = 0
        previousWP = ""
        tasknumberssofar = {}
        for t in tasks:
            taskDict = dictFromXML (t)
            taskDict["wp"]= wpDict["Number"]

            # let's generate the tasknumbers
            # fairly complicated because we have to support the multiple phases 
            if not previousWP == taskDict["wp"]:
                tasknumber = 1
                tasknumberssofar = {}
                previousWP = taskDict["wp"]

            if taskDict["Label"] in tasknumberssofar:
                taskDict["tasknumber"] = tasknumberssofar[taskDict["Label"]]
            else:
                tasknumberssofar[taskDict["Label"]] = tasknumber
                taskDict["tasknumber"] = tasknumber
                tasknumber += 1 

            taskDict["taskId"] = "T\," + str(taskDict["wp"]) + "." + str(taskDict["tasknumber"])
            
            # make some as integer:
            taskDict["Duration"] = int(taskDict["Duration"])
            taskDict["Start"] = int(taskDict["Start"])
            
            allTasks.append(taskDict)

            
        # analye effort
        partners = wp.findall("partner")
        for p in partners:
            partnerId = p.attrib['id']
            # print partnerId
            for task in p.findall("taskeffort"):
                # print task.find("task").text
                # print task.find("resources").text

                allEfforts.append({"partner": partnerId, "task": task.find("task").text.strip(),
                                   "resources": task.find("resources").text.strip(),
                                   "wp": wpDict["Number"]})
            

        # analyze milestones
        milestones = wp.findall("milestone")
        for t in milestones:
            thisdict = dictFromXMLWithMains (t)
            thisdict ["wp"]= wpDict["Number"]

            # make some as integer:
            thisdict["Monthdue"] = int(thisdict["Monthdue"])
            allMilestones.append(thisdict)


        # analyze deliverables
        deliverables = wp.findall("deliverable")
        for t in deliverables:
            thisdict = dictFromXMLWithMains (t)
            thisdict ["wp"]= wpDict["Number"]

            # make some as integer:
            thisdict["Monthdue"] = int(thisdict["Monthdue"])
            allDeliverables.append(thisdict)


    fixProducingTask (allMilestones) 
    fixProducingTask (allDeliverables) 

        
def analyzeTree(tree, verbose=False):
    """Take an XML tree and create all the necessary data structures"""
    global titlepageDict
    global partnerList 

    # titlepage 
    titlepageDict = dictFromXML (tree)

    # partners
    allpartnersNode = tree.find ("allpartners")
    partnerList = analyzePartners (allpartnersNode)

    # workpackages
    allWPsNode = tree.find ("workpackages")
    analyzeWPs (allWPsNode, verbose)

########################################
## 

def generateTemplatesBuildListResult (templ, listtoworkon, keytosave, expandedresults ):

    t = Template(templ["template"])
    
    substitutedValues = [(t.substitute(x), x) for x in listtoworkon]
    
    if templ.has_key("joiner"):
        exp = templ["joiner"].join([x[0]  for x in substitutedValues])
        expandedresults[keytosave] = exp
    else:
        if templ.has_key("numerator"):
            i = 0
            for substitutedText, value in substitutedValues:
                expandedresults[keytosave+"-"+str(eval(templ["numerator"]))] = substitutedText
                i +=1 
        else:
            expandedresults[keytosave] = [x[0]  for x in substitutedValues]

    return expandedresults 

def generateTemplates(config, verbose):
    from templates import templates as templates

    global titlepageDict, partnerList 
    global allWPDicts, allMilestones, allDeliverables, allTasks, allEfforts

    # pp(templates)

    expanded = {}
    
    for templ in templates:
        if templ.has_key("dict"):
            # dealing with a dictionary is quite straightforward. 
            t = Template(templ["template"])
            exp =  t.substitute (eval(templ["dict"]))
            expanded[templ["label"]] = exp
        elif templ.has_key("list"):
            # dealing with a list argument is more complex, since it can be grouped
            # listresult = [t.substitute(x) for x in ]
            if templ.has_key ("groupby"):
                # groupby must be a key in the directory contained in the list
                # print eval(templ["list"])
                groups = set ([x[templ["groupby"]] for x in eval(templ["list"])])
                # print groups
                for g in groups:
                    listtoworkon = [x for x in eval(templ["list"]) if x[templ["groupby"]] == g]
                    expanded = generateTemplatesBuildListResult (templ,
                                                                 listtoworkon,
                                                                 templ["label"] + "-group" + g,
                                                                 expanded)
                    # expanded[templ["label"]] = groupresult
            else:
                expanded = generateTemplatesBuildListResult (templ,
                                                             eval(templ["list"]),
                                                             templ["label"], expanded) 

        # write this entry to file?
        if templ.has_key("file"):
            if templ["file"] == True:
                if templ.has_key("dir"):
                    filename = config.get("PathNames",
                                          "genlatex" + templ["dir"] + "path")
                else:
                    filename = config.get ("PathNames",
                                           "genlatexpath")
                filename = os.path.join (filename, templ["label"])
                # print filename
                
                if templ.has_key("groupby"):
                    for g in groups:
                        fn = filename + "-group-" + g + ".tex"
                        # print fn
                        key = templ["label"] + "-group" + g
                        # print key 
                        # print expanded[key]
                        utils.writefile (expanded[key], fn)
                else:
                    utils.writefile (expanded[templ["label"]], filename +".tex")
    pp(expanded)

#########################################
    
def computeStatistics (verbose):
    """Embellish the global lists with some additional sums, statistics,
    cross-referencing to IDs, etc. Add whatever seems useful here, makes
    it later to generate the LaTeX strings later on."""

    global titlepageDict, partnerList 
    global allWPDicts, allMilestones, allDeliverables, allTasks, allEfforts


    # What can we compute about WPs?
    for wp in allWPDicts:
        wp['wpeffort'] = str(sum([int(e['resources'])
                                  for e in allEfforts if e['wp'] == wp['Number']]))
        taskset = set([task['Label'] for task in allTasks if task['wp'] == wp['Number']])
        wp['taskeffort'] = dict([ (t, sum([int(te['resources'])
                                           for te in allEfforts if te['task'] == t]))
                                  for t in taskset ] )
        
        partnerset = set([te['partner'] for te in allEfforts if te['wp'] == wp['Number'] and int(te['resources']) > 0])
        wp['partnereffort'] = dict([ (p, sum([int(te['resources'])
                                              for te in allEfforts
                                              if te['partner'] == p and te['wp'] == wp['Number'] and int(te['resources']) > 0]))
                                     for p in partnerset ] )

        wp['End'] = int(wp['Start']) + int(wp['Duration'])

        wp['Leadernumber'] = [p['Number'] for p in partnerList if p['Shortname'] == wp['Leadership']][0]
    return 

########################################
if __name__ == '__main__':
    import sys

    from optparse import OptionParser
    parser = OptionParser("Read the project XML files and produce LaTeX, figures, etc.")
    parser.add_option ("-s", "--settings", dest="settingsfile",
                       help="the settings file")
    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="print lot's of debugging information",
                       action="store_true", default=False)
    (options, args) = parser.parse_args()

    config = settings.getSettings(options.settingsfile)

    parser = wikiParser.wikiParserFactory (config)

    xmlMainFile = "main.xml"
    xmlExpandedFile  = "main_expanded.xml"

    ## expand the include commands 
    utils.expandInclude (config.get("PathNames", "xmlpath"),
                         xmlMainFile,
                         xmlExpandedFile)
    
    ## read in the expanded XML file into a tree structure
    tree = ElementTree()
    tree.parse(os.path.join(config.get("PathNames", "xmlpath"),
                            xmlExpandedFile))
    if options.verbose and False:
        # dump on tree does not seem to support utf-8, so we use write here 
        tree.write (sys.stdout, encoding="utf-8")

    # create internal datastructures
    analyzeTree (tree.getroot(), options.verbose)

    computeStatistics (options.verbose)
    
    if options.verbose:
        pp(titlepageDict)
        pp(allWPDicts)
        pp(allTasks)
        pp(allMilestones)
        pp(allDeliverables)
        pp(allEfforts)
        pp(partnerList) 

    ## pp (allEfforts)
    ## pp(allWPDicts)
    ## newWP = [x.update({'effort': str(sum([int(e['resources']) for e in allEfforts if e['wp'] == x['Number']]))}) for x in allWPDicts]
    ## pp(newWP)
    ## pp ([  dict (x, **{'effort': str(sum([int(e['resources']) for e in allEfforts if e['wp'] == x['Number']]))})
    ##        for x in allWPDicts]) 

    # pp ([ dict (e, **{'blabla': 17}) for e in allEfforts])
    
    generateTemplates (config, options.verbose)
    
    ## let's try this iterator idea

    ## iterator = "[x['Shortname'] for x in partnerList]"
    ## rowtemplate = "${Name} & ${Nation} & ${Type}"
    
    ## for i in eval(iterator):
    ##     print i
    ##     # print rowtemplate.substitute(partnerList[i])

    ## wpgrouper = "[x['Number'] for x in allWPDicts]"
    ## deltemplate = Template("""Name: ${Title} Month Due: ${Monthdue}""")
    ## delpick = "[a for a in allDeliverables if a['wp']==i]"
    ## deljoiner = "\\\\ \n"
    ## for i in eval(wpgrouper):
    ##     print i
    ##     print deljoiner.join([deltemplate.substitute(x) for x in eval(delpick)])
    ##     ## for x in eval(delpick):
    ##     ##     print 

    ## print "".join([str(x)  for x in [{"Name": 5, "Monthdue": 17}]])
    ## print "".join([deltemplate.substitute(x)  for x in [eval('{"Title": 5, "Monthdue": 17}')]])
    ## print deltemplate.substitute(eval('{"Title": 5, "Monthdue": 17}'))
