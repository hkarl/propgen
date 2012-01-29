#!/usr/bin/python

# we need to parse various wiki formats into useable latex
# also, helper functions to extract tables, lists, etc.
# complicated also by the fact that there are different wiki syntaxes to deal with

import re
from pprint import pprint as pp
import settings
import utils
import os 


def wikiParserFactory(config):
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
        """extract the section with title at level """
        return None

    def getList (self, wiki):
        """turn the first itemize in the wiki into a list"""
        # note: this seems to be identical for all known wiki syntax variations
        # overwrite this in subclass if necessary 
        lines = wiki.splitlines()
        res = []
        found = False
        
        for l in lines:
            if re.match (r"^   \* ", l):
                if not found:
                    found=True
                res.append(str(l[4:].strip()))
            else:
                if found:
                    break
                    
        
        return res 

    def getListAsDict (self, wiki, delimiter = ":"):
        """tmp is an aray of strings, assumed to be key/values delimited by delimited
        split them up, return a proper dictionary for that"""
        tmp = self.getList(wiki)
        tmp = [x.split(':') for x in tmp]
        tmp = [(x[0].strip(), x[1].strip()) for x in tmp]
        return dict(tmp)
        
    def getTable (self, wiki):
        """turn the first table into list of dictionaries, using the first row as
        keys for the dictionaries. Removing boldfacing from the first row entries."""

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
        try:
            t = re.split (startre, wiki)[1]
        except:
            print "Warning: Section " + title + " not found!"
            return ""
        
        tt = re.split (endre, t)[0]

        return tt 
        

    def buildHeadings (self, latex):
        for rep in self.headingReplacements:
            latex = re.sub (rep[0],
                            lambda m: '\\' + rep[1] + '{' + m.group(1) + '}' +
                            "\n\\label{sec:" +
                            self.constructLabel (m.group(1)) + "}\n",
                            latex)
        return latex

    def buildLists (self, latex):
        indentLevel = 0
        enumerateLevel = 0 

        lines = latex.split('\n')
        latex = ""
        for l in lines: 
            # an itemize list? 
            tmp = re.match('( *\* )', l)
            if tmp:
                leadingSpacesBeforeAsterix =tmp.group(0)
                lineIndent = (len(leadingSpacesBeforeAsterix)-1)/3
                restText = l[3*lineIndent+2:len(l)] + '\n'

                # print lineIndent
                # print leadingSpacesBeforeAsterix

                if lineIndent > indentLevel:
                    # print indentLevel - lineIndent + 1
                    for i in range(lineIndent - indentLevel ):
                        latex +=  "\\begin{compactitem}\n"
                    indentLevel = lineIndent 
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
                if (indentLevel > 0):
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
                lineIndent = (len(leadingSpacesBeforeAsterix)-1)/3
                restText = l[3*lineIndent+2:len(l)] + '\n'

                # print lineIndent
                # print leadingSpacesBeforeAsterix

                if lineIndent > enumerateLevel:
                    # print eumerateLevel - lineIndent + 1
                    for i in range(lineIndent - enumerateLevel ):
                        latex +=  "\\begin{compactenum}\n"
                    enumerateLevel = lineIndent 
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
                if (enumerateLevel > 0):
                    # close all indents
                    for i in range(enumerateLevel):
                        latex +=  "\\end{compactenum}\n" 
                    enumerateLevel = 0 
                latex += l + '\n'

        return latex 


    def buildFigure (self, t):
        import glob
        lines = t.split('\n')
        latex = ""
        # print self.figureRE
        for l in lines:
            m = re.search (self.figureRE, l)
            if m:

                # s is the constructed replacmenet string. Might contain warning 
                s = ""

                # print "recognized figure"
                kvstring= m.group(1)
                # print kvstring, self.figureKeys
                r= re.compile(self.figureKeys)
                d = {}
                for k,v1,v2 in r.findall(kvstring):
                    # print "KEys: ", k, v1, v2
                    d[k] = v2

                # pp(d)
                # error checking: is the figure there, in a good format?
                if not d.has_key("file"):
                    utils.warning ("You are trying to include a graphic, but did not specify the filename!")
                    continue 

                # strip of any extension of the filename first - TODO 
                mm = re.search(r'([^.]*?)\..*', d['file'])
                if mm:
                    utils.warning ("No need to specify file extension for graphic inclusion, file: " + d['file'])
                    d['file'] = mm.group(1)

                # check for PDF first 
                if not os.path.exists (os.path.join(
                    self.config.get("PathNames", 'manuallatexfigurespath'),
                    d["file"] + ".pdf")):
                    w = "You are trying to include file " + d["file"] +  \
                        ", but no PDF file of that name exists in " + \
                        self.config.get("PathNames", 'manuallatexfigurespath')
                    utils.warning (w)
                    s += w

                    print (os.path.join(
                        self.config.get("PathNames", 'manuallatexfigurespath'),
                        d["file"]))
                    if not glob.glob (os.path.join(
                        self.config.get("PathNames", 'manuallatexfigurespath'),
                        d["file"] + ".*")):
                        w = ("You are trying to include file " +
                             d["file"] + 
                             ", but no file with any extension of that name was found in " +
                             self.config.get("PathNames",
                                             'manuallatexfigurespath'))
                        utils.warning (w)
                        # that overwrittes a potential warning about pdf file not found 
                        s = w
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

                if not s:
                    # no warnings produced, so let's include the figure 
                    s = "\\begin{figure}{\\centering\\includegraphics*[width="
                    if d.has_key("latexwidth"):
                        s += d["latexwidth"]
                    else:
                        s += "0.8"
                    s += "\\textwidth]"
                    s += "{" + d["file"] + "}"
                    if d.has_key("caption"):
                        s += "\\caption{" + d["caption"] + "}"
                    if d.has_key("label"):
                        s += "\\label{fig:" + d["label"] + "}"
                    s += "}\\end{figure}"
                else:
                    s = "\\fxwarning{" + s + "}"

                latex += s
            else:
                latex += l + "\n"

        return latex 


    def buildTable (self, t):

        import string
        
        inTable = False
        tabularHeader = "" 

        lines = t.splitlines()
        latex = ""
        for l in lines:
            # is there a tabular header in the wiki input?
            # extract it for the next following table
            mh = re.search (r'#+ *TABULAR: *(.*) *#*$', l)
            if mh:
                # print mh.group(1)
                tabularHeader = mh.group(1) 
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
                ll = re.sub (self.tableColumnsRE, r'&', ll)

                if inTable==False:

                    if tabularHeader:
                        latex+= "{\\centering\\begin{tabular}{" + tabularHeader  + "}\n"
                        tabularHeader = ""
                    else:
                        latex+= "{\\centering\\begin{tabular}{" + (colstring * cols)  + "}\n"
                    latex+= "\\toprule\n"
                    latex+= ll + "\\\\ \n"
                    latex+= "\\midrule\n"
                    inTable=True
                else:
                    # we already are in the table, just put in the line 
                    latex += ll + '\\\\ \n'
            else:
                if inTable==True:
                    # we just left a table 
                    latex+= "\\bottomrule \n\\end{tabular}}\n"
                    inTable=False

                latex += l + '\n'
        return latex

    def handleCharacters (self, latex):
        import string 
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
        import string 
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

    
    def getLaTeX (self, t):
        """turn all of the wiki into LaTeX"""

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
            hint =  m.group(1)
            t = re.sub (startCom + ".*" + endCom, "", t, 0, re.DOTALL)
            anyHeading =  '|'.join([x[0] for x in self.headingReplacements])
            t = re.sub (anyHeading,
                        lambda m: m.group() +
                        "\\commissionhint{" + hint + "}", t, 1) 
        return t 
                       
    
