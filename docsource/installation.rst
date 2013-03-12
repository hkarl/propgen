********************* 
Installation
*********************

==================================
 Quick and dirty, virtual machine
==================================

To get your own version of PropGen up and running quickly, use the virtual machine. 

- Download it from Ubuntu One, using this link: http://ubuntuone.com/6CMWlbTtjxQtjhed24ZIkn

- It is a VirtualBox-produced Open Virtualization Appliance. It should work out of the box under VirtualBox and can (probably) be used under different hypervisors. Import it in your hypervisor. 

   - Note: under VirtualBox, it is configured to use NAT network access. There are two port forwarding rules configured for port 8080 (to access the Wiki) and 9001 (to access the Etherpad). You most probably want to check whether this is suitable for your local hypervisor setting as well. 

- Start the virtual machine. 

- Point your browser to this virtual machine, port 8080 gives the wiki, 9001 the etherpad-lite. Login into the Wiki using ProjectMaster and password 123abc. Go to http://<virtualmachine>:8080/TestProject . Click on "CreatePDF" and enjoy the PDF for a proposal. 

- Predefined accounts: 

   - Unix user: propgen , Password: abc123 
      - To change: log into the virtual machine, type "passwd" at the prompt 
   - Wiki user: ProjectMast , Password 123abc 
      - To change: log into the wiki, ??? 
   - Mysql user: root, Password: abc123 
      - To change: $ sudo dpkg-reconfigure mysql-server-5.5
   - Mysqk user: propgen, Password: abc123 
      - To change: Follow instructions here: https://github.com/Pita/etherpad-lite/wiki/How-to-use-Etherpad-Lite-with-MySQL; remember to edit ~/etherpad-lite/settings.json
 

===================================
 Quick and dirty, own installation
===================================

The fastest possible way to get everything set up and
produce a proposal PDF, assuming you have latex and python set up:  

.. code-block:: bash 

   $ cd ~/tmp 
   $ wget --no-check-certificate https://github.com/hkarl/propgen/zipball/master --output-document=propgen.zip 
   $ unzip propgen.zip 
   $ cd hkarl-propgen-7d7fd2d/  
   $ cd moin 
   $ python wikiserver.py &
   $ cd ..
   $ make 

Note: the directory name of hkarl-propgen-XXXX will
depend on the fingerprint of the current version in
github. It will vary. 

That will leave TestProject.pdf in the current directory. Use your webbrowser to go to http://127.0.0.1:8080/TestProject, make some changes to this page or to the Wiki pages linked from there, save the changes. Type make again in the shell. Gives an updated PDF file. 



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

