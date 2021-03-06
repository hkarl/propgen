# See LICENCE file for licencing information 

# Where is the settings file? PAth is relative to the main directory (same as this Makefile) 
SETTINGS = settings.cfg

# Which flags to use? -v is verbose for all scripts; 
# in production use, -v is usually not necessary
# FLAGS = -v 
FLAGS =

LATEXBIN = pdflatex -interaction=nonstopmode

# Relevant path names. They are extracted from settings.cfg 

PROJECTNAME  = $(strip $(shell grep "projectName " ${SETTINGS} | cut -f 2 -d = ))
BINPATH = $(shell grep "binpath " ${SETTINGS} | cut -f 2 -d = )
WIKIPATH = $(shell grep "wikipath " ${SETTINGS} | cut -f 2 -d = )
XMLPATH = $(shell grep "xmlpath " ${SETTINGS} | cut -f 2 -d = )
LATEXPATH = $(strip $(shell grep "manuallatexpath " ${SETTINGS} | cut -f 2 -d = ))
GENERATEDLATEXPATH = $(shell grep "genlatexpath " ${SETTINGS} | cut -f 2 -d = )
LATEXLINKS =  $(shell find ${LATEXPATH} -type l)

####################################
.PHONY: proposal pdf clean pullproject xml latexFromWiki latexFromXML ensureSymbolicLinks fullcommit doc docclean

####################################


proposal: 
	make pullproject
	make xml 
	make latexFromWiki
	make latexFromXML
	make ensureSymbolicLinks 


pullproject: 
	cd ${BINPATH} ; python pullProject.py -s ../$(SETTINGS) $(FLAGS) 

xml:
	cd ${BINPATH} ; python generateXML.py -s ../$(SETTINGS) $(FLAGS) 

latexFromWiki:
	cd ${BINPATH} ; python latexFromWiki.py -s ../$(SETTINGS) $(FLAGS) 

latexFromXML:
	cd ${BINPATH} ; python latexFromXML.py  -s ../$(SETTINGS) $(FLAGS) 

ensureSymbolicLinks:
	cd ${BINPATH} ; python ensureSymbolicLinks.py   -s ../$(SETTINGS) $(FLAGS) 

pdf: 
	cd ${LATEXPATH}; ${LATEXBIN} main; bibtex main; ${LATEXBIN} main; ${LATEXBIN} main
	cp ${LATEXPATH}/main.pdf ${PROJECTNAME}.pdf


clean:
	-find ${WIKIPATH} -type f -print | grep -v README | xargs rm 
	-find ${XMLPATH} -type f -print | grep -v README | xargs rm 
	-find ${GENERATEDLATEXPATH} -type f -print | grep -v README | xargs rm 
	# remove empty symbolic links from latex path - this is debatable! 
	-cd ${LATEXPATH} ; rm -f main.aux main.lof main.log main.lot main.lox main.out main.toc main.bbl main.blg 
	-for d in ${LATEXLINKS}; do test ! -e $$d && rm $$d ; done  

moinpdf:
	-rm logfile
	make clean
	make proposal > logfile
	make pdf  >> logfile 
	cp ${PROJECTNAME}.pdf "moin/wiki/data/pages/${PROJECTNAME}/attachments/"
	cp logfile "moin/wiki/data/pages/${PROJECTNAME}/attachments/logfile.txt"
	tar cfhz ${PROJECTNAME}.tgz latex 
	mv ${PROJECTNAME}.tgz "moin/wiki/data/pages/${PROJECTNAME}/attachments/"


doc:
	cd docsource ; make install 
doclean:
	find doc -type f -print | grep -v README | xargs rm 

fullcommit: 
	make clean 
	make proposal 
	make pdf 
	cd docsource ; make install
	make clean 
	git commit -a -m "a full commit triggered by the makefile" 

