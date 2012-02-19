#!/usr/bin/python

"""general docu for latexFromXML"""

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
"""A list storing one directory per workpackage. Filled from XML file. Fields of this directory are:
"""

allMilestones = []
allDeliverables = []
allTasks = []
allEfforts = []
partnerList = []
titlepageDict = {}
""" Dictionary containing all information about the project in general; mostly it goes on the titlepage."""

expanded = {}

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


###############
# produce the LaTeX options 
def processLaTeX (config):
    t = ""
    if config.getboolean('LaTeX', 'showCommissionHints'):
        t += "% commissionHints command unchanged to have them included\n"
    else:
        t += "\\renewcommand{\commissionhints}[1]{}\n"

    
    if config.getboolean('LaTeX', 'useShowkeys'):
        t += "\\usepackage{showkeys}\n"
    else:
        t += "% showkeys not used \n"

    ## make all boolean variables directly available as toggles in LaTeX:

    for s in config.sections():
        if not s == "CustomLaTeX": 
            for k in config.options(s):
                # print k 
                try:
                    v = config.getboolean (s,k)
                    if v:
                        t +="\\newboolean{" + s + "-" + k + "}\n" + "\\setboolean{" + s + "-" + k + "}{true}\n"
                    else:
                        t +="\\newboolean{" + s + "-" + k + "}\n" + "\\setboolean{" + s + "-" + k + "}{false}\n"
                except ValueError:
                    pass

    ## and put all the entries in CustomLaTeX 
    if config.has_section('CustomLaTeX'):
        for o in config.options('CustomLaTeX'):
            c =  config.get('CustomLaTeX', o)
            # print c 
            r = eval(c)
            # print r
            # print r"\newcommand{" + o + "}{" + str(r) + "}\n"
            t += "\\newcommand{\\" + o + "}{" + str(r) + "}\n"
        
    
    utils.writefile (t, os.path.join(config.get('PathNames', 'genlatexpath'),
                               "settings.tex"))
    
##############################################################

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

        # create milestone ids
        currentWP = "" 
        for m in allMilestones:
            if not m['wp'] == currentWP:
                currentWP = m['wp']
                count = 1
            m['id'] = 'M\,' + currentWP +"." + str(count)
            count += 1 

        # analyze deliverables
        deliverables = wp.findall("deliverable")
        for t in deliverables:
            thisdict = dictFromXMLWithMains (t)
            thisdict ["wp"]= wpDict["Number"]

            # make some as integer:
            thisdict["Monthdue"] = int(thisdict["Monthdue"])
            allDeliverables.append(thisdict)

        currentWP = "" 
        for m in allDeliverables:
            if not m['wp'] == currentWP:
                currentWP = m['wp']
                count = 1
            m['id'] = 'D\,' + currentWP +"." + str(count)
            count += 1 


        # produce the wp header
        
        
    fixProducingTask (allMilestones) 
    fixProducingTask (allDeliverables)

    # put any additional information into the task strings

    for t in allTasks:
        t['contributedDeliverables'] = [d['Label'] for d in allDeliverables if t['Label'] in d['Producingtask'] ]
        t['contributedMilestones'] = [d['Label'] for d in allMilestones if t['Label'] in d['Producingtask'] ]

    # make sure all tasks and all partners show up in allEfforts:
    for t in allTasks:
        for p in partnerList:
            if not [e for e in allEfforts if e['partner'] == p['Shortname'] and
                    e['task'] == t['Label']]:
                allEfforts.append ({"partner": p['Shortname'],
                                    "task": t['Label'],
                                    "resources": '0',
                                    "wp": t['wp']})

    # pp (allTasks) 


###############################################################################################################
####    GANTT HANDLING
###############################################################################################################


def produceUncompressedGantt (l, config):
    """produce a Gantt string for the elements in list, without trying to
    compress that into a complact representation. Each element a separate line."""
    return "\\\\ \n".join(["\\ganttmilestone" + e['deco'] + "{"+ e['id'] + '}{' \
                           + str(e['Monthdue']) + "}" for e in l    ])
    
