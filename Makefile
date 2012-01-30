

# where is the settings file? 
SETTINGS = settings.cfg

####################################
SHELL?=/bin/bash 
.PHONY: proposal pdf clean pullproject
####################################


proposal: 
	make pullproject
	make xml 
	make latexFromWiki

pullproject: 
	cd bin ; python pullProject.py -s ../$(SETTINGS)

xml:
	cd bin ; python generateXML.py -s ../$(SETTINGS)

latexFromWiki:
	cd bin ; python latexFromWiki.py -s ../$(SETTINGS)

clean:
	find generated/ -type f -print | grep -v README | xargs rm 

