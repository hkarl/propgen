#!/usr/bin/python

# we need to parse various wiki formats into useable latex
# also, helper functions to extract tables, lists, etc.
# complicated also by the fact that there are different wiki syntaxes to deal with

import re
from pprint import pprint as pp

def wikiParserFactory(config):
    wikitype = config.get ('Wiki', 'wikitype')

    if wikitype == "moinmoin" or wikitype=="moinmoin-local":
        return wikiParserMoinmoin()
    elif wikitype == "twiki":
        return wikiParserTwiki()
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

    def getTable (self, wiki):
        """turn the first table into list of dictionaries, using the first row as
        keys for the dictionaries. Removing boldfacing from the first row entries."""
        return []

    def getTableDelimiter (self, wiki, column, rowre, boldface):
        """get Table, but with possibility to specify how columns are separated,
        which regular expression should be applied to detect a table row,
        and what the boldface delimiter for the particular wiki is """
        lines = wiki.splitlines()
        found = False
        rows=[]
        keys=[]
        for l in lines:
            if re.match(rowre, l):
                if not found:
                    # first table row, extract keys
                    found=True
                    keys =  l.split(column)
                    keys = map (lambda x: str(x.strip()).strip(boldface), keys)
                else:
                    # normal table row, just add the individual dictionary for this row
                    values = l.split (column)
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

    def getLaTeX (self, wiki):
        """turn all of the wiki into LaTeX"""
        return ""
    
class wikiParserMoinmoin(wikiParser):
    """Specialized for Moinmoin"""
    def getSection (self, wiki, title, level):
        """extract the section with title at level """
        startre = '='*level + ' +' + title + ' +' + '='*level
        # print startre

        t = re.split (startre, wiki)[1]

        ## try to find the end of the section; signaled by another heading
        ## of the same or smaller level
        ## no matter if not found, then simply talk all the text
        
        endre = '=' + '=?'*(level-1) + ' '
        # print endre 
        tt = re.split (endre, t)[0]

        return tt 


    def getTable (self, wiki):
        """turn the first table at the beginning of wiki text into a dictionary"""
        t = self.getTableDelimiter (wiki, '||', r"^\|\|", "'")
        # pp(t)
        return t 

class wikiParserTwiki(wikiParser):
    """Specialized for Twiki"""
 