def produceCompressedGantt (l, config):
    # sort by date first:
    # note: a bit complex, let's assure that when there are several ones on the same date, they appear
    # in order of their id. Irrespective of whether they belong to the same WP (TODO: should this be made
    # an option to choose that "own" items come first? -- Makes little sense 
    inputlist = sorted(l, key=lambda x: int(x['Monthdue']))

    maxNumLines = len(inputlist)
    projectDuration = int(titlepageDict["duration"])

    occupancyMatrix = [[False for i in range(projectDuration+1)] for j in range(maxNumLines)]
    resultLists = [[] for j in range(maxNumLines)]

    for entry in inputlist:
        # search the first line where the month of this entry is not yet occupied
        line = 0
        while occupancyMatrix[line][int(entry['Monthdue'])] == True:
            line += 1

        # put this entry in the lineth line: 
        resultLists[line].append(entry)

        for m in range(int(entry['Monthdue']), \
                       min(int(projectDuration)+1,
                           int(entry['Monthdue'])+int(config.get ("Gantts", 'ganttDistanceBetweenMS')))):
            occupancyMatrix[line][m] = True

    return "\\\\ \n".join([ "\n".join([ "\\ganttmilestone" + e['deco'] + "{"+ e['id'] + '}{' + str(e['Monthdue']) + "}" for e in line])
                     for line in resultLists if line])


    
def computeGanttStrings (config):
    global titlepageDict, partnerList, expanded 
    global allWPDicts, allMilestones, allDeliverables, allTasks, allEfforts

    for wp in allWPDicts:

        # print "WP: ", wp['Number']
        # the actual gantt chart, spearately for task bars, the deliverables, and the milestones.
        # also a combined deliverables/milestones string 
        # enables easy mix and match 

        # construct the relevant milestone, deliverable list
        # question is whether to incorporate also the cross-WP
        # milestones/deliverables; this is configurable option

        # print "milestones WITH cross-WP milestones, as arrays:"
        milestoneList = [x for x in allMilestones
                         if x['wp'] == wp['Number'] or
                         ( config.getboolean ("Gantts", "milestonesShowCrossWP") and 
                           utils.treeReduce ([[task['wp'] == wp['Number'] for task in allTasks if task['Label'] ==contribTask ]
                                              for contribTask in x['Producingtask']],
                                             lambda a, b: a or b)
                           )]
        for m in milestoneList:
            m["deco"] = "[milestone={" + config.get ("Gantts", "milestoneDecoration") + "}]" 
            
        wp["milestoneGanttString"] = produceCompressedGantt (milestoneList, config)
        wp["milestoneUncompressedGanttString"] = produceUncompressedGantt (milestoneList, config)
        wp["milestoneInGantt"] = [m["Label"] for m in milestoneList]
        wp["milestoneGanttLegend"] = "\n".join([Template(config.get("Gantts","milestoneLegendTemplate")).substitute(x) for x in milestoneList])
        
        deliverableList = [x for x in allDeliverables
                           if x['wp'] == wp['Number'] or
                           ( config.getboolean ("Gantts", "deliverablesShowCrossWP") and 
                             utils.treeReduce ([[task['wp'] == wp['Number'] for task in allTasks if task['Label'] ==contribTask ]
                                                for contribTask in x['Producingtask']],
                                               lambda a, b: a or b)
                             )]

        for d in deliverableList:
            d["deco"] = ""
            
        wp["deliverableGanttString"] = produceCompressedGantt (deliverableList, config)
        wp["deliverableUncompressedGanttString"] = produceUncompressedGantt (deliverableList, config)
        wp["deliverableInGantt"] = [d["Label"] for d in deliverableList]
        wp["deliverableGanttLegend"] = "\n".join([Template(config.get("Gantts","deliverableLegendTemplate")).substitute(x) for x in deliverableList])

        
        ########################
        # the groupbar for a WP is fairly simple:
        wp["groupbar"] = r"\ganttgroup{}{" + wp['Start'] +  "}{" \
                         + str(int(wp["Start"]) + int(wp['Duration']) - 1) + r"} \\"
        
        ########################
        # compute the taskbar gantt part
        # complicated by possibly multi-phased tasks
        wp["taskGantt"] = ""
        tasksofthiswp = set ([t['Label'] for t in allTasks if t['wp'] == wp['Number']])
        # make sure we iterate over these tasks in the right order (Damm, these phased tasks
        # create so many problems :-(

        # pp(allTasks)
        # pp(tasksofthiswp)
        for tasklabel in sorted(tasksofthiswp,
                                key=lambda x:
                                [t['taskId'] for t in allTasks if t['Label']==x][0]):
            # print tasklabel
            phases = sorted ([t for t in allTasks if t['Label'] == tasklabel],
                            key=lambda x: x['Start'])

            for i,t in enumerate (phases):
                taskganttid = "T" + t["wp"] + "-" + str(t["tasknumber"])
                # print taskganttid
                t["ganttid"] = taskganttid
                if i==0:
                    thistaskgantt = "\\ganttbar[name="+ taskganttid  + "-" + str(i) + \
                                         "]{" + t['taskId'] + \
                                         ((": " + t['Name']) if
                                          config.getboolean('Gantts', 'ganttTaskbarsShowTaskname')
                                          else "" ) +  \
                                          "}{"+ str(t['Start']) + "}{" + str(t['Start']+t['Duration']-1) + "} \\\\  \n"
                else:
                    thistaskgantt += "\\ganttbar[name="+ taskganttid  + "-" + str(i)+ \
                                     "]{" + t['taskId'] + \
                                     ((" (Phase " + str(i+1) + ")") if
                                      config.getboolean('Gantts', 'ganttTaskbarsShowTaskname')
                                      else "(" +  str(i+1)+ ")")  + \
                                     "}{"+ str(t['Start']) + "}{" + str(t['Start']+t['Duration']-1) + "} \\\\  \n"
                    thistaskgantt += "\\ganttlink[link type=F-S]{" + taskganttid + "-" + str(i-1) + "}{" + \
                                     taskganttid + "-" + str(i) + "}\n" 
                    
            # print thistaskgantt
            wp["taskGantt"] += thistaskgantt
        wp["taskGantt"] = wp["taskGantt"].strip("\n")


    #####
    ## Gantt Legend strings for deliverables and milestones

    for d in allDeliverables:
        d['ganttLegend'] = Template(config.get("Gantts",
                                               "deliverableLegendTemplate")).substitute(d)
    for ms in allMilestones:
        ms['ganttLegend'] = Template(config.get("Gantts","milestoneLegendTemplate")).substitute(ms)

    return 

