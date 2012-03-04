"""An action to pull a page from Etherpad and use the text as a new version of the current page."""

from MoinMoin.PageEditor import PageEditor
import ConfigParser
import py_etherpad 

def execute (pagename, request):

    # find the settings file to access the ehterpad: 
    c = ConfigParser.SafeConfigParser()
    c.optionxform = str  # to make option names case sensitive! 
    c.read ('../settings.cfg')
    
    etherpadIP = c.get ('Etherpad', 'IP')
    etherpadPort = c.get ('Etherpad', 'Port')

    try:
        key = c.get('Etherpad', 'Key')
    except:
        try:
            keypath= c.get('Etherpad', 'PathToKey')
            fp = open(keypath, 'r')
            key = fp.read()
        except:
            key = "not found"


    # create a py_etherpad client object
    baseURL = "http://" + etherpadIP + ":" + etherpadPort + "/"
    ep = py_etherpad.EtherpadLiteClient (apiKey = key,
                                         baseUrl = baseURL + "api")

    pe = PageEditor(request, pagename) 

    currev = pe.current_rev()

    request.reset()

    padname = "Wiki-" + pagename

    try: 
        padtext = ep.getText (padname)[u'text']
        try:
            pe.saveText (padtext, currev)
            msg = "Text has been successfully obtained from Etherpad."
        except Exception as e:
            msg = "Text has been obtained from Etherpad, but an error occured when saving it to Wiki. " 
    except Exception as e:
        msg = "An error occured when trying to obtain text from Etherpad." 

    request.theme.add_msg(msg, "info")
    pe.send_page()