class wikiParserMoinmoin(wikiParser):
    """Specialized for Moinmoin"""

    def __init__ (self, config):
        self.config = config 
        self.boldfaceDelimiter = "'''"
        self.tableColumns = "||"
        self.tableColumnsRE = "\|\|"
        self.tableRows = r"^\|\|"
        self.headingReplacements = [(r'===== (.*) =====', 'subparagraph'),
                                    (r'==== (.*) ====', 'paragraph'),
                                    (r'=== (.*) ===', 'subsubsection'),
                                    (r'== (.*) ==', 'subsection'),
                                    (r'= (.*) =', 'section')]


        ## sadly, is seems we have to use the twiki approach here 
        self.figureRE = r'<img (.*)/>'
        self.figureKeys = r'([^ =]+) *= *("(.*?)"|[^ ]*)'

    def buildFigure (self, t):
        # moinmoin syntax gets in out way - kick out the attachment syntax
        # and rely on the twik iway of doing it - this needs fixing! TODO
        t = re.sub (r"{{attachment:.*?}}", "", t)
        return (wikiParser.buildFigure (self, t))
        
    def getSection (self, wiki, title, level):
        """extract the section with title at level """

        startre = self.localHeading (title, level)
        endre = '=' + '=?'*(level-1) + ' '

        return self.getSectionRe (wiki, startre, endre)

    ## def getTable (self, wiki):
    ##     """turn the first table at the beginning of wiki text into a dictionary"""
    ##     return self.getTableDelimiter (wiki, '||', r"^\|\|")

    def handleCharacters (self, latex):

        # first call the general methods to deal with characters:
        latex = wikiParser.handleCharacters (self, latex)
        
        # bold face?
        latex = re.sub (r"'''(.+?)'''", r'\\textbf{\1}', latex) 

        # emphasize?
        latex = re.sub (r"''(.+?)''", r'\\emph{\1}', latex) 

        # camel case stuff? (not sure this applies to moimon ? 
        latex = re.sub (r' !([a-z0-9]*?[A-Z]\w*?) ', r' \1 ', latex) 

        return latex

    def localHeading (self, title, level):
        return '='*level + ' +' + title + ' +' + '='*level


class wikiParserTwiki(wikiParser):
    """Specialized for Twiki"""

    def __init__ (self, config):
        self.config = config 
        self.boldfaceDelimiter = "*"
        self.tableColumns = "|"
        self.tableColumnsRE = "\|"
        self.tableRows = r"^\|"
        self.figureRE = r'&lt;img (.*)/&gt;'
        self.figureKeys = r'([^ =]+) *= *(&quot;(.*?)&quot;|[^ ]*)'
        self.headingReplacements = [(r'---\+ (.*)', 'section'),
                                    (r'---\+\+ (.*)', 'subsection'),
                                    (r'---\+\+\+ (.*)', 'subsubsection'),
                                    (r'---\+\+\+\+ (.*)', 'paragraph'),
                                    (r'---\+\+\+\+\+ (.*)', 'subparagraph')]

    def getSection (self, wiki, title, level):
        """extract the section with title at level """
        startre = self.localHeading (title, level)
        endre = r'---' + r'\+?'*(level-1) + r' '

        return self.getSectionRe (wiki, startre, endre)

    ## def getTable (self, wiki):
    ##     """turn the first table at the beginning of wiki text into a dictionary"""
    ##     return self.getTableDelimiter (wiki, '|', )

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

    config = settings.getSettings(options.settingsfile)
    
    parser = wikiParserFactory (config)

    if args:
        for a in args:
            print parser.getLaTeX (open(a, 'r').read())
    else:
        import sys
        print parser.getLaTeX (sys.stdin.read())
        
    
