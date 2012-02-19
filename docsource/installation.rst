********************* 
Installation
*********************

=================
 Usage scenarios
=================


External Wiki
=============

A typical usage scenario of this PropGen tool is the
following: 

- A proposal is to be prepared by a group of people. 
  
- One of them runs the wiki, or an external Wiki provider
  is used 
  
- Several people install the PropGen tool (ignoring the
  built-in Wiki) and can then built the PDF file for the
  proposal. 

- Not everybody needs to install PropGen. Ideally, a
  version control system like SVN is integrated and
  whoever generates a new PDF file commits it to this
  version control system. Then, everybody has access to
  reasonably up-to-date versions.  

This scenario is fairly straightforward to set up. I
assume here that you have your external Wiki set up and
know how to administer it. 


Built-in Wiki
=============

An alternative is to use the MoinMoin Wiki included in
the PropGen distribution. Then, one partner has to run
this wiki. Ideally and typically, the same machine is
then able to run PropGen and to generate the proposal
PDF. This can conveniently be triggered via a crontab
(e.g., do an hourly build) and the result can be put
into a version control system similar to above. 

If other partners want to setup PropGen as well to
locally generate the PDF, that is no problem at all. 

Advantage of this approach is that the generation scripts can
directly talk to the wiki and there is no need to go
over the network to pull the wiki files. This is
substantially more reliable, faster, and easier to
setup (in particular, if there are firewalls or proxies
in place, which can be real trouble). The disadvantage
is that often, a Wiki is already in place, people have
their accounts on it, are accustomed to its syntax and
quirks, it can have powerful features not present in
the provided MoinMoin installation (e.g, Twiki has a
very useful butracker that can be very beneficial
during proposal writing). The choice is yours!  

Integrating a version control system
====================================

As outlined above, it can be extremely useful to
integrate a version control system like SVN. I would
recommend to limit this to the latex directory, only
committing files in this directory. 

Nothing is done automatically here since the variety of
VCS systems is large. But it should be a simple
exercise to integrate corresponding commit commands in
the Makefile. 

However, some care has to be taken in that symbolic
links from the LaTeX directory to the "generated"
directory are used. The reason is that it can be
convenient, towards the end of a proposal preparation
process, to stop pulling some parts of a proposal from
the Wiki and to rather work on the LaTeX files
directly. This allows better fine-tuning then working
via the Wiki. The process is simple: replace the
symbolic link by the actual file. Then, this file is
used and it is not touched by the generation process.

=====================
 Actual installation
=====================

Prerequisites
=============

You need the following software installed: 

Python 
  You will need Python version 2.7.2 or
  later. Python 3 is known not to work at this time,
  Python 2.6 is too old. 

Mechanize
  If you want to pull in Wiki files over the
  network (e.g., from a remote Twiki), then you need the
  python mechanize module installed. Details can be found
  on the `Mechanize webpage <http://wwwsearch.sourceforge.net/mechanize/>`_. 

Tex
  An up-to-date LaTeX installation. TexLive 2011 was
  used for development. Non-standard packages or packages
  which needed patches are provided in the distribution. 

Make
  There is a simple makefile in place. It is not
  absolutely needed and could quite easily be replaced by
  shell scripts or batch files.

Bash
  The makefile uses some simple loop and test
  constructs of bash. (See the clean target, e.g.) It
  should not be difficult to do without or provide a
  version for another shell. 

Operation system
  Development and testing took place on Mac OSX
  Snow Leopard. Normal Linux distributions should pose no
  problems at all. Installation on Window is likely to be
  problematic because of symbolic links, and makefiles,
  bash etc. is likely to require at least cygwin - but I
  have very little clue of Windows and dare not make any
  statements here. Your mileage might vary. 

Installation
============

- Download the PropGen package and unpack to a folder of
  your choice. 
  
  - From github: 

    - Main page: https://github.com/hkarl/propgen

    - GIT Read-Only: git://github.com/hkarl/propgen.git

    - ZIP file:
      https://github.com/hkarl/propgen/zipball/master

  - Other sources still to come (possibly even a virtual
    machine) 
  
- Decide which Wiki to use 
  
  - Internal wiki: See details below 

  - External wiki: simply add information to settings.cfg
    (see below) 
  
- Add the templates to an external Wiki 


Example templates for MoinMoin and Twiki are included
in the templates folder. Ignore the directories; they
are just to group the wiki files a bit. Each file
becomes one Wiki page with the corresponding filename. 

This step is not
necessary when using the internal Wiki, it is
pre-populated with an example pseudo project

  
- Once you have setup Wiki access and the Wiki is
  running, try to generate a PDF file 


=======================================================
 Setting up the MoinMoin Wiki included in distribution
=======================================================

If you want to use an external wiki (e.g., an existing
Twiki or the included MoinMoin wiki running on another
machine), you can skip this section.


Preconfigured accounts
======================


Adding accounts
===============

Run the MoinMoin Wiki
=====================



=============================================
 Setting up settings.cfg - Which Wiki to use
=============================================