################################################
def computeWPTable (config):
    global titlepageDict, partnerList, expanded 
    global allWPDicts, allMilestones, allDeliverables, allTasks, allEfforts

    maxPartnerPerRow = config.getint('WPTables', 'maxPartnersPerRow')
    firstColumn = config.getint ('WPTables', 'firstColumnWidth')
    otherColumns = config.getfloat ('WPTables', 'tabularCorrection')*(100.0-firstColumn) / maxPartnerPerRow /100.0

    for wp in allWPDicts:
        t = r"\begin{tabular}"

        t += r"{|p{0.%d\textwidth}" % firstColumn 
        t += ("|" + config.get('WPTables', 'wptablespacing') +
              r"p{%f\textwidth}" % otherColumns + \
              config.get('WPTables', 'wptablespacing'))  \
              * maxPartnerPerRow
        t += "|} \n \\hline"

        # which WP?
        t += r'\textbf{Workpackage no.} & \multicolumn{1}{c|}{%s} & \multicolumn{%d}{l|}{\textbf{Start date:} M %s} \\ \hline ' % (wp['Number'], maxPartnerPerRow-1, wp['Start'])
        t += "\n"
        t += r'\textbf{Title} & \multicolumn{%d}{l|}{%s} \\ \hline' % (maxPartnerPerRow,
                                                                       wp['Name'])
        t += r'\textbf{Activity type} & \multicolumn{%d}{l|}{%s \hfill} \\ \hline ' % (maxPartnerPerRow,
                                                                                wp['Type'])
        t += "\n"

        # build the partner lists
        numPartners = len(partnerList)
        printedPartners = 0
        while printedPartners < numPartners:
            fromPartner = printedPartners +1
            toPartner = fromPartner + min(maxPartnerPerRow, numPartners-printedPartners)-1
            # print fromPartner, toPartner

            t1 = "Part.\ no.\ "
            t2 = "Short name "
            t3 = "Effort "
            
            for i in range (fromPartner, fromPartner + maxPartnerPerRow):
                # print i
                if i <= toPartner:
                    shortname = [x['Shortname'] for x in partnerList
                                 if i == int(x['Number'])][0]
                    try: 
                        thiseffort = wp['partnereffort'][shortname]
                    except KeyError:
                        thiseffort = 0

                    inactiveLighter = lambda x: x if thiseffort > 0 else \
                                     r'\textcolor{%s}{%s}' % (config.get('WPTables',
                                                                       'colorInactivePartner'),
                                                             str(x))
                    wpHighligher = lambda x: inactiveLighter(x) if not wp['Leadership'] == shortname else \
                                   r'\textbf{%s}' % inactiveLighter(x)

                    centerer = lambda x: "\centering{%s}" % wpHighligher(x)
                    t1 += " & " + centerer(str(i)) 
                    t2 += " & " + centerer(shortname) 
                    t3 += " & " + centerer(str(thiseffort))
                else:
                    t1 += " & "
                    t2 += " & "
                    t3 += " & "
            t += t1 + r'\\ \hline ' + "\n" + t2 + r'\\ \hline ' + "\n" + t3 + r'\\ \hline ' + "\n"
            printedPartners = toPartner

        t += r'\end{tabular}'
        wp['tableheader'] = t
        # pp(wp)

