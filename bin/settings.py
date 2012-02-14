#!/usr/bin/python

import ConfigParser, os

def getSettings(filename):
    """Try to find the settings file, turn it into a configParser
    object, and do some first preprocessing on it."""

    if not filename:
        filename = "../settings.cfg"

    c = ConfigParser.SafeConfigParser()
    c.optionxform = str  # to make option names case sensitive! 

    if not c.read(filename):
        print "Settings file not found, was looking at: " + filename
        print "Serious problem - giving up"
        exit

    # add a .. prefix if pathNames appear
    if c.has_section('PathNames'):
        for o in c.options('PathNames'):
            if not o == 'bindir':
                c.set ('PathNames', o, os.path.join ('..', c.get('PathNames', o)))
                # print o, c.get('PathNames', o)


    return c 
