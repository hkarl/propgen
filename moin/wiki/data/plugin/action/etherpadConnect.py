"""Helper function to provide an Etherpad client object, compute the Etherpad name, and read / store pad name in the corresponding file."""

import ConfigParser
import py_etherpad 

# for obfuscating pad names:
import string
import random

def id_generator(size=12,
                 chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for x in range(size))



def etherpadConnect (pagename):
    """for the given pagename, return an Etherpad client object and the desired Pad name. Pad name is either stored in the obfucated.cfg file, or can be constructed directly. Also, padURL is returned."""

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
    


    # create a py_etherpad client object
    baseURL = "http://" + etherpadIP + ":" + etherpadPort + "/"
    ep = py_etherpad.EtherpadLiteClient (apiKey = key,
                                         baseUrl = baseURL + "api")



    # instead of using password, we can at least obfuscate the pad names: 
    try:
        obfuscated = c.getboolean ('Etherpad', 'ObfuscatePads')
    except: 
        obfuscated = False

    if obfuscated:
        co = ConfigParser.SafeConfigParser()
        co.optionxform = str  # to make option names case sensitive! 
        co.read ('obfuscated.cfg')
        
        try:
            padname = co.get ('EtherpadObfuscated', pagename)
        except:
            print "generating new pad id" 
            if not co.has_section('EtherpadObfuscated'):
                co.add_section ('EtherpadObfuscated')
            padname = pagename + "-" + id_generator()
            co.set ('EtherpadObfuscated', pagename, padname)
            with open ('obfuscated.cfg', 'w') as configfile:
                co.write (configfile)
    else: 
        padname = "Wiki-" + pagename

    print "padname: ", padname

    padURL = baseURL + "p/" +  padname     

    return (ep, padname, padURL)