###############################################

def analyzeTree(tree, config, verbose=False):
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

    # compute the gantt chart entries 
    computeGanttStrings (config)


########################################
## use the templates to generate latex text 

class recursiveTemplate(Template):
    """ try to find recursively occuring patterns and replace them first"""
    def substitute (self, d):
        # print "REC"
        tmp = self.template
        # print "template before RE: ", tmp
        tmp = re.sub (r'\${([_a-zA-Z][_a-zA-Z0-9]*)_(\${([_a-zA-Z][_a-zA-Z0-9]*)})}',
                lambda m: "${" + m.group(1) + "_" + d[m.group(3)] +"}",
                tmp)
        # print "template after RE: ", tmp
        # pp(d)
        ts = Template(tmp)
        substituted =  ts.substitute (d)
        # print substituted 
        # print re.findall (r'%{(.*?)}', substituted)
        ## print "----"
        ## print substituted
        ## m = re.search (r'%{(.*?)%}', substituted)
        ## if m:
        ##     print m.group(1)
        ##     print eval(m.group(1))
        executed = re.sub (r'%{(.*?)%}',
                           lambda m: eval(m.group(1)),
                           substituted,
                           flags=re.DOTALL)
        ## print executed 
        return executed 

def generateTemplatesBuildListResult (templ, listtoworkon, 
                                      keytosave, expandedresults):

        
    if templ.has_key ("dict"):
        dicttouse = eval(templ["dict"])
    else:
        dicttouse = None 

    if templ["template"]:
        ## print "--------------"
        ## print templ["template"]
        t = recursiveTemplate(templ["template"])
        ## print t.template
        # print "keytosave: ", keytosave
        if dicttouse:
            ## print "--------------"
            # pp(dicttouse)
            # pp (listtoworkon)
            substitutedValues = [ ((t.substitute(dict (dicttouse, **x)), x) if isinstance (x, dict)
                                   else (t.substitute(dict (dicttouse, **{"Listelement": x})), x))
            for x in listtoworkon]
        else:
            substitutedValues = [(t.substitute(x), x) for x in listtoworkon]
    else:
        substitutedValues = [ (x, None) for x in listtoworkon]
    
    if templ.has_key("joiner"):
        # little nastiness: newline characters are not interpreted as such from cfg file
        templ["joiner"] = re.sub(r'\\n', '\n', templ["joiner"])
        if templ.has_key("sorter"):
            tmp = sorted(substitutedValues,
                         key = lambda y: ((eval(templ['sorter']))(y[1])))
            exp = (templ["joiner"]).join([x[0] for x in tmp])
            # print exp
        else:
            exp = (templ["joiner"]).join([x[0]  for x in substitutedValues])
        expandedresults[keytosave] = exp.strip()
        writeTemplateResult (expandedresults, templ, keytosave) 
    else:
        if templ.has_key("numerator"):
            i = 0
            for substitutedText, value in substitutedValues:
                keytosave2 = keytosave+"_"+str(eval(templ["numerator"]))
                expandedresults[keytosave2] = substitutedText.strip()
                writeTemplateResult (expandedresults, templ, keytosave2) 
                i +=1 
        else:
            expandedresults[keytosave] = [x[0].strip()  for x in substitutedValues]
            writeTemplateResult (expandedresults, templ, keytosave) 

    return expandedresults 

