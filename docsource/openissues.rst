******************************* 
Open Issues
******************************* 


========================== 
Known bugs 
========================== 

None, of course :-). If you find any, let me know! 

========================== 
Things still to do (TODO)
========================== 

Nothing immediately obvious. 

==========================  
Debatable aspects
========================== 

#. The settings and the latexTemplates files could be put on the Wiki
   as well. Two-edged sword: Might make it easier for everybody to
   configure things, but that is a serious downside as
   well. Technically, this would not be difficult to do. Not made up
   my mind yet.

==========================  
Ideas for future features
========================== 

1. Integrate a version control system like SVN for
   the produced LaTeX files 
2. Build a bridge to the financial planning of a
   project. 

  - Either by parsing from/ writing to an Excel
    (or similar) spreadsheet. Relatively easy, but
    hard to make this general. (This is currently implemented in rudimentary form)  
  
  - Or by putting spreadsheet-functionality onto
    the wiki. Hard to do for different wiki types
    (a nightmare, probably). 

3. Build support for latexdiff. Possibly triggered
   from wiki as well? 
4. Better support for figures in both wiki and latex. One idea might be
   to upload a PDF to the wiki and have the Wiki convert it to a PNG
   file. And then pull the PDF file directly from the wiki, without
   need to manually put it in the LaTeX figure directory.
