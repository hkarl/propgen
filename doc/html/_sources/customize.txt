******************************* 
How to customize PropGren
*******************************


This section explains how the resulting PDF file can be customized. 

==========================  
Simple customization
========================== 

Simple customizations can be done in settings.cfg; section :ref:`sec-settings-cfg` gives a detailed description of all the available values. 

In particular, the section CustomLaTeX gives a lot of flexibility: you
can put python expressions there, evaluating on the main variables
describing the project, and generate LaTeX code directly from it. Such
expressions are then turned into LaTeX commands, directly accessible
by writing them down in Wiki text.



=========================== 
 Customize LaTeX templates 
=========================== 

More powerful customization is available via the LaTeX templates in the file latexTemplate.cfg. Essentially, this give a small templating engine where LaTeX code can be put into variables, and the LaTex code can contain variable names to be replaced before the actual LaTeX is generated. 

Almost all of the generated LaTeX code (ending up in generated/latex in the end) is controlled by this file. There are a few exceptions - notably, the headers of the workpackage is too complex to do via the templating engine; the files including the individual partner files and WP files are also generated  automatically since they are fairly straightforward. 

Details are explained in :ref:`sec-latexTemplates-cfg`; how to use the various options in this file is described in detail in the function generateTemplates in the source code of the latexFromXML.py module :ref:`seclatexFromXML`. 


========================== 
Complex customization
========================== 

For even deeper customization, you have to modify either the main.tex file (in the latex directory) or the Python scripts (in directory bin).  This gives totally flexibility, but you really should understand what you are doing here. 
