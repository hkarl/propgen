

# where is the settings file? 
SETTINGS = settings.cfg


####################################
SHELL?=/bin/bash 
.PHONY: proposal pdf clean pullproject


proposal: 
	make pullproject

pullproject: 
	cd bin ; python pullProject.py -s ../$(SETTINGS)