def generateTemplates(config, verbose):

    global titlepageDict, partnerList, expanded 
    global allWPDicts, allMilestones, allDeliverables, allTasks, allEfforts


    # pp(templates)

    templateParser = settings.getSettings(config.get("PathNames",
                                                     "latexTemplates"))


    expanded = {}
    
    for templsection in templateParser.sections():
        # print templsection
        templ = templateParser._sections[templsection]
        # pp (templ)
        templ["label"] = templsection
        if not templ.has_key("list"):
            if templ.has_key("dict"):
                # dealing with a dictionary is quite straightforward. 
                t = recursiveTemplate(templ["template"])
                exp =  t.substitute (eval(templ["dict"]))
                expanded[templ["label"]] = exp.strip()
            else:
                # print "Template " + templ["label"] + " has neither dict not list; makes no sense."
                # pp(templ)
                # pp(templ['template'])
                expanded[templ["label"]] = templ["template"].strip()
            writeTemplateResult (expanded, templ) 
        else:
            # do we ALSO have a dict to use or substitution keys?
            # dealing with a list argument is more complex, since it can be grouped
            # listresult = [t.substitute(x) for x in ]
            if templ.has_key ("groupby"):
                # groupby must be a key in the directory contained in the list
                # print templ['list']
                # print eval(templ["list"])
                groups = set ([x[templ["groupby"]] for x in eval(templ["list"])])
                # print groups
                for g in groups:
                    listtoworkon = [x for x in eval(templ["list"]) if x[templ["groupby"]] == g]
                    expanded = generateTemplatesBuildListResult (templ,
                                                                 listtoworkon,
                                                                 templ["label"] + "_" + g,
                                                                 expanded)
            else:
                expanded = generateTemplatesBuildListResult (templ,
                                                             eval(templ["list"]),
                                                             templ["label"],
                                                             expanded) 




def writeTemplateResult (expanded, templ, keytouse = None):
    """Use the information in templ to check whether it should be written out"""

    if not keytouse:
        keytouse = templ["label"]

    # should we write a toggle around the latex code?
    # yes, if there is a correspoding filed in config
    # TODO - this is complicated since the keytouse typically has suffixes for workpackages!!
    ## toggle = False
    ## toggleSection = "" 
    ## for s in config.sections():
    ##     try:
    ##         config.getboolean(s, keytouse)
    ##         toggle = True
    ##         toggleSection = s
    ##         break 
    ##     except:
    ##         pass
        
    ## print keytouse, toggle, toggleSection 


    # write this entry to file?
    if templ.has_key("file"):
        if templ["file"] == 'True':

            if templ.has_key("dir"):
                filename = config.get("PathNames",
                                      "genlatex" + templ["dir"] + "path")
            else:
                filename = config.get ("PathNames",
                                       "genlatexpath")

            filename = os.path.join (filename, keytouse)
            filename += ".tex"
            # print "filename: ", filename
            # print "content: ", pp(expanded[keytouse])
            utils.writefile (expanded[keytouse], filename)

    
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
                                              if te['partner'] == p and
                                              te['wp'] == wp['Number'] and int(te['resources']) > 0]))
                                     for p in partnerset ] )
        # make sure that every partner is mentioned in partnereffort, with 0 if no effort
        for p in partnerList:
            if not wp['partnereffort'].has_key(p['Shortname']):
                wp['partnereffort'][p['Shortname']] = 0
            

        wp['End'] = int(wp['Start']) + int(wp['Duration']) - 1 

        wp['Leadernumber'] = [p['Number'] for p in partnerList if p['Shortname'] == wp['Leadership']][0]
    return 


def generatePartnerDescriptions(config, verbose):
    t = ""
    for p in partnerList:
        # print p
        t += r"\subsection{" + p['Name'] + " (" + p['Shortname'] + ")}\n"
        t += r"\label{partner:" + p['Shortname'] +"}\n"
        t += "\\input{partners/" + p["Wiki"] + ".tex}\n"
        t += r"\ifthenelse{\boolean{Participants-newpageAfterEachPartner}}{\newpage}{}"

    utils.writefile (t, 
                     os.path.join(config.get('PathNames', 'genlatexpartnerspath'),
                                  'partnersIncluder.tex'))

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
    analyzeTree (tree.getroot(), config, options.verbose)

    computeStatistics (options.verbose)

    # compute the WP table as far as necessary; try to delegate as much as possible
    # to the templating engine
    computeWPTable (config) 

    generatePartnerDescriptions (config, options.verbose)
    
    
    generateTemplates (config, options.verbose)

    processLaTeX (config) 

    if options.verbose:
        print "titlepage" 
        pp(titlepageDict)
        print "allWPDicts"
        pp(allWPDicts)
        print "allTasks"
        pp(allTasks)
        print "allMilestones"
        pp(allMilestones)
        print "allDeliverables"
        pp(allDeliverables)
        print "allEfforts"
        pp(allEfforts)
        print "partnerList"
        pp(partnerList)
        print "expanded"
        pp (expanded) 


## pp( utils.roundPie(utils.mapReduce ([   (utils.searchListOfDicts(partnerList,
##                                                                  'Shortname',
##                                                                  e['partner'],
##                                                                  'Nation'),
##                                          int(e['resources']))
##                                         for e in allEfforts],
##                                     lambda a,b: a+b))
##     )
