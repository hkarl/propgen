#!/usr/bin/python

"""This script reads in the XML files describing the project and
generates the LaTeX output. To this end, it uses a couple of steps:

   1. Analze the entire XML tree and put the content into the global
   variables allWPDicts, allMilestones, allDeliverables, allTasks,
   allEfforts, partnerList and titlepageDict. This is triggered by the
   analyzeTree function. 

   2. Statistics are computed - computeStatistics
   
   3. The tables for the WP are generated - computeWPTable 

   4. The partner descriptions are generated - generatePartnerDescriptions

   5. The templates from latexTemplates.cfg are processed; this is the
      main step for all the details of LaTeX producting - generateTemplates

   6. Finally, LaTeX options in settings.cfg - processLaTeX

Details from where files are read and where files are put are
controlled by settings.cfg. 
"""

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
"""A list storing one dictionary per workpackage. Filled from XML
file. Some additions computed. 
"""

allMilestones = []
"""A list storing one dictionary per milestone. Filled in from XML
file, with some additions. """

allDeliverables = []
"""A list storing one dictionary per deliverable. Filled in from XML
file, with some additions. """

allTasks = []
"""A list storing one dictionary per task. Collected from all the
tasks in all the workpackage pages. Some additions computed. """

allEfforts = []
"""A list containing a dictionary per task/partner
combination. Extracted from the effort tables on the Wiki."""

partnerList = []
"""A list storing one dictionary per partner."""

titlepageDict = utils.documentedDict()
""" Dictionary containing all information about the project in
general; mostly it goes on the titlepage. It directly obtains its
content from the main project wiki page, without any additions
computed here.
"""

expanded = utils.documentedDict()
"""This dictionary collects all the expansions of templates from
latexTemplate.cfg. Like all the other ones, it can be used as an
argument to the dict option therein, allowing to build templates that
use the expansions of simpler templates as variables.
"""

def stripped(text=None):
    return "<empty>" if text is None else text.strip()

def errorMsg(tree):
    print "Something was left empty in %s '%s'" % (tree.tag,tree.text)
    for x in tree.getchildren():
        print "| %s | %s | %s |" % (stripped(x.tag),stripped(x.text),x.attrib)
    print
    raise SystemExit

def dictFromXML (tree):
    """Given an XML node (obtained via the xml.etree.ElementTree
    libary, build a dictionary where the keys are the tag of a child
    node and the text attribute of the child node is the value. Return
    this dictionary."""

    try:
        return utils.documentedDict ([(x.tag.strip(), x.text.strip()) for x in tree.getchildren()])
    except:
        errorMsg(tree)

def dictFromXMLWithMains (tree):
    """Similar to dictFromXML, but this function in addition
    understands an XML-attribute main. This is used to differentiate,
    e.g., between lead contributor and non-lead contributors of a
    task; or to differentiate between a main producing task for a
    deliverable and an ordinary task. This XML attributes are
    generated based on boldface markup in generateXML; see function
    singleWorkpackageXML in generateXML.py. If such a key is found in
    the XML atribute, a corresponding entry is put into the dictionary
    that is to be generated from this XML subtree.

    Example: Milestone dicts have a key Contributor, which has a list
    of partner shortnames. A milestone also *might* have a key
    ContributorMain, which is a partner shortname string, specifying
    a potential lead partner for this milestone.
    """
    d = utils.documentedDict()
    try:
        ll = [(x.tag.strip(), x.text.strip(), x.attrib) for x in tree.getchildren()]
    except:
        errorMsg(tree)

    for l in ll:
        tag = l[0]
        val = l[1]
        attrib = l[2]
        hasMain = False

        if tag in d:
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
                d.keydoc  = "A main key for the acutal key " + tag
            else:
                d[tag+"Main"] = ""

        if hasMain:
            # TODO: add sorting order here
            # it doesnt make a lot of sense for all things, but useful nonetheless
            d[tag+"String"] = ", ".join([ "\\textbf{" + x + "}" if x == d[tag+"Main"]
                                          else x for x in sorted(d[tag])])
            # print "adding " + tag + " to dictionary"
            d.keydoc = """Since key %s has a main attribute, we
            add here a key that contains a string
            concatening the list of individual entries, marking the
            main entry in boldface."""  % tag
    return d


