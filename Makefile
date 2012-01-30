

# where is the settings file? 
SETTINGS = settings.cfg
FLAGS = -v 
####################################
.PHONY: proposal pdf clean pullproject
####################################


proposal: 
	make pullproject
	make xml 
	make latexFromWiki

pullproject: 
	cd bin ; python pullProject.py -s ../$(SETTINGS) $(FLAGS) 

xml:
	cd bin ; python generateXML.py -s ../$(SETTINGS) $(FLAGS) 

latexFromWiki:
	cd bin ; python latexFromWiki.py -s ../$(SETTINGS) $(FLAGS) 

clean:
	find generated/ -type f -print | grep -v README | xargs rm 

