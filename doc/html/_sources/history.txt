*****************
 Version history
*****************

Version 0.2 (April 19, 2013): 

- Budget information can be handled via a table in the main project page. Actual cost data is then computed based on actual person months assigned in the projects and based on the type of workpackages (research vs. management) and partners (industry vs. academic). Highly configurable rules; no need for Excel files any more. Alternatively, there is shaky support for reading budget data from an Excel file, but that is not well supported. 

- Better support for the moinmoin figure inclusion syntax; not possible to specify captions and labels directly 

- Handling of ampersands rewritten. Hopefully simplified the interface and removed a number of pitfalls. 

- Person months can now be floats; no longer need to be integers. However, this is not well tested yet and should be considered an experimental feature. 

- wikiParser got various overhauls. In particular, handling with verbatim environments was simplified (nesting is no longer allowed, which never made much sense anyway), which resulted in BIG speedup for the wiki parsing (easily a factor of ten faster now). 

- Labels for figures no longer automatically generate a fig: prefix. Despite being convenient, it turned out to be simply too confusing (this breaks backward compatibility, but is easiy to fix; look for fig: in wikiParser.py)

- Various small bugs removed (e.g., partners were not filtered correctly in the task tables). 

- Various small additions (e.g., additional pie charts for budget distribution  defined). 

Outlook: 

- Twiki is supported is on the list of endangered modules, since I am not using twiki any longer. Use at your own risk!


Version 0.1: 

- First released version 
