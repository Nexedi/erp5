How to develop ERP5 Appliance Buildout
======================================

Normal buildout run assumes that all resources are available over the network.
And this is correct way to use buildout, but...how to develop it locally and
still be sure that it run over the network.

Lets assume that software is available in ~/erp5.buildout.

Create your working directory ~/buildout.devel:

  $ mkdir ~/buildout.devel

Now checkout the buildout:

~/erp5.buildout/parts/subversion/bin/svn https://svn.erp5.org/repos/public/erp5/trunk/buildout/ ~/buildout.devel/checkout

Start simple http server there:

  $ cd ~/buildout.devel/checkout
  $ ~/erp5.buildout/bin/python2.6 -m SimpleHTTPServer 9000 # or any other free port

Now create directory to simulate extending over the network:

  $ mkdir ~/buildout.devel/work

And create profile there:

  $ cat > ~/buildout.devel/work/buildout.cfg
[buildout]
extends = http://localhost:9000/buildout-2.12.cfg
extends-cache = extends-cache
^D

Now it is time to play. Observe what and how is downloaded from your simulated
server.

Happy hacking!

Simple server idea contributed by Lucas Carvalho Teixeira
