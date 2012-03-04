
"""An action to put the current wiki text on an Etherpad page and put a warning message on this page."""

from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor
import ConfigParser
import py_etherpad 


def execute (pagename, request):

    # find out which port to use:
    c = ConfigParser.SafeConfigParser()
    c.optionxform = str  # to make option names case sensitive! 
    c.read ('../settings.cfg')
    
    etherpadIP = c.get ('Etherpad', 'IP')
    etherpadPort = c.get ('Etherpad', 'Port')
    
    # API key for Etherpad: 
    try:
        key = c.get('Etherpad', 'Key')
    except:
        try:
            keypath= c.get('Etherpad', 'PathToKey')
            fp = open(keypath, 'r')
            key = fp.read()
        except:
            key = "not found"

    # Password for Etherpad?
    try:
        etherpadPassword = c.get('Etherpad', 'Password')
    except:
        etherpadPassword = ''
        pass 

    # create a py_etherpad client object
    baseURL = "http://" + etherpadIP + ":" + etherpadPort + "/"
    ep = py_etherpad.EtherpadLiteClient (apiKey = key,
                                         baseUrl = baseURL + "api")

    # parse the action request: 
    pe = PageEditor(request, pagename) 

    padtext = pe.get_raw_body()
    ## print padtext
    ## if isinstance(padtext, unicode):
    ##     padtext = padtext.encode('latin-1', 'ignore')
    ## print type(padtext)
    ## print padtext 

    currev = pe.current_rev()


    # TODO: Check whether is is already on Etherpad - if so, ask whether a new session should be started?

    
    padname = "Wiki-" + pagename
    padURL = baseURL + "p/" +  padname 
    success = False 

    # padtextEP = padtext.encode('iso8859')
    padtextEP = padtext.encode('utf-8')
    # padtextEP = padtext.encode('ascii', 'xmlcharrefreplace')
    try: 
        r = ep.getText (padname)

        ep.setText (padname, padtextEP)
        success = True 
    except ValueError:
        try: 
            if etherpadPassword:
                # let's try to password-protect this page:
                # ep.createGroupIfNotExistsFor ()
                # ep.setPassword (padname, etherpadPassword)
                print "not implemented"
            else:
                ep.createPad (padname, padtextEP)
                 
            success = True
        except:
            msg = "Unknown error occured when trying to create a new pad"
            pass
    except:
        msg = "Unknown error occured when trying to access Etherpad."


    # put the result of the etherpad invocation back on wiki: 
    if success: 
        admon = """{{{#!wiki caution
        '''Do not edit this page, it is currently on Etherpad!'''

        This wiki page is currently edited in an Etherpad session - URL: %s. You really should not edit this page since it is very likely that your edits will get lost once the Etherpad session is integrated back into the wiki. Use the action PullFromEtherpad to trigger that integration (and then stop the Etherpad editing!).
        }}}
        """ % padURL

        savetext = admon + "\n\n" + padtext
        
        request.reset()
        try:
            pe.saveText(savetext, currev)
            msg = "no error" 
        except pe.EditConflict, e:
            # print e 
            msg = "Edit Conflict" + e.message

        request.theme.add_msg(msg, "info")
        pe.send_page()
    else:
        request.theme.add_msg (msg, "info")
        pe.send_page()
        
