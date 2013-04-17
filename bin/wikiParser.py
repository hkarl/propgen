#!/usr/bin/python

""" 
We need to parse various wiki formats into useable latex. This module
provides an abstract base class wikiParser that implements a lot of
basic functions e.g.,  to extract tables, lists, etc.

This base class has to be subclassed to specialize for specific Wiki
syntax variants. The subclasses can be fairly slim and mostly specify
regular expressions to use (e.g., how to recognize headings).

A factory function is called to obtain an instance of such a parser. 
"""


import re
from pprint import pprint as pp
import shutil
import utils
import os 
import string
import glob
import bisect
import fnmatch 

def wikiParserFactory(config):
    """Construct an instance of the correct parser class, choice depends on what is
    selected in settings.cfg."""
    wikitype = config.get ('Wiki', 'wikitype')

    if wikitype == "moinmoin" or wikitype=="moinmoin-local":
        return wikiParserMoinmoin(config)
    elif wikitype == "twiki":
        return wikiParserTwiki(config)
    else:
        return None         
    

class wikiParser:
    """Base class to get the interface for turning wiki syntax into useful stuff"""

    def getSection (self, wiki, title, level):
        """Extract the section with title at level from the text in the wiki parameter """
        return None

    def getList (self, wiki):
        """Turn the first itemize in the wiki into a list.
        
        Note: this seems to be identical for all known wiki syntax variations
        overwrite this in subclass if necessary """
        lines = wiki.splitlines()
        res = []
        found = False
        
        for l in lines:
            m = re.match (r"^ +\* (?P<entry>.*)", l)
            if m:
            # if re.match (r"^ +\* ", l):
                if not found:
                    found=True
                res.append(str(m.group('entry').strip()))
            else:
                if found:
                    break
                    
        
        return res 

    def getListAsDict (self, wiki, delimiter = ":"):
        """Take the next enumeration from the wiki content. Assume it is a list with key/value delimited by delimiter. 
        Split them up, return a proper dictionary for that"""
        tmp = self.getList(wiki)
        tmp = [x.split(':') for x in tmp]
        tmp = [(x[0].strip(), x[1].strip()) for x in tmp]
        return dict(tmp)
        
    def getTable (self, wiki):
        """turn the first table into list of dictionaries, using the first row as
        keys for the dictionaries. Remove boldfacing from the first row entries if present."""

        lines = wiki.splitlines()
        found = False
        rows=[]
        keys=[]
        for l in lines:
            if re.match(self.tableRows, l):
                if not found:
                    # first table row, extract keys
                    found= True
                    keys = l.split(self.tableColumns)
                    keys = map (lambda x:
                                str(x.strip()).strip(self.boldfaceDelimiter),
                                keys)
                else:
                    # normal table row, just add the individual dictionary for this row
                    values = l.split (self.tableColumns)
                    values = map (lambda x: x.strip(), values)
                    rows.append(dict (zip(keys,values)))
            else:
                if found:
                    break

        # and get rid of some empty entries:
        for r in rows:
            try:
                r.pop('')
            except:
                pass
            
        return rows

    def getSectionRe (self, wiki, startre, endre):
        """Use the text in the wiki parameter, extract the next
        section matching the start and end regular expressions."""
        try:
            t = re.split (startre, wiki)[1]
        except:
            print "Warning: Section not found! regular expression:", startre
            return ""

        ## print "previous string removed:"
        ## print t 
        tt = re.split (endre, t)[0]

        return tt 
        

    def buildHeadings (self, latex):
        """Turn all the wiki headings in the latex parameter into the
        proper LaTeX heading commands, along with a label command as
        well. Uses the classes headingReplacements attribute where
        proper regular expressions are defined.  """
        for rep in self.headingReplacements:
            latex = re.sub (rep[0],
                            lambda m: '\\' + rep[1] + '{' + m.group(1) + '}' +
                            "\n\\label{sec:" +
                            self.constructLabel (m.group(1)) + "}\n",
                            latex, 0 , re.M)
        return latex

    def buildLists (self, latex):
        """Turn all the Wiki lists in the latex text into proper LaTeX
        lists. Take care to handle nested lists correctly."""
        indentLevel = 0
        enumerateLevel = 0 

        lines = latex.split('\n')
        latex = ""
        for l in lines: 
            # an itemize list? 
            tmp = re.match('( *\* )', l)
            if tmp:
                leadingSpacesBeforeAsterix =tmp.group(0)
                lineIndent = (len(leadingSpacesBeforeAsterix)-1)/self.lineIndentDivisor
                # restText = l[3*lineIndent+2:len(l)] + '\n'
                restText = l[len(leadingSpacesBeforeAsterix):] + '\n'

                # print lineIndent
                # print leadingSpacesBeforeAsterix

                # print "restText  ", restText

                if lineIndent > indentLevel:
                    # print indentLevel - lineIndent + 1
                    for i in range(lineIndent - indentLevel ):
                        latex +=  "\\begin{compactitem}\n"
                        indentLevel += 1
                    latex +=  "\\item " +  restText

                elif lineIndent == indentLevel:
                    latex +=  "\\item " +  restText
                elif lineIndent < indentLevel:
                    for i in range(indentLevel - lineIndent):
                        latex +=  "\\end{compactitem}\n"
                    indentLevel = lineIndent 
                    latex +=  "\\item " +  restText
            else:
                # no indent on this line ; do we have an indent previously?
                if indentLevel > 0:
                    # close all indents
                    for i in range(indentLevel):
                        latex +=  "\\end{compactitem}\n" 
                    indentLevel = 0 
                latex += l+  '\n'


        lines = latex.split('\n')
        latex = ""
        for l in lines: 
            tmp = re.match('( *1\. | *1 )', l)
            if tmp:
                leadingSpacesBeforeAsterix =tmp.group(0)
                lineIndent = (len(leadingSpacesBeforeAsterix)-1)/self.lineIndentDivisor
                # restText = l[3*lineIndent+2:len(l)] + '\n'
                restText = l[len(leadingSpacesBeforeAsterix):] + '\n'

                # print lineIndent
                # print leadingSpacesBeforeAsterix

                if lineIndent > enumerateLevel:
                    # print eumerateLevel - lineIndent + 1
                    for i in range(lineIndent - enumerateLevel ):
                        latex +=  "\\begin{compactenum}\n"
                        enumerateLevel += 1
                    latex +=  "\\item " +  restText

                elif lineIndent == enumerateLevel:
                    latex +=  "\\item " +  restText
                elif lineIndent < enumerateLevel:
                    for i in range(enumerateLevel - lineIndent):
                        latex +=  "\\end{compactenum}\n"
                    enumerateLevel = lineIndent 
                    latex +=  "\\item " +  restText
            else:
                # no indent on this line ; do we have an indent previously?
                if enumerateLevel > 0:
                    # close all indents
                    for i in range(enumerateLevel):
                        latex +=  "\\end{compactenum}\n" 
                    enumerateLevel = 0 
                latex += l + '\n'

        return latex

    def getFileFromWiki(self, figfile):
        """
        Let's try to see if the figure file has been uploaded to the wiki.
        Also check if there is a newer version there, rather than the one in the latex path.

        This needs to be overriden by the dervied classes since this is highly specific for the particular wiki type.
        :rtype : None or error code
        """
        return None

    def buildFigure (self, t):
        """An attempt to allow direct figure inclusion. See
        documentation for details on synatx and limitations."""
        lines = t.split('\n')
        latex = ""
        # print self.figureRE
        for l in lines:
            # print l 
            m = re.search (self.figureRE, l)
            if m:
                ## print "line with figure: " , l
                ## print 'pre', m.group('pre') 
                ## print 'fs', m.group('fs')
                ## print 'post', m.group('post') 

                # s is the constructed replacmenet string. Might contain warning 
                s = ""

                # print "recognized figure"
                kvstring= m.group('fs')
                # print kvstring, self.figureKeys
                r= re.compile(self.figureKeys)
                d= self.extractFigureKeys (kvstring)

                # pp(d)
                # error checking: is the figure there, in a good format?
                if not d.has_key("file"):
                    utils.warning ("You are trying to include a graphic, but did not specify the filename!")
                    continue 

                # strip of any extension of the filename first - TODO 
                mm = re.search(r'([^.]*?)\..*', d['file'])
                if mm:
                    # utils.warning ("No need to specify file extension for graphic inclusion, file: " + d['file'])
                    d['file'] = mm.group(1)

                self.getFileFromWiki (d['file'])

                # check for PDF first
                crucialFailure = False

                if ((not os.path.exists(os.path.join(self.config.get("PathNames", 'manuallatexfigurespath'),
                                                     d["file"] + ".pdf"))) and
                        (not os.path.exists(os.path.join(self.config.get("PathNames", 'uploadedfigurespath'),
                                                         d["file"] + ".pdf")))):
                    w = "You are trying to include file " + d["file"] +  \
                        ", but no PDF file of that name exists in " + \
                        self.config.get("PathNames", 'manuallatexfigurespath') + \
                        ' or in ' +  self.config.get("PathNames", 'uploadedfigurespath')
                    utils.warning (w)
                    s += w

                    # print (os.path.join(
                    #     self.config.get("PathNames", 'manuallatexfigurespath'),
                    #     d["file"]))
                    if ((not glob.glob(os.path.join(
                            self.config.get("PathNames", 'manuallatexfigurespath'),
                            d["file"] + ".*")))
                        and
                            (not glob.glob(os.path.join(
                                    self.config.get("PathNames", 'uploadedfigurespath'),
                                    d["file"] + ".*")))
                        ):
                        w = ("You are trying to include file " +
                             d["file"] + 
                             ", but no file with any extension of that name was found in " +
                             self.config.get("PathNames",
                                             'manuallatexfigurespath')  + \
                             ' or in ' +  self.config.get("PathNames", 'uploadedfigurespath'))
                        utils.warning (w)
                        # that overwrittes a potential warning about pdf file not found 
                        s = w
                        crucialFailure = True
                    else:
                        w =  ("You are trying to include file " +
                              d["file"] + 
                              ", and at least some file with that basename was found in " +
                              self.config.get("PathNames",
                                              'manuallatexfigurespath') + 
                              " but you REALLY want to put PDF files there for acceptable results")

                        utils.warning (w)
                        s = w

                if not d.has_key("label"):
                    w =  ("You are not assigning a label to figure " + d["file"] + \
                             " - that will make cross-referencing impossible")
                    utils.warning (w)
                    s += " -- " + w

                if not d.has_key("caption"):
                    w =  ("You are not giving a caption to figure " + d["file"] + \
                             " - that will look VERY strange in the text!")
                    utils.warning (w)
                    s += " -- " + w

                st = ""
                if not crucialFailure:
                    # no warnings produced, so let's include the figure 
                    st = "\\begin{figure}{\\centering\\includegraphics*[width="
                    if d.has_key("latexwidth"):
                        st += d["latexwidth"]
                    else:
                        st += "0.8"
                    st += "\\textwidth]"
                    st += "{" + d["file"] + "}"
                    if d.has_key("caption"):
                        st += "\\caption{" + d["caption"] + "}"
                    if d.has_key("label"):
                        st += "\\label{fig:" + d["label"] + "}"
                    st += "}\\end{figure}"

                if s:
                    s =  st + "\\fxwarning{" + s + "}"
                else:
                    s = st

                #  dont ignore  the rest of the line:
                ## print "--------------" 
                ## print l
                ## print m.group('pre') + s + m.group('post')
                # latex += l
                latex += m.group('pre') + s + m.group('post')
            else:
                # print "no match"
                latex += l + "\n"

        return latex 


    def buildTable (self, t):
        """Turn wiki tables into LaTeX tabular environments. Interpret
        #TABULAR commands to set the tabular header. """


        
        inTable = False
        tabularHeader = "" 

        lines = t.splitlines()
        latex = ""
        for l in lines:
            # is there a tabular header in the wiki input?
            # extract it for the next following table
            mh = re.search (r'#+ *X?TABULAR: *(.*?) *#*$', l)
            if mh:
                # print "recognized header"
                # print l 
                # print mh.group(1)
                tabularHeader = mh.group(1)
		if re.search ('XTABULAR', l):
		    tabularType = 'xtabular'
                    print "xtabular recognized"
		else:
		    tabularType = 'tabular'

                continue 


            if len(l) > 0 and re.match(self.tableRows, l):
                # we are in a table row
                # print l

                ll = string.rstrip(string.lstrip(l, self.tableColumns),
                                   self.tableColumns)
                cols = string.count (ll, self.tableColumns)+1
                # print cols 
                colstring = 'p{' + str(0.8/cols) + '\\textwidth}'
                # print colstring 
                ll = re.sub (re.escape(self.tableColumns), r'&', ll)

                if not inTable:

                    if tabularHeader:
                        latex+= "\\centering\\begin{" + tabularType + "}{" + tabularHeader  + "}\n"
                        tabularHeader = ""
                    else:
                        latex+= "\\centering\\begin{tabular}{" + (colstring * cols)  + "}\n"
                        tabularType = "tabular"
                    if tabularType == 'tabular':
                        latex+= "\\toprule\n"
                    latex+= ll + "\\\\ \n"
                    if tabularType == 'tabular':
                        latex+= "\\midrule\n"
                    inTable=True
                else:
                    # we already are in the table, just put in the line 
                    latex += ll + '\\\\ \n'
            else:
                if inTable:
                    # we just left a table 
                    if tabularType == 'tabular':
                        latex+= "\\bottomrule \n"
                    latex += "\\end{" + tabularType + "} \n"
                    inTable=False

                latex += l + '\n'
        return latex

    def handleCharacters (self, latex):
        """Replace any special characters that might appear from
        attempts at manual HTML markup."""

        latex = string.replace (latex, '&lt;br&gt;', '\\newline')
        latex = string.replace (latex, '&lt;BR&gt;', '\\newline')
        latex = string.replace (latex, '%BR%', '\\newline')
        latex = string.replace (latex, '&gt;', '>')

        latex = re.sub (r'#+ *TODO: *(.*?)#+',
                        r'\\fxwarning{TODO!}\\emph{\\textbf{\1}}', \
                        latex, flags=re.DOTALL) 

        latex = string.replace (latex, '#', "\#")

        latex = re.sub (r'(\s)&quot;', r"\1``", latex)
        latex = re.sub (r'&quot;(\s)', r"''\1", latex)
        # we need a catch-all, in case there is no white-space around
        latex = re.sub (r'&quot;', r"''", latex)

        latex = string.replace (latex, '&amp;', "\\&")
        return latex
    
    def applyLaTeXFunctions (self, latex):
        """Apply all the LaTeX conversions functions step by
        step. Note that the order is important!"""

        # before we do anything, let's get rid of "lonely" & characters
        # later on, we build them back into \& for LaTeX processing
        latex  = string.replace (latex, '& ', '&amp;')

        # build the headings:
        latex = self.buildHeadings (latex) 

        # an compactenum list?
        latex = self.buildLists (latex)

        # process a figure:
        latex = self.buildFigure (latex) 

        # build table
        latex = self.buildTable (latex) 

        # and some simple replacements; need to fix the umlaut thingies
        # this needs to be done before the table generation 

        # and some simple replacements; need to fix the umlaut thingies 
        latex = self.handleCharacters(latex)

        return latex 

    
    def getLaTeX (self, t, f=""):
        """turn all of the wiki into LaTeX"""

        self.wikifile = f

        ## processing steps independent of the wiki type:
        t = re.sub (r'&lt;DEL&gt;(.|\n)*?&lt;/DEL&gt;', r'', t)
        t = re.sub (r'&lt;del&gt;(.|\n)*?&lt;/del&gt;', r'', t)
        t = re.sub (r'&lt;!--(.*)--&gt;', r'%% \1\n ', t)
        t = re.sub (r'<DEL>(.|\n)*?</DEL>', r'', t)
        t = re.sub (r'<del>(.|\n)*?</del>', r'', t)
        t = re.sub (r'<!--(.*)-->', r'%% \1\n ', t)

        # deal with the commissionHints:
        t = self.moveCommissionHints (t)


        # deal with verbatim environments:
        # t = [('bla1 \\b{v} bla2 \\e{v} bla3 \\b{v} bla4 ', ' bla5')]
        verbatimsplitter = re.compile (r'(.*?)\\begin\{verbatim\}(.*?)\\end\{verbatim\}', re.DOTALL)
        # [('bla1 ', ' bla2 '), (' bla3 ', ' bla4 ')]
        verbatimsplit = verbatimsplitter.findall(t)
        # print type(verbatimsplit)
        # print (verbatimsplit)

        if verbatimsplit: 
            verbatimender = re.compile (r'(.*)\\end\{verbatim\}(.*)', re.DOTALL)
            # [('bla1 \\b{v} bla2 \\e{v} bla3 \\b{v} bla4 ', ' bla5')]
            verbatimend = verbatimender.findall(t)

            latex = ""
            # now iterate over verbatimsplit, apply functions to first part, add with second part
            for block in verbatimsplit:
                latex += self.applyLaTeXFunctions(block[0]) + "\\begin{verbatim}" + block[1] + "\\end{verbatim}"
            if verbatimend:
                # print verbatimend
                latex += self.applyLaTeXFunctions (verbatimend[0][1])

            # in the function calls, all # characters are still there 
            # t = applyFunctions(t)
        else:
            latex = self.applyLaTeXFunctions (t) 

        return latex

    def constructLabel (self, t):
        """Given a heading, construct a suitable label out of it.
        Remove whitspaces and obvious strange characters."""

        # in case someone has the bright idea to put ampersands in the titles: 
        # t = re.sub ('\\\\&', '', t)
        t = re.sub ('&', '', t)

        # remove double whitespaces:
        t = re.sub (r'\s+', ' ', t)

        # capitalize to CamelCase:
        t = re.sub (r' ([a-z])', lambda m: m.group(1).upper(), t)
        
        # and remove all the remaining whitespaces: 
        t = re.sub (r'\s', '', t)
        return t 

    def moveCommissionHints (self, t):
        """Make sure that commission hints appear after the first heading!"""
        startCom = self.localHeading ("Start commission hints", 5)
        endCom = self.localHeading ("End commission hints", 5)

        m = re.search (startCom + "(.*)" + endCom, t, re.DOTALL)
        if m:
            hint =  m.group(1).strip()
            t = re.sub (startCom + ".*" + endCom, "", t, 0, re.DOTALL)
            anyHeading =  '|'.join([x[0] for x in self.headingReplacements])
            t = re.sub (anyHeading,
                        lambda m: m.group() +
                        "\n\\commissionhints{" + hint + "}", t, 1, re.M) 
        return t 
                       
    
