
"""A Moinmoin action to download the latex / figure code. Useful in
the later stages of the proposal writing.  The
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
        out = subprocess.check_output (['make', 'createtar'],
                                       cwd=makepath,
                                       stderr=subprocess.STDOUT)
        request.theme.add_msg ("The tar file has been created successfully.")        
    except subprocess.CalledProcessError, e:
        request.theme.add_msg ("The tar command has returned code %d, this usually signifies an error.\n Output: %s" % (e.returncode, e.output))
    except OSError, e: 
        request.theme.add_msg ("Operating system raised an error with code %d and description:  %s." % (e.errno, e.strerror))
    except:
        request.theme.add_msg ("An unknown error has occured. This is a serious problem!")
        
        
    Page (request, pagename).send_page()
    
    
