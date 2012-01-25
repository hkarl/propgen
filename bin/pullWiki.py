#!/usr/bin/python

import sys 

###########################################

def pullFactory (configs, verbose=False):
    """A factory to create a proper instance of a Wiki puller class.
    It uses the setting wikitype to determine which class to use."""

    wikitype = configs.get ('Wiki', 'wikitype')
    if verbose: 
        print wikitype

    if wikitype=="moinmoin-local":
        pullInstance = PullMoinmoinLocal (configs, verbose)
    elif wikitype=="moinmoin":
        pullInstance = PullMoinmoin (configs, verbose)
    else:
        print "unknown wiki type!"
        sys.exit()
    
    return pullInstance  

###########################################
# classes to pull a page from different wikis

class PullWiki:
    """A base class for all classes that pull one or several pages from a wiki.
    This should be an abstract class, i.e., instances of this class should not be instantiated."""
    def __init__ (self, options, verbose=False):
        if verbose:
            print options
        sys.exit()

    def getPage (self, page, verbose=False):
        if verbose:
            print page
            print "base class not callable"
        sys.exit()
        

###########################################
# pull from anything based on mechanize
# to be subclassed further for the particular wiki type

class PullWikiMechanize(PullWiki):
    """A class to capture the mechanize-modul based login to a wiki.
    Needs to be subclassed further to capture idiosyncracies of different wiki types."""

    def __init__ (self, configs, verbose=False):

        if verbose:
            print "Trying to setup mechanize"

        self.baseURL = configs.get('Wiki', 'baseURL')
        self.wikiuser = configs.get('Wiki', 'wikiuser')
        self.wikipassword = configs.get('Wiki', 'wikipassword')
        self.wikiproject = configs.get('Wiki', 'projectPage')
        
        import mechanize
        self.br=mechanize.Browser()
        self.br.set_handle_robots(False)
        self.setProxyValues (configs, verbose)
        
    def setProxyValues (self, configs, verbose=False):

        if verbose:
            print "setting proxy values is known not to work reliably, not implemented yet!"

        
###########################################
# pull page from twiki 

###########################################
# pull page from moinmoin, remotely

class PullMoinmoin(PullWikiMechanize):

    def __init__ (self, configs, verbose=False):

        import mechanize
        
        PullWikiMechanize.__init__(self, configs, verbose)

        ## let's do the login by accessing the main project page  
        ## loginURL = self.baseURL + self.wikiproject + "?action=login"
        # we don't really need a particular page: 
        loginURL = self.baseURL +  "?action=login"
        if verbose:
            print "init in PullMoinmoin"
            print "login url: " + loginURL

        loginresponse = self.br.open(loginURL)
        loginforms = mechanize.ParseResponse(loginresponse) 

        loginform=None
        for f in loginforms:
            try:
                f.find_control (name="password")
                loginform = f
            except:
                pass

        if loginform:
            if verbose:
                print loginform
            loginform["name"]=self.wikiuser
            loginform["password"]=self.wikipassword
            self.br.open(loginform.click()).read()
        else:
            print "No password field found when trying to login into moinmoin. Giving up!"
            sys.exit() 
            
        
    def getPage (self, page, verbose=False):

        import mechanize
        
        targetURL = self.baseURL + page + "?action=raw"

        if verbose: 
            print "trying to load: " + targetURL
        self.br.open(targetURL)
        response = self.br.response().read()

        return response 
    
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
    import settings 

    config = settings.getSettings(options.settingsfile)
    if options.verbose:
        print config
    
    pullInstance = pullFactory (config, options.verbose)

    if options.page:
        res = pullInstance.getPage(options.page)
    else:
        res = pullInstance.getPage(config.get('Wiki','projectPage'))

    if res:
        print res.encode('utf-8')
    

