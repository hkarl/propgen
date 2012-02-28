***************************
 Source code documentation
***************************


The code described here lists in the bin directory. Some general remarks: 

- The invocation sequence is pullproject -> generateXML -> latexFromWiki -> latexFromXML -> ensureSymbolicLinks 
  
- Details are in the makefile in the main directory 
  
- Many functions get passed a parameter "config". This is the content of settings.cfg, as parsed by the standard python configuration file parser ConfigParser.SafeConfigParser (see python library documentation for details). 


.. aafig::
   :aspect: 60
   :scale: 150
   :proportional:
   :textual:


			      +------------+
			      | pullProject|
			      +-----+------+
				    |
				    |
				    v
			    +-----------------+
	   +----------------+  generated wiki |
	   | 	            +--------+--------+
	   |	                     |	     
	   |	                     |	     
	   |	                     v	     
	   |	               +------------+ 
	   |	               | generateXML| 
	   |	               +-----+------+ 
	   |	                     |	     
	   |	                     |	     
	   |	                     v	     
	   |	             +---------------+
	   |	             | generated xml |
	   |	             +--------+------+
	   |	                      |
	   |	                      |
	   |	                      |                 
	   |	                      |                 
	   v	                      v                 
      +-------------+           +------------+                
      +latexFromWiki|           |latexFromXML|         	 
      +----+--------+           +-----+------+         	 
	   |	                      |                
	   |    +---------------------+-----------------------+
	   |    |                     |                       |
	   |    |                     |                       |
	   v    v                     v                       v
   +-----------------+    +--------------------+  +--------------------------+
   | generated latex |    | generated latex wp |  | generated latex partners |
   +-------+---------+    +-----------+--------+  +-----------+--------------+
	   |                          |                       |
	   |                          |                       |
	   +--------------------------+-----------------------+
				      |
				      |
				      v
			  +-----------+--------+
			  | ensureSymbolicLinks|
			  +-----------+--------+
				      |
	  +---------------------------+----------------------------+
	  |                           |                            |
	  v                           v                            v
     +-------+                   +----------+            +----------------+
     | latex |                   | latex wp |            | latex partners |
     +-------+                   +----------+            +----------------+










=============
 pullproject
=============


.. automodule:: pullProject
   :members:


.. _sec-wiki-parser:

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


.. _seclatexFromXML:

============== 
latexFromXML
==============

.. automodule:: latexFromXML
   :members:

=========================================================
 latexFromXML - key/value pairs used in global variables
=========================================================

.. include:: latexfromXMLKeyValue.rst 


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

.. _sec-settings-cfg:

==============
 settings.cfg
==============

.. include:: settings.rst

.. _sec-latexTemplates-cfg:


==================
latexTemplates.cfg
==================

This file contains the input for a little templating engine. 

.. include:: latexTemplates.rst 



.. _sec-Makefile:


==========
 Makefile
==========

# .. code-block:: make
 
.. literalinclude:: ../Makefile 
   :language: make 


.. _sec-mainLaTeX:

==========
 main.tex
==========

TODO 

.. literalinclude:: ../latex/main.tex
   :language: latex 