class wikiParserMoinmoin(wikiParser):
    """Specialized for Moinmoin. Especially the order of the heading
    replacement regular expressions is tricky for moinmoin."""

    def __init__ (self, config):
        self.config = config
        self.localMoinmoin = config.get('Wiki', 'wikitype') == 'moinmoin-local'
        self.latexFiguresPath = config.get('PathNames', 'uploadedfigurespath')
        self.wikiAttachementPath = '../moin/wiki/data/pages/'
        self.boldfaceDelimiter = "'''"
        self.tableColumns = "||"
        # self.tableColumnsRE = "\|\|"
        self.tableRows = r"^\|\|"
        self.lineIndentDivisor = 1

        self.headingReplacements = [(r'^===== (.*) =====$', 'subparagraph'),
                                    (r'^==== (.*) ====$', 'paragraph'),
                                    (r'^=== (.*) ===$', 'subsubsection'),
                                    (r'^== (.*) ==$', 'subsection'),
                                    (r'^= (.*) =$', 'section')]

                                    #
        ## DATED:
        ## sadly, is seems we have to use the twiki approach here 
        ## self.figureRE = r'<img (.*)/>'
        ## self.figureKeys = r'([^ =]+) *= *("(.*?)"|[^ ]*)'

        ## Pattern: 
        ## {{attachment:test.pdf|label=fig:bla|caption=This is the caption}}
        self.figureRE = r'(?P<pre>.*){{attachment:(?P<fs>.*)}}(?P<post>.*)' #  r'{{attachment:(.*)}}' r'&lt;img (.*)/&gt;'   
        self.figureKeys = r'([^ =]+) *= *([^\|}]*)'


    def getFileFromWiki(self, figfile):

        """
        Try to find a figure file in the local moinmoin installation.
        Only relevant if it is indeed local moinmoin.

        :return: None
        """
        # print "in GetFileFromWiki"
        # print self.wikifile

        print figfile


        # try to find out what the candidate files are:

        if self.wikifile:
            candidateFiles = os.path.join(self.wikiAttachementPath,
                                                 self.wikifile,
                                                 'attachments',
                                                 figfile + '.*')

            # possible files: with any ending, in attachement path
            files = glob.glob (candidateFiles)
        else:
	    # print "trying by treewalk"
            # print self.wikiAttachementPath
            # print os.getcwd()
            files = []
            rdf = os.walk (self.wikiAttachementPath)
            # print rdf
	    try:
            	for root, dirnames, filenames in rdf: 
                    # print root, dirnames, filenames 
                    for filename in fnmatch.filter (filenames, figfile+'.*'):
		        # print "filename", filename 
                    	files.append(os.path.join(root, filename))
            except Exception as e: 
                print "Exception", type(e)


        # print "files: ", files 

        for f in files:
            fBase = os.path.basename(f)
            # print fBase

            existingFile = os.path.join(self.latexFiguresPath, fBase)

            # does this file really exist?
            if os.path.exists(existingFile):
                # if yes, is it perhaps newer than the one in the Wiki attachment?
                if (os.path.getmtime(existingFile) >
                    os.path.getmtime(f)):
                    # then, don't do antything
                    loop
            # otherwise: copy the file from the attachement path to the uploaded latex directory
            shutil.copy2(f, existingFile)



        return None

    ## def buildFigure (self, t):
    ##     """For building a figure, the moinmoin syntax can be exploited
    ##     by means of the vertical bar syntax. It should look like this:
    ##        {{attachment:test.pdf|label=fig:bla|caption=This is the caption}}
    ##     """
        
    ##     t = re.sub (r"{{attachment:.*?}}", "", t)
    ##     return (wikiParser.buildFigure (self, t))


    def extractFigureKeys (self, kvstring):
        """For building a figure, the moinmoin syntax can be exploited
        by means of the vertical bar syntax. It should look like this:
        {{attachment:duckie.png|&postion=htbp,&caption=bla bla and some more text for the caption,&label=fig:duckie,&latexwidth=0.8}}
           kvstring has the key-value pairs, with the {{attachment: }} already removed 
        """
        d = {}

        l = string.split(kvstring, '|')
        d['file'] = l[0]
        ll = string.split (','.join(l[1:]), ',')
        for x in ll:
            if x[0] == '&': 
                xx = string.split(x, '=')
                if xx[0][0] == '&':
                    xx[0] = xx[0][1:]
                d[xx[0]] = xx[1]

        #print d 
        
        return d


    def getSection (self, wiki, title, level):
        """Extract the section with title at level """

        startre = self.localHeading (title, level)
        endre = r'\n=' + '=?'*(level-1) + ' '
        
        # print "start, end re: >>" + startre + "<< >>" + endre +  "<<"
        return self.getSectionRe (wiki, startre, endre)

    def handleCharacters (self, latex):

        # first call the general methods to deal with characters:
        latex = wikiParser.handleCharacters (self, latex)
        
        # bold face?
        latex = re.sub (r"'''(.+?)'''", r'\\textbf{\1}', latex) 

        # emphasize?
        latex = re.sub (r"''(.+?)''", r'\\emph{\1}', latex) 

        # camel case stuff? (not sure this applies to moimon ? 
        latex = re.sub (r' !([a-z0-9]*?[A-Z]\w*?) ', r' \1 ', latex)

        latex = re.sub (r'&ldquo;', r"``", latex)
        latex = re.sub (r'&rdquo;', r"''", latex)


        return latex

    def localHeading (self, title, level):
        return '='*level + ' +' + title + ' +' + '='*level

    def buildListsHelper (self, inputLines, regexp, markup):
        indentStack = []
        lines = inputLines.split('\n')
        indentLevel = 0
        currentIndentIndex = -1
        latex = ""
        for l in lines:
        # an itemize list?
            tmp = re.match(regexp, l)
            if tmp:
                # print l, indentStack
                leadingSpacesBeforeAsterix =tmp.group(0)
                lineIndent = len(leadingSpacesBeforeAsterix)-2
                # restText = l[3*lineIndent+2:len(l)] + '\n'
                restText = l[len(leadingSpacesBeforeAsterix):] + '\n'

                # print lineIndent
                # print leadingSpacesBeforeAsterix
                # print "restText  ", restText


                if (not indentStack) or (lineIndent > max(indentStack)):
                    # new indentation level found
                    indentStack.append (lineIndent)

                # try to find the right index in the indentation stack, beware of missing ones
                # if the indentation value is in the stack, get that value's index
                # if not, round up to the next bigger one (to stay consistent with moinmoin)
                newIndentIndex = bisect.bisect_left (indentStack, lineIndent)

                # print currentIndentIndex, newIndentIndex

                if newIndentIndex > currentIndentIndex:
                    for i in range(currentIndentIndex, newIndentIndex):
                        latex +=  "\\begin{%s}\n" % markup
                elif newIndentIndex < currentIndentIndex:
                    for i in range(newIndentIndex, currentIndentIndex):
                        latex +=  "\\end{%s}\n" % markup

                currentIndentIndex = newIndentIndex

                latex +=  "\\item " +  restText

            else:
                # no indent on this line ; did we have an indent previously thgat we have to close?
                # i.e., is this the end of this (possibly nested) environment?
                if currentIndentIndex >= 0:
                    # close all indents
                    for i in range(currentIndentIndex+1):
                        latex +=  "\\end{%s}\n" % markup
                    currentIndentIndex = -1

                indentStack = []
                latex += l + '\n'

        # at the end of the lines: is possible an indent still open?
        if currentIndentIndex >= 0:
            # close all indents
            for i in range(currentIndentIndex+1):
                latex +=  "\\end{%s}\n" % markup
            currentIndentIndex = -1

        return latex


    def buildLists (self, latex):
        """Moinmoin has a rather different approach to building lists since it does not mandate a fixed number
        of whitespaces per indentation level. Rather, any increase is seen to go one step deeper. This rules out the
        ability to jump over several levels, though."""

        latex = self.buildListsHelper(latex, '( *\* )', 'compactitem')
        latex = self.buildListsHelper(latex, '( *1\. | *1 )', 'compactenum')

        return latex


