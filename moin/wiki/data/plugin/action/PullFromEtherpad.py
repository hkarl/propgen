"""An action to pull a page from Etherpad and use the text as a new version of the current page."""

from MoinMoin.PageEditor import PageEditor
from etherpadConnect import etherpadConnect as etherpadConnect


def execute (pagename, request):

    # get the etherpad instance and related information: 
    (ep, padname, padURL) = etherpadConnect (pagename)

    # teh moinmoin data: 
    pe = PageEditor(request, pagename) 
    currev = pe.current_rev()
    request.reset()

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