###############
# produce the LaTeX options 
def processLaTeX (config):
    """Process the LaTeX-relevant sections of settings.cfg, turn the options
    therein into LaTeX commands. Some of them need specific processing
    (like showCommissionHints), others evaluate a LaTeX expression,
    others simply generate a boolean variable for the switches in settings.cfg. 
    """
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
    """Produce the partnerList dictionaries, containing all partner
    descriptions, from the correspndng part of the XML tree."""
    
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
        if "Producingtask" in md:
            tmp = sorted([taskmap[x] for x in md["Producingtask"]])
            # print tmp
            tmp2 = ", ".join([ "\\textbf{" + x + "}"
                               if x == taskmap[md["ProducingtaskMain"]]
                               else x for x in tmp])
            # print tmp2
            md["ProducingtaskString"] = tmp2
            # print "adding producingtaskString" 
            md.keydoc = """A string that contains all the tasks
            producing this milestone or deliverable; with a possible
            main contributor set in boldface."""
            
def analyzeWPs (tree, verbose=False):
    """Given an XML tree pointing to a WP, extract all the information
    from it and build the global variables describing this WP. """
    
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
                taskDict.keydoc = """Constructed tasknumber, makes
                sure that a multiple phase task only gets one number,
                consequetively increasing in a WP, ordered in the same
                order as the tasks appear on the WP's wiki page. If
                you want something like T 1.1, use taskId instead. """
                tasknumber += 1 

            taskDict["taskId"] = "T\," + str(taskDict["wp"]) + "." + str(taskDict["tasknumber"])
            taskDict.keydoc = """Based on the tasknumber, construct a
            readbable number for this task. """
            
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
                d = utils.documentedDict()

                d["partner"] = partnerId
                d.keydoc = """The partner shortname of the partner
                organization the effort of which is described here. """
                
                d["task"] = task.find("task").text.strip()
                d.keydoc = """The task label which identifies this
                task."""
                
                d["resources"] = task.find("resources").text.strip()
                d.keydoc = """The resources which this partner has in
                this task."""
                
                d["wp"] = wpDict["Number"]
                d.keydoc = """For simplicity, this field describes the
                number of the workpackage in which this task is
                hosted. Not strictly necessary, but makes a number of
                tests simpler later on."""

                allEfforts.append(d)
            

        # analyze milestones
        milestones = wp.findall("milestone")
        for t in milestones:
            thisdict = dictFromXMLWithMains (t)
            thisdict ["wp"]= wpDict["Number"]

            # make some as integer:
            thisdict["Monthdue"] = int(thisdict["Monthdue"])
            thisdict.keydoc = """Due dates are interpreted as being at
            the END of the given month. Relevant for correct placement
            of the markers in the Gantt charts."""
            allMilestones.append(thisdict)

        # create milestone ids
        currentWP = "" 
        for m in allMilestones:
            if not m['wp'] == currentWP:
                currentWP = m['wp']
                count = 1
            m['id'] = 'M\,' + currentWP +"." + str(count)
            m.keydoc = """Unique shortname for the milestone."""
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
        t['contributedDeliverables'] = [d['Label'] for d in
                                        allDeliverables if t['Label'] in d['Producingtask'] ]
        t.keydoc = """All the deliverables this task contributes to,
        using the label of the deliverable. A
        list; can be turned into a string by proper join operation. """
        t['contributedMilestones'] = [d['Label'] for d in allMilestones if t['Label'] in d['Producingtask'] ]
        t.keydoc = """All the milestones this task contributes to,
        using the label of the milestone. A
        list; can be turned into a string by proper join operation. """

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
    """Produce a Gantt chart where milestones and deliverables are
    packed in as few lines as possible, with horizontal separation
    being controlled by the corresponding setting in
    settings.cfg. Milestones/deliverables are sorted by their due
    date! If they should appear in some other order, change the first
    line in this function (computation of inputList). TODO: Thinky
    about making this a configurable option. """

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
    """Determine the actual gantt chart, spearately for task bars, the
    deliverables, and the milestones. This function computes various
    extensions for the main global variables (see key documentation). 
    Also a combined deliverables/milestones string 
    enables easy mix and match 

    construct the relevant milestone, deliverable list
    question is whether to incorporate also the cross-WP
    milestones/deliverables; this is configurable option"""

    global titlepageDict, partnerList, expanded 
    global allWPDicts, allMilestones, allDeliverables, allTasks, allEfforts

    for wp in allWPDicts:

        milestoneList = [x for x in allMilestones
                         if x['wp'] == wp['Number'] or
                         ( config.getboolean ("Gantts", "milestonesShowCrossWP") and 
                           utils.treeReduce ([[task['wp'] == wp['Number'] for task in allTasks if task['Label'] ==contribTask ]
                                              for contribTask in x['Producingtask']],
                                             lambda a, b: a or b)
                           )]
        for m in milestoneList:
            m["deco"] = "[milestone={" + config.get ("Gantts",
                         "milestoneDecoration") + "}]"
            m.keydoc = """A string to be passed to the pgfgantt
                         package, to make the milestones look
                         differently from the deliverables
                         markers. Controlled by the
                         milestoneDecoration option in settings.cfg."""
            
        wp["milestoneGanttString"] = produceCompressedGantt (milestoneList, config)
        wp.keydoc = """A LaTeX command string containing the
        commands to typeset the milestones of a particular WP (use
        pgfgantt commands). It is
        in compressed version, i.e., it tries to put milestones on
        as few lines as possible.""" 

        wp["milestoneUncompressedGanttString"] = produceUncompressedGantt (milestoneList, config)
        wp.keydoc = """A LaTeX command string containing the commands to typeset the
        milestones of a particular WP. This is in uncompressed form,
        i.e., each miilestone goes on a separate line."""
        
        wp["milestoneInGantt"] = [m["Label"] for m in milestoneList]
        wp.keydoc = """Which milestones (symbolic labels) appear in
        the Gantt chart of this WP? (This is NOT the same thing as the
        milestones hosted in a WP because of cross-WP milestones; this
        list might contain milestones of other WPs as well in case a
        task of this WP contributes to the milestone."""
        
        wp["milestoneGanttLegend"] = "\n".join([Template(config.get("Gantts","milestoneLegendTemplate")).safe_substitute(x) for x in milestoneList])
        wp.keydoc = """The part of the Gantt legend pertaining to the
        milestones. Its look is controlled by the
        milestoneLegendTemplate in settings.cfg."""
        
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
        wp.keydoc = "Compare the same corresponding key for milestones."

        wp["deliverableUncompressedGanttString"] = produceUncompressedGantt (deliverableList, config)
        wp.keydoc = "Compare the same corresponding key for milestones."

        wp["deliverableInGantt"] = [d["Label"] for d in deliverableList]
        wp.keydoc = "Compare the same corresponding key for milestones."

        wp["deliverableGanttLegend"] = "\n".join([Template(config.get("Gantts","deliverableLegendTemplate")).safe_substitute(x) for x in deliverableList])
        wp.keydoc = "Compare the same corresponding key for milestones."

        
        ########################
        # the groupbar for a WP is fairly simple:
        wp["groupbar"] = r"\ganttgroup{}{" + wp['Start'] +  "}{" \
                         + str(int(wp["Start"]) + int(wp['Duration']) - 1) + r"} \\"
        wp.keydoc = """In a horizontal bar is desired to separate WPs;
        this is a command for the pgfgantt package. """
        
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
                t.keydoc = """The string to typeset in the Gantt box
                of this task."""
                
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
        wp.keydoc = """A command for pgfgantt to set the task part of
            the WP's Gantt chart. This is in principle
            straightforward, but the requirement for multi-phase tasks
            makes it a bit complicated. """ 


    #####
    ## Gantt Legend strings for deliverables and milestones

    for d in allDeliverables:
        d['ganttLegend'] = Template(config.get("Gantts",
                                               "deliverableLegendTemplate")).safe_substitute(d)
        d.keydoc = """The string to be put into the legend of a Gantt
        chart for this deliverable. Controlled by the
        deliverableLegendTemplate option in settings.cfg. """

    for ms in allMilestones:
        ms['ganttLegend'] = Template(config.get("Gantts","milestoneLegendTemplate")).safe_substitute(ms)
        ms.keydoc = """The string to be put into the legend of a Gantt
        chart for this milestone. Controlled by the
        deliverableLegendTemplate option in settings.cfg. """

    return 

