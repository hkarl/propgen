

# where is the settings file? 
SETTINGS = settings.cfg

# which flags to use? -v is verbose for all scripts 
FLAGS = -v 


### extract relevant path names from settings.cfg 

BINPATH = `grep "binpath " ${SETTINGS} | cut -f 2 -d = `
WIKIPATH = `grep "wikipath " ${SETTINGS} | cut -f 2 -d = `
XMLPATH = `grep "xmlpath " ${SETTINGS} | cut -f 2 -d = `
LATEXPATH = `grep "manuallatexpath " ${SETTINGS} | cut -f 2 -d = `
GENERATEDLATEXPATH = `grep "genlatexpath " ${SETTINGS} | cut -f 2 -d = `

####################################
.PHONY: proposal pdf clean pullproject xml latexFromWiki latexFromXML ensureSymbolicLinks
####################################


proposal: 
	make pullproject
	make xml 
	make latexFromWiki
	make latexFromXML
	make ensureSymbolicLinks 


pullproject: 
	cd ${BINDIR} ; python pullProject.py -s ../$(SETTINGS) $(FLAGS) 

xml:
	cd ${BINDIR} ; python generateXML.py -s ../$(SETTINGS) $(FLAGS) 

latexFromWiki:
	cd ${BINDIR} ; python latexFromWiki.py -s ../$(SETTINGS) $(FLAGS) 

latexFromXML:
	cd ${BINDIR} ; python latexFromXML.py  -s ../$(SETTINGS) $(FLAGS) 

ensureSymbolicLinks:
	cd ${BINDIR} ; python ensureSymbolicLinks.py   -s ../$(SETTINGS) $(FLAGS) 

pdf: 
	cd ${LATEXPATH}; pdflatex main; bibtex main; pdflatex main; pdflatex main 


clean:
	find ${WIKIPATH} -type f -print | grep -v README | xargs rm 
	find ${XMLPATH} -type f -print | grep -v README | xargs rm 
	find ${GENERATEDLATEXPATH} -type f -print | grep -v README | xargs rm 