Sphinx 
  If you should want to generate the documentation for
  the reStructuredText markup (I have no idea why you
  would want to do that), you will also need `Sphinx
  <http://sphinx.pocoo.org/>`_ , at least version
  1.1.2. In particular, you will also need the aafigure
  extension (see
  http://packages.python.org/sphinxcontrib-aafig/ ) to
  be installed and added to conf.py; affigure also
  needs a dependency repotlab. 

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
  
- Decide which Wiki to use and set it up correctly. 
  
  - Internal wiki: See :ref:`sec-setting-up-moinmoin`

  - For both internal and external wiki: simply add
    information to settings.cfg (see
    :ref:`sec-setting-up-settings-cfg`)
  
- Add the templates to an external Wiki 

  - Example templates for MoinMoin and Twiki are
    included in the templates folder. Ignore the
    directories; they are just to group the wiki files
    a bit. Each file becomes one Wiki page with the
    corresponding filename.

  - This step is not necessary when using the internal
    Wiki; it is pre-populated with an example pseudo
    project which should be easy to modify. 

  - It might make sense to rename the "TestProject" page to
    some more specific for your project. (Then, remember to
    also rename the corresponding entry in settings.cfg.)

- Once you have setup Wiki access and the Wiki is
  running, try to generate a PDF file. cd into the main
  propgen directory and type make. 

.. _sec-setting-up-moinmoin:

=======================================================
 Setting up the MoinMoin Wiki included in distribution
=======================================================

If you want to use an external wiki (e.g., an existing
Twiki), you can skip this section.

For more details, check the documentation of the
MoinMoin Wiki. 


Preconfigured account
=====================

The distributed version of MoinMoin is setup to support
accounts, require login to edit or download material,
and to deny anonymous access. 

It has a preconfigured account ProjectMaster with
password 123abc. This account ProjectMaster is
configured as a superuser in MoinMoin. Check the lines

.. code-block:: python 

   acl_rights_default = u"ProjectMaster:read,write,delete,revert,admin Known:read,write,revert,delete"

and 

.. code-block:: python

   superuser = [u"ProjectMaster"]

in the file moin/wikiconfig.py. It gives admin rights
to the ProjectMaster account, and usual read, write,
revert, delete rights to all other known accounts. 

Change password
===============

Obviously, you really, really want to change the
password of this superuser. Log in as the user for
which you want to change password, go to "Settings" (link
on the very top of the page, to the left), then click
"Change password". 

.. figure:: figures/MoinMoin-ChangePassword.png 
   :scale: 50 % 


Or go directly to
http://127.0.0.1:8080/ProjectMaster?action=userprefs&sub=changepass
(and replace "ProjectMaster" by the account name for
which you want to change the password, of course). 




Adding accounts
===============

You could stick to the preconfigured account and
distribute this account name and password to all
members of your team. However, then it will not be
possible to track who did which changes. 

Hence, it is usually preferable to assign a dedicated
username/password to each team member. 

To add a user, you need to login as the superuser
ProjectMaster. Go to the Wiki page NewUser (e.g., if
you run it locally on the default port, goto
http://127.0.0.1:8080/NewUser), and create as many
users as you like. 



Rename the main project page
============================

In case you want a different main page name, simply use
the "Rename page" action of the Wiki. Remember to
rename the corresponding setting (projectName) in
settings.cfg as well!

Run the MoinMoin Wiki
=====================

Simple: 

.. code-block:: bash 

   $ cd moin 
   $ python wikiserver.py &

You might want to start this as a daemon, possibly
start automatically after reboot. Consult your own
operating system how to do that. 



.. _sec-setting-up-settings-cfg:

=============================================
Setting up wiki in settings.cfg
=============================================

The file settings.cfg contains both basic
configurations to ensure that the download script talks
to the right wiki server as well as basic configuration
options about what kind of information to generate. The
latter content-customization options are described
elsewhere (Section :ref:`sec-settings-cfg`). Here, we concentrate on basic connectivity
settings. 

.. include:: settings.rst
   :end-before: PathNames


===================================
 Using the PropGen virtual machine
===================================

Usage, accounts, passwords
==========================

- Download the virtual machine. Run it in a hypervisor. The virtual machine is a virtualbox, but can probably convert it to some other hypervisor if needs be. 

- There is an account propgen; this is under which all the programs run. Password: abc123. You *definitely must* change the password. (Login under this account, type passwd at the prompt.) 

- change the password of the mysql server for both the root account and the propgen account: sudo dpkg-reconfigure mysql-server-5.5. The MySQL password of the propgen user must also be changed in the settings.json file in the ehterpad-lite directory! 


- Both Etherpad lite and the Moinmoin wiki are preconfigured and start at boot time. 


Notes on the virtual machine installation
=========================================

This section summaries the crucial steps to install the virtual machine that can be downloaded from Ubuntu One. It might help to setup an own installation. 

- It is a ubuntu 12.04 i386 server, with fairly minimal setup. Only OpenSSH is selected as software package in the initial selection. 

- You might want to change the keyboad layout (currently configured via console-data as a German Apple USB keyboad, no deadkeys) and possibly the locale. 

- Plain installation of ubuntu from ISO image (no hypervisor extensions installed; this is recommendable to do once you have chosen your hypervisor setup) 

- Install mysql, follwowing these instructions: https://help.ubuntu.com/11.10/serverguide/C/mysql.html (should apply to 12.04 as well...). Same password abc123, *change the password* , type sudo dpkg-reconfigure mysql-server-5.5 in terminal. Change it then in the etherpad-lite configuration correspondingly.  

- Installation of Etherpad lite follows these instructions: https://github.com/Pita/etherpad-lite . Make sure to install node.js! 

- Tell etherpad-lite to use the mysql database. Described here: https://github.com/Pita/etherpad-lite/wiki/How-to-use-Etherpad-Lite-with-MySQL . The user to use here is propgen. Note: In this description, in settings.json also needs to alter the databse entry; 'store' is incorrect (it is the table, not the database) and has to be replaced by 'etherpad-lite' in the example. In settings.json, you have to put the password given to mysql; whatever you have changed it to! 


- Install the necessary python libraries, in particular, we need 

  - pip to support python module installation http://pypi.python.org/pypi/pip (pip will pull in necessary libraries automatically) 

  .. code-block:: bash 

     $ sudo apt-get install python-pip

  - mechnize from http://wwwsearch.sourceforge.net/mechanize/ ; this should be at leat version 2.5 (note: some Linux installations seem to have older versions of mechanized installed; they are known to NOT work!) 

  .. code-block:: bash 

     $ sudo pip install mechanize 

  - Sphinx, to generate the documentation (should be version 1.1.3 or later) 

  .. code-block:: bash 

     $ sudo pip install Sphinx 


- Pull the actual distribution or propgen from github; it will include the moinmoin wiki already, with necessary adaptations. https://github.com/hkarl/propgen

  .. code-block:: bash 

    $ cd ~
    $ git clone git://github.com/hkarl/propgen.git


- Try to start the wikiserver. It should say "Running on http://127.0.0.1:8080/ ". Direct your browser there, it should deny access; click on login. Use the ProjectMaster with 123abc. 

  .. code-block:: bash 

     $ cd propgen 
     $ cd moin 
     $ python wikiserver.py 

- Let's make sure that the etherpad-lite server starts at every boot. Upstart script for etherpad-lite, copied and slightly adapted from this source http://raphael.kallensee.name/journal/etherpad-lite-auf-ubuntu-server-apache-upstart/. This script goes into /etc/init/. Note that this configuration write logs into ~/etherpad-lite/log; you might want to check them occasionally.  WARNING:  It sometimes seems so have problems connecting to the SQL database correctly. No idea why this is the case, still monitoring problem :-(. 


 .. literalinclude:: upstart/etherpad-lite.conf 
      :language: bash 



- Provide an upstart script to have the wikiserver starting at boot-time; similar logic as for the etherpad-lite upstart script. 


 .. literalinclude:: upstart/moinwiki.conf 
      :language: bash 

                       						


- Install an up-to-date TexLive. Unfortunately, even ubunutu 12.04 still comes with an 2009 texlive, far too outdated for our needs. Follow instructions here: http://www.tug.org/texlive/quickinstall.html . Note: this can take a while... 

Note: there is a little pitfall. Don't put the PATH definition in .bashrc, else the upstart script will not find the latex binaries. The texlive PATH extension has to go into ~/.profile. 









