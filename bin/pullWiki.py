#!/usr/bin/python


import settings 

###########################################

def pullFactory (configs, verbose=False):
    """A factory to create a proper instance of a Wiki puller class.
    It uses the setting wikitype to determine which class to use."""

    wikitype = configs.get ('Wiki', 'wikitype')
    if verbose: 
        print wikitype

    if wikitype=="moinmoin-local":
        pullInstance = PullMoinmoinLocal (configs, verbose)
    else:
        print "unknown wiki type!"
        exit 
    
    return pullInstance  

###########################################
# classes to pull a page from different wikis

class PullWiki:
    """A base class for all classes that pull one or several pages from a wiki.
    This should be an abstract class, i.e., instances of this class should not be instantiated."""
    def __init__ (self, options, verbose=False):
        if verbose:
            print options
        exit

    def getPage (self, page, verbose=False):
        if verbose:
            print page
            print "base class not callable"
        exit
        


###########################################
# pull page from twiki 

###########################################
# pull page from moinmoin, remotely 

###########################################
# pull page from moinmoin, locally  

class PullMoinmoinLocal(PullWiki):
    """Talk to a locally available Moinmoin wiki."""
    def __init__ (self, configs, verbose=False):
        if verbose:
            print "Trying to setup pulling from local moinmoin files"

        import sys
        # example for MoinMoin integration taken from here:
        # http://moinmo.in/MoinAPI/Beispiele#Referenz_der_Klassen_und_Methoden_von_MoinMoin
        # adding the path of moinmoin to sys.path
        sys.path.append (configs.get('Wiki', 'moinmoinpath'))
        
        from MoinMoin.web.contexts import ScriptContext
        self.request = ScriptContext()

    def getPage (self, page, verbose=False):

        print self.request 
        from MoinMoin.Page import Page
        text = Page (self.request, page).get_raw_body()
        if verbose:
            print type(text)
            print text.encode('utf-8')
        return text 

###########################################

if __name__ == "__main__":

    ## get the command line options: 
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

    if options.verbose:
        print options
        print args


    ### try to read the settings file:
    config = settings.getSettings(options.settingsfile)
    if options.verbose:
        print config
    
    pullInstance = pullFactory (config, options.verbose)

    pullInstance.getPage('TestProject', verbose=True)
    pullInstance.getPage('LanguageSetup', verbose=True)

    