################################################
def computeWPTable (config):
    """For each WP in allWPDicts, compute the LaTeX string for the
    header of the workpackage table. The table header
    is fairly complex to stitch together and is done here instead of
    in the latexTemplates.cfg. 
    """
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

                    # this one stopped working at some time with misplaced aligns:
                    # centerer = lambda x: "\centering{%s}" % wpHighligher(x)
                    # tried the hackish alternative:
                    centerer = lambda x: "\hfill {%s} \hfill \\vadjust{}" % wpHighligher(x)
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
        wp.keydoc = """The WP table header block, with effort lines
        per partner. It is a complete tabular environment, ready to be
        used in a template section of latexTemplates.cfg."""


###############################################

def analyzeTree(tree, config, verbose=False):
    """Take an XML tree and create all the necessary data structures;
    just invokes various analyses functions."""
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
    """Try to find recursively occuring patterns and replace them first"""
    def substitute (self, d):
        # print "REC"
        tmp = self.template
        # print "template before RE: ", tmp
        tmp = re.sub (r'\${([_a-zA-Z][_a-zA-Z0-9]*)_(\${([_a-zA-Z][_a-zA-Z0-9]*)})}',
                lambda m: "${" + m.group(1) + "_" + d[m.group(3)] +"}",
                tmp)
        # print "======================================================================="
        # print "template after RE: ", tmp
        # pp(d)
        # print "======================================================================="
        ts = Template(tmp)
        substituted =  ts.safe_substitute (d)
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
    """Helper function to deal with lists in the template substition
    process. 
    """
        
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
            substitutedValues = [ ((t.safe_substitute(dict (dicttouse, **x)), x) if isinstance (x, dict)
                                   else (t.safe_substitute(dict (dicttouse, **{"Listelement": x})), x))
            for x in listtoworkon]
        else:
            substitutedValues = [(t.safe_substitute(x), x) for x in listtoworkon]
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
    """ This function processes the
    latexTemplates.cfg file. It goes over each section, expands the
    template option, considering the other options. The expansion of
    the template option is based on Python's string.Template
    expansion, with a few extras added in.

    The expanded version of the template string is stored in a special
    dictionary expanded, using the section name as the key. It can be
    used like the other dictionaries; hence, complex entries can be
    constructed over multiple sections using the expanded dictionary
    as the dict from which the expansion strings are pulled. This is
    common practice e.g. for complex tables, where first individual
    lines are built and the the full table is constructued. 

    The following options are understood:

    template
    
       The actual template string. Write plain LaTeX code here. Add
       ${NAME} commands; these are expanded during processing just
       like the standard template class does; see below for
       details. In addition, it is possible to use %{ PYTHONCODE
       %}. This string is replaced by the evaluation result of the
       PYTHONCODE string. 

    dict
       Specify a dictionary in which the ${NAME} are looked up as
       keys; the value of that key then replaces the ${NAME} string in
       template. Either dict or list must be given.

    list
       A list option must be followed by list variable (or other
       iterable). Then, the template is evaluated over each element of
       the list; the elements must be dictionaries where the ${NAME}s
       exist as keys.

       A dict option can be given as well, then ${NAME}s are looked up
       both in the list elements as well as in the given dictionary.

       Without any further options, a list of expanded template
       strings is put into expanded dictionary, under the sectionname
       as key. 
       
    numerator
       When a list option is given, it can be useful or desirable not
       to put a list into the expanded dictionary, but rather a
       separate entry under a separate key for each list element can
       be useful. The numerator option triggers this and specifies the
       suffix to be placed after the section name in the expanded
       dictionary. numerator can be a an expression like
       value['Shortname'], which is then evaluated over the dictionray
       in the provided list (in this example, this is evaluated over
       the list allWPDicts, Shortname is the WP shortname; then,
       sectionname-WPShortname can be used later on). 

    joiner
       If a list is given, but ony a single string entry in the
       expanded dictionary is desired (instead of a a list entry or a
       separate entries), then a string to be used with the
       string.join method can be given here. 

    sorter
       Specifies a Python expression to sort the list before being
       expaned. Typically, this should be a lambda function, evaluated
       over the list elements in the usual way the Python sorted
       built-in function's key option is used.  Mostly makes sense in
       combination with the joiner option.

    file
       Normally, results of the template expansion are only placed in
       the expanded dictionary. Giving file=True optino also writes
       the expansion result into a file called
       SECTIONNAME.tex. Directory is the genlatexpath value in
       settings.cfg. 

    dir
       Only relevant when file=True: this option specifies the
       directory (relative to the genlatexpath option). 

    """

    global titlepageDict, partnerList, expanded 
    global allWPDicts, allMilestones, allDeliverables, allTasks, allEfforts


    # pp(templates)

    templateParser = utils.getSettings(config.get("PathNames",
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
                exp =  t.safe_substitute (eval(templ["dict"]))
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
    """Use the information in templ to check whether it should be
    written out and write the particular template to disk."""

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

            outtext = expanded[keytouse]

            # move any figures out of the framed environments
            inlines = outtext.split('\\begin{framed}')
            outlines = []
            outlines.append(inlines[0])

            p = re.compile (r'(?P<beforeFigure>.*)(?P<beginfigure>\\begin{figure})(?P<bodyfigure>.*)(?P<endfigure>\\end{figure})(?P<afterfigure>.*\\end{framed}.*)',
                            re.DOTALL)
            for o in inlines[1:]:
                # print "---------------------"

                m = p.match (o)
                while m:
                    # print "before figure:", m.group('beforeFigure')
                    # print "--------"
                    # print "begin figure:", m.group('beginfigure')
                    # print "--------"
                    # print "body figure:", m.group('bodyfigure')
                    # print "--------"
                    # print "end figure:", m.group('endfigure')
                    # print "--------"
                    # print "after figure:", m.group('afterfigure')

                    o = m.group('beforeFigure') + \
                        m.group('afterfigure') + \
                        m.group('beginfigure') + \
                        m.group('bodyfigure') + \
                        m.group('endfigure')

                    m = p.match (o)


                outlines.append(o)

            outtext = '\\begin{framed}'.join(outlines)
            utils.writefile (outtext, filename)

    
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
        wp.keydoc = """The total effort of this WP (as string, not
        sure why?)."""

        taskset = set([task['Label'] for task in allTasks if task['wp'] == wp['Number']])
        wp['taskeffort'] = dict([ (t, sum([int(te['resources'])
                                           for te in allEfforts if te['task'] == t]))
                                  for t in taskset ] )
        wp.keydoc = """A dictionary, mapping the symbolic label of
        each task of this WP to the total effort it consumes (as
        integer)."""
        
        partnerset = set([te['partner'] for te in allEfforts if te['wp'] == wp['Number'] and int(te['resources']) > 0])
        wp['partnereffort'] = dict([ (p, sum([int(te['resources'])
                                              for te in allEfforts
                                              if te['partner'] == p and
                                              te['wp'] == wp['Number'] and int(te['resources']) > 0]))
                                     for p in partnerset ] )
        wp.keydoc = """A dictionary mapping the shortname of each
        partner with positive effort in this WP to the effort (as integer)."""
        
        # make sure that every partner is mentioned in partnereffort, with 0 if no effort
        for p in partnerList:
            if not wp['partnereffort'].has_key(p['Shortname']):
                wp['partnereffort'][p['Shortname']] = 0
            

        wp['End'] = int(wp['Start']) + int(wp['Duration']) - 1 

        try:
            wp['Leadernumber'] = [p['Number'] for p in partnerList if p['Shortname'] == wp['Leadership']][0]
        except:
            wp['Leadernumber'] = 1
    return 


def generatePartnerDescriptions(config, verbose):
    """Generate the LaTeX code to describe a partner, including
    subsection heading and labels. Produces the partnersIncluder.tex
    file. 
    """
    
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
    parser.add_option ("-d", "--docu", dest="docu",
                       help="print documentation output for the main global variables",
                       action="store_true", default=False)
    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="print lot's of debugging information",
                       action="store_true", default=False)
    (options, args) = parser.parse_args()

    config = utils.getSettings(options.settingsfile)

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


    ## just to help producing the documentation easier:
    if options.docu:
        fp = codecs.open ("../docsource/latexfromXMLKeyValue.rst",
                          'w', encoding='utf-8')
        utils.docuDict ('titlepageDict', titlepageDict, fp)
        utils.docuDict ('allWPDicts', allWPDicts[0], fp)
        utils.docuDict ('allTasks', allTasks[0], fp)
        utils.docuDict ('allMilestones', allMilestones[0], fp)
        utils.docuDict ('allDeliverables', allDeliverables[0], fp)
        utils.docuDict ('allEfforts', allEfforts[0], fp)
        utils.docuDict ('partnerList', partnerList[0], fp)

        fp.close()

