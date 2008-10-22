===================================
How to setup PyUNO for zope
===================================

:Author: Junyong Pan <panjy at zopechina.com>, Anton Stonor <stonor@giraffen.dk>
:Date: $Date: 2003-08-12 02:50:50 -0800 (Tue, 12 Aug 2003) $
:Version: $Revision: 1.5 $

(to be refined)

Portal Transforms allows you to convert Word documents to HTML. A cool
feature
if you want to preview Word documents at your web site or use Word as a web
authoring tool.

To do the actual transform, Portal Transforms rely on a third party
application
to do the heavy lifting. If you have not installed such an application,
Portal
Transforms will not perfom Word to HTML transforms.

One of the options is Open Office. It is not the easiest application to
set up
to work with Portal Transforms, but it works on both Windows and Unix
and delivers
fairly good HTML.

Problems
====================
- PyUNO is cool, but PyUNO now ship with its own python intepreter, which is not compatible with zope's
- PyUNO is not threadsafe now.

SETTING UP OPEN OFFICE ON WINDOWS
=======================================

WARNING: You can setup pyuno, but you can't use it concurrently. see 'Install oood'

1) Install Open Office 2.0

   Just run the standard installer.

   Pyuno in this version ship with python 2.3, which is compatible with Zope 2.7

2) Set the environment PATH
Add the Open Office program dir to the Windows PATH, e.g.
C:\Program Files\OpenOffice.org 1.9.82\program

See this article on how to set the Windows PATH:
http://vlaurie.com/computers2/Articles/environment.htm

You can also look at the python.bat (located in your Open Office program
dir)
for inspiration.

3) Set the PYTHONPATH
You need to add these directories to the PYTHONPATH:
a) The Open Office program dir (e.g. C:\Program Files\OpenOffice.org
1.9.82\program)
b) The Open Office python lib dir (e.g. C:\Program Files\OpenOffice.org
1.9.82\program\python-core-2.3.4\lib)

From the Windows system shell, just run e.g.:
set PYTHONPATH= C:\Program Files\OpenOffice.org 1.9.82\program
set PYTHONPATH=  C:\Program Files\OpenOffice.org
1.9.82\program\python-core-2.3.4\lib

You can also look at the python.bat (located in your Open Office program
dir) for inspiration.

4) Start Open Office as UNO-server
Run soffice "-accept=socket,host=localhost,port=2002;urp;"

5) Now it should work

For Debian Linux Users
=========================

see: http://bibus-biblio.sourceforge.net/html/en/LinuxInstall.html

1. install version 1.1, which doesn't contain pyuno::

    apt-get install openoffice

2. install a version of pyuno which enable ucs4 unicode

   - you can download at http://sourceforge.net/projects/bibus-biblio/

   - copy to /usr/lib/openoffice/program

3. set up environment variables

    OPENOFFICE_PATH="/usr/lib/openoffice/program"
    export PYTHONPATH="$OPENOFFICE_PATH"
    export LD_LIBRARY_PATH="$OPENOFFICE_PATH"

Install oood
===================

Note, this product is for linux only

http://udk.openoffice.org/python/oood/

UNDERSTANDING OPEN OFFICE AND UNO
=============================================
Open Office allows programmers to remotely control it. Portal Transforms
takes
advantage of this opportunity by scripting Open Office from Python. It
is possible
through PyUNO that exposes the Open Office API in Python.

Now, you can't download and install PyUNO as a module for your the Python
interpreter that is running your Zope server. PyUNO only comes bundled
with Open
Office and the Python that is distributed with Open Office. To make
PyUNO work
from within your standard Python you must expand the PYTHONPATH as done
above so
Python also will look inside Open Office for modules. If it works you
should be
able to start up a Python shell and do

>>>import uno

In some cases you can be unlucky and the Python used for Zope is not in
sync with
the Python that is distributed with Open Office. That is solved by
rebuilding
Python -- a task that is beyond the scope of this guide.

