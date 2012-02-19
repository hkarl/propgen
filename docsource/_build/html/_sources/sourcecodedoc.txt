***************************
 Source code documentation
***************************


The code described here lists in the bin directory. Some general remarks: 

- The invocation sequence is pullproject -> generateXML -> latexFromWiki -> latexFromXML -> ensureSymbolicLinks 
  
- Details are in the makefile in the main directory 
  
- Many functions get passed a parameter "config". This is the content of settings.cfg, as parsed by the standard python configuration file parser ConfigParser.SafeConfigParser (see python library documentation for details). 



=============
 pullproject
=============


.. automodule:: pullProject
   :members:

============
 wikiParser
============


The wikiParser module as such
=============================
.. automodule:: wikiParser
   :members: wikiParserFactory

The wikiParser base class
=========================

.. autoclass:: wikiParser 
   :members: 
   
The moinmoin parser
=========================

.. autoclass:: wikiParserMoinmoin 
   :members:

The twiki parser
=========================

.. autoclass:: wikiParserTwiki
   :members:


=============
latexFromWiki
=============

.. automodule:: latexFromWiki
   :members:

============== 
latexFromXML
==============

.. automodule:: latexFromXML


============
settings 
============

.. automodule:: settings
   :members:

===================
ensureSymbolicLinks
===================

.. automodule:: ensureSymbolicLinks
   :members:

============
utils 
============

.. automodule:: utils
   :members:

