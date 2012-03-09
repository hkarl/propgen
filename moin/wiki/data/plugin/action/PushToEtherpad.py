
"""An action to put the current wiki text on an Etherpad page and put a warning message on this page."""

from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor
import ConfigParser
import py_etherpad 

# for obfuscating pad names:
import string
import random

def id_generator(size=12,
                 chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for x in range(size))


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
    # NOTE: This is future versions of Etherpad-lite 
    ## try:
    ##     etherpadPassword = c.get('Etherpad', 'Password')
    ## except:
    ##     etherpadPassword = ''
    ##     pass

    ## print etherpadPassword
        
    # and groupID?
    ## try:
    ##     etherpadGroup = c.get('Etherpad', 'GroupID')
    ## except:
    ##     etherpadGroup = ''
    ##     pass
    

    # instead of using password, we can at least obfuscate the pad names: 
    try:
        obfuscated = c.getboolean ('Etherpad', 'ObfuscatePads')
        obfuscatedFile = c.get ('Etherpad', 'ObfuscatedFile')
    except: 
        obfuscated = False



    # create a py_etherpad client object
    baseURL = "http://" + etherpadIP + ":" + etherpadPort + "/"
    ep = py_etherpad.EtherpadLiteClient (apiKey = key,
                                         baseUrl = baseURL + "api")

    # parse the action request: 
    pe = PageEditor(request, pagename) 

    padtext = pe.get_raw_body()
    currev = pe.current_rev()


    padname = "Wiki-" + pagename
    padURL = baseURL + "p/" +  padname 
    success = False 
    padtextEP = padtext.encode('utf-8')


    # start the actual writing out to Etherpad. 
    try: 
        r = ep.getText (padname)

        ep.setText (padname, padtextEP)
        success = True 
    except ValueError:
        try: 
            if etherpadPassword:
                # is there a groupID? if not, create the group
                print "Group: ", etherpadGroup
                if not etherpadGroup:
                    resp = ep.createGroupIfNotExistsFor (c.get('Wiki', 'projectName'))
                    print resp
                    groupID = resp['groupID']
                    print groupID

                    # testing: delete the group immediately
                    ep.deleteGroup (groupIP)
                    
                # store the created group id in the settings file


                # then create the pad in this group
                # ep.createPad (padname, padtextEP)

                # and set pass word on it
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
        
