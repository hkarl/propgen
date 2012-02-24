********************************
Directory layout and major files
********************************

This section summarizes the directory layout as used in the standard
distribution setup. It is possible to widely reconfigure this (via the
PathNames section in settings.cfg); however, unless there are concrete
reasons to change it, it seems reasonable not to modify this. 

=====================
 Directory structure
=====================

bin 
   All the Python scripts necessary to generate the proposal PDF are
   here. 

doc
   The documentation in various formats. 

docsource
   The sources for the documentation, in reStructuredText, based on
   Sphinx. 

generated
   This directory contains all intermediately downloaded or generated
   files. It has several subdirectories: 

   latex 
      All the generated LaTeX files go in here. Files in the directory
      as such are direct transliterations of the corresponding Wiki
      files. There are a few subdirectories: 
      
      figures
         All *generated* tables,
         gantts, and pie charts go in here (in respective
         subdirectories). 
	
      partners 
         Files pertaining to the description of partners. 

      wp 
         Files pertaining to individual workpackages. One file per
         workpackage, containing all relevant information. 
 	 

   wiki
      The raw download of the wiki sources. Very useful for error
      checking, in case some of the download fails, problems with
      special characters (e.g., Umlaute) appear, etc. Files in here
      should be verbatim copies of all the Wiki pages pertaining to
      the project. In particular, there are two further
      subdirectories: 

      partners 
         All the partner description files, as linked from the Partner
         Description part of the main project page. 

      wp 
         All the workpackage wiki pages, as linked from the
         workpackage description part of the main page. 

   xml
      A directory containing all intermediately generated XML
      files. Workpackage-specific information goes into the
      subdirectory wp. One file per workpackage. All the partner
      descriptions go in one LaTeX file. 

      The purpose of the intermediate XML representation is to give
      secondary tools a standard way to hook in (and it is a legacy of
      an older version of the program). 

latex
   This directory contains all the manually added LaTeX files, as well
   as the root main.tex file invoked by pdflatex. Feel free to add any
   files you like in here. 

   It has a few subdirectories: 

   figures 
      By convention, all figures necessary for the proposal go in
      here. In addition, there are subdirectories gantts, pies, tables
      pointing to generated material. 

   partners 
      Same purpose as above. 

   styles
      All specific, non-standard, unusual or modified style files are
      collected here.  

   wp 
      Same purpose as above. 
  
   In addition, there are symbolic links pointing from this directory
   to the directory generated, to each of the automatically generated
   files. This is done by the script ensureSymbolicLinks.py. The idea
   is to keep files on the Wiki as long as possible. But if, at some
   point in time, a file should be maintained only manually, remove
   the symbolic link, copy the generated file to the this directory,
   and the generation scripts will no longer overwrite this file; all
   manual changes are preserved. (Obviously, you should make it clear
   on the wiki that the wiki version is out of date.) 

moin 
   A distribution of the MoinMoin wiki, adapted to the needs of a
   project proposal. In particular, restricted login and a
   pre-configured superuser. 

template 
   All template files. It contains, for each supported wiki type, an
   example setup of the example project, separated by
   subdirectory. Currently, moinmoin and twiki. 
   See also below for latexTemplates.cfg. 



================
 Relevant files
================


settings.cfg
   This file contains main configuration options: where to find the
   Wiki, which information to include, some basic settings about the
   look of the PDF file. See :ref:`sec-settings-cfg` for the actual
   source code and detailed documentation. 

template/latexTemplates.cfg
   In here, all the templates used to produce actual LaTeX code are
   maintained. Changes here allow a fine-grained customization of the
   result. See :ref:`sec-latexTemplates-cfg` for the actual source
   code and detailed documentation. 


latex/main.tex
   The main LaTeX file; from here, all other LaTeX files are
   included. You can change a lot of the behavior here, e.g., include
   other style files. This file is never manipulated automatically,
   feel free to make manual adjustments here. See :ref:`sec-mainLaTeX` for details. 

latex/warnings.tex 
   All warning generated during the production of XML or LaTeX code
   are collected here and can be typeset directly. The showWarnings
   flag in settings.cfg controls whether these warnings are included
   in the PDF output.

latex/settings.tex
   This file is produced from settings.cfg by turning all the
   True/False flags in this file into a corresponding LaTeX variable
   (which can be queried via the ifthenelse command). It also contains
   the *results* of executing all the  commands in  the CustomLaTeX
   section of settings.cfg, made accessible via a corresponding LaTeX
   variable. 

latex/partners/partnersIncluder.tex
   A small file, generated to make sure that all downloaded partner
   descriptions are included. No need to change anything manually when
   a new partner is added. 

latex/wp/wpIncluder.tex 
   Similarly, a file to include all workpackage description files. 

Makefile
   A standard Makefile guiding the generation process. It is fairly
   straightforward, simply running the consecutive steps of a build
   process after each other for the main target *pdf*. See
   :ref:`sec-Makefile` for details. 

projectname.pdf 
   The ultimate PDF file. "projectname" is replaced by the value you
   gave in settings.cfg's projectName option. In the example setup, it
   will be called TestProject.pdf. 

