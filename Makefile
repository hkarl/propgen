

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
	make latexFromXML
	make ensureSymbolicLinks 


pullproject: 
	cd bin ; python pullProject.py -s ../$(SETTINGS) $(FLAGS) 

xml:
	cd bin ; python generateXML.py -s ../$(SETTINGS) $(FLAGS) 

latexFromWiki:
	cd bin ; python latexFromWiki.py -s ../$(SETTINGS) $(FLAGS) 

latexFromXML:
	cd bin ; python latexFromXML.py  -s ../$(SETTINGS) $(FLAGS) 
ensureSymbolicLinks:
	cd bin ; python ensureSymbolicLinks.py   -s ../$(SETTINGS) $(FLAGS) 


clean:
	find generated/ -type f -print | grep -v README | xargs rm 