class wikiParserTwiki(wikiParser):
    """Specialized for Twiki"""

    def __init__ (self, config):
        self.config = config 
        self.boldfaceDelimiter = "*"
        self.tableColumns = "|"
        # self.tableColumnsRE = "\|"
        self.tableRows = r"^\|"
        self.lineIndentDivisor = 3

        # example for image string:
        # <img file="duckie" label="duckie" caption="The main objectives of the Test project" latexwidth="1"/>

        self.figureRE = r'(?P<pre>.*)&lt;img (.*)/&gt;(?P<post>.*)'   
        self.figureKeys = r'([^ =]+) *= *(&quot;(.*?)&quot;|[^ ]*)'
        self.headingReplacements = [(r'^---\+ (.*)$', 'section'),
                                    (r'^---\+\+ (.*)$', 'subsection'),
                                    (r'^---\+\+\+ (.*)$', 'subsubsection'),
                                    (r'^---\+\+\+\+ (.*)$', 'paragraph'),
                                    (r'^---\+\+\+\+\+ (.*)$', 'subparagraph')]

    def extractFigureKeys (self, kvstring):
        d = {}
        for k,v1,v2 in re.findall(kvstring):
            # print "KEys: ", k, v1, v2
            d[k] = v2
        return d
    

    def getSection (self, wiki, title, level):
        """extract the section with title at level """
        startre = self.localHeading (title, level)
        endre = r'---' + r'\+?'*(level-1) + r' '

        return self.getSectionRe (wiki, startre, endre)

    def handleCharacters (self, latex):

        # first call the general methods to deal with characters:
        latex = wikiParser.handleCharacters (self, latex)
        
        # bold face?
        latex = re.sub (r'\*(.+?)\*', r'\\textbf{\1}', latex) 

        # emphasize?
        latex = re.sub (r'_(.+?)_', r'\\emph{\1}', latex) 

        # camel case stuff?
        latex = re.sub (r' !([a-z0-9]*?[A-Z]\w*?) ', r' \1 ', latex) 

        return latex

    def localHeading (self, title, level):
        """How does a heading with the given title, at the given level,
        look in this wiki style? Describe it as a regular expression."""
        return r'---' + r'\+'*level + r' +' + title
        

########################
# interactive calling:

if __name__ == '__main__':
    import sys

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option ("-s", "--settings", dest="settingsfile",
                       help="the settings file")
    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="print lot's of debugging information",
                       action="store_true", default=False)
    (options, args) = parser.parse_args()

    config = utils.getSettings(options.settingsfile)
    
    parser = wikiParserFactory (config)

    if args:
        for a in args:
            print parser.getLaTeX (open(a, 'r').read())
    else:
        import sys
        print parser.getLaTeX (sys.stdin.read())
        
    
