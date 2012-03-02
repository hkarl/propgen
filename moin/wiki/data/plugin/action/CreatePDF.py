
"""A Moinmoin action to create the PDF file of a project proposal. The
relative location of the moinmoin wiki with respect to main Makefile
is hardcoded, and so is the location of the attachements in the
Makefile. 
"""

from MoinMoin.Page import Page
import os
import subprocess 


def execute (pagename, request):

    # find the path to the root of the project directory tree
    makepath = os.path.join(os.path.curdir, "..")
    
    # trigger a build viewer the make process. It puts the PDF file directly in the right place! 
    try: 
        out = subprocess.check_output (['make', 'moinpdf'], cwd=makepath, stderr=subprocess.STDOUT)
        request.theme.add_msg ("The pdf has been created successfully.")        
    except subprocess.CalledProcessError as (returncode, output):
        request.theme.add_msg ("The pdf has been created with return code %d, this usually signifies an error.\n Output: %s" % (returncode, output))
    except OSError as (errno, strerror):
        request.theme.add_msg ("Operating system raised an error with code %d and description:  %s." % (errno, strerror))
    except:
        request.theme.add_msg ("An unknown error has occured. This is a serious problem!")
        
        
    Page (request, pagename).send_page()
    
    
