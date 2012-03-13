
"""An action to put the current wiki text on an Etherpad page and put a warning message on this page."""

from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor


from etherpadConnect import etherpadConnect as etherpadConnect


def execute (pagename, request):

    # parse the action request: 
    pe = PageEditor(request, pagename) 

    padtext = pe.get_raw_body()
    currev = pe.current_rev()
    padtextEP = padtext.encode('utf-8')

    # get the etherpad instance and related information: 
    (ep, padname, padURL) = etherpadConnect (pagename)

    
    # start the actual writing out to Etherpad. 
    success = False 
    try: 
        r = ep.getText (padname)
        ep.setText (padname, padtextEP)
        success = True 
    except ValueError:
        # print "Etherpad reported valueError" 
        ep.createPad (padname, padtextEP)
        success = True
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
            msg = "Edit Conflict when trying to push out to Etherpad!" + e.message

        request.theme.add_msg(msg, "info")
        pe.send_page()
    else:
        request.theme.add_msg (msg, "info")
        pe.send_page()
        
