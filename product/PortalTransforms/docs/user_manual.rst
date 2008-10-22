=============================
Portal Transforms'User manual
=============================

:Author: Sylvain Thénault
:Contact: syt@logilab.fr
:Date: $Date: 2005-08-19 23:43:41 +0200 (Fre, 19 Aug 2005) $
:Version: $Revision: 1.7 $
:Web site: http://sourceforge.net/projects/archetypes

.. contents::


What does this package provide ?
================================

This package is both a python library for MIME type based content
transformation, including a command line tool, (what i call the python package)
and a Zope product providing two new tools for the CMF (what i call the Zope
product). A python only distribution will be available, where all the Zope
specific files won't be included.



Python side
===========

The *transform* command line tool
`````````````````````````````````

    command line tool for MIME type based transformation

    USAGE: transform [OPTIONS] input_file output_file

    OPTIONS:
     -h / --help
       display this help message and exit.

     -o / --output <output mime type>
       output MIME type. (conflict with --transform)

     -t / --transform <transform id>
       id of the transform to apply. (conflict with --output)

    EXAMPLE:
     $ transform -o text/html dev_manual.rst dev_manual.html


Customization hook
``````````````````

You can customize the transformation engine by providing a module
"transform_customize" somewhere in your Python path. The module must provide a
*initialize* method which will take the engine as only argument. This method
will have the reponsability to initialize the engine with desired
transformations. When it's not found, the *initialize* method from the
*transforms* subpackage will be used.



Zope side
=========


The MIME types registry
```````````````````````

This tool registered known MIME types. The information associated with a MIME
type are :

  * a title

  * a list rfc-2046 types

  * a list of files extensions

  * a binary flag

  * an icon path

You can see regitered types by going to the *mimetypes_registry* object at the
root of your CMF site, using the ZMI. There you can modify existent information
or add / delete types. This product cames with a default set of MIME types icons
located in portal_skins/mimetypes_icons.


The tranformation tool
``````````````````````

It's a MIME type based transformation engine. It's has been designed to
transform portal content from a given MIME type to another. You can add / delete
transformations by going to the *portal_transforms* object at the root of your
CMF site, using the ZMI. Some transformations are configurable, but not all. A
transform is a Python object implementing a special interface. See the
developper documentation if you're interested in writing a new
transformation.


Archetypes integration
``````````````````````

Archetypes will use this product for automatic transformation if you have
configurated it to use the new base unit (set USE_NEW_BASEUNIT to 1 in the
Archetypes config.py). If you're using the old base unit (still default in 1.0),
the transform tool won't be used (at least by the Archetypes library).


Default transformations
=======================

The default transformations are described here. They are separated in two groups,
safe and unsafe. Safe transforms are located in the *transforms* directory of this
product. Unsafe transforms are located in the *unsafe_transforms* directory and
are not registered by default. Moreover, there is no __init__.py file in this
directory so it requires a manual intervention to make them addable to the
transforms tool. Usually unsafe transforms are so called since they allow
configuration of a path to a binary executable on the server, which may be
indesirable for Zope service providers. 


Safe transforms
```````````````

*st* 
  transforms Structured Text to HTML. Not configurable.

*rest*
  transforms Re Structured Text to HTML. You need docutils to use this
  transformation. Not configurable.

*word_to_html*
  transforms M$ Word file to HTML, using either COM (on windows), wvWare or
  PyUNO (from OpenOffice.org). Not configurable.

*pdf_to_html*
  transforms Adobe PDF to HTML. This transforms requires the "pdftohtml"
  program. Not Configurable.

*lynx_dump*
  transforms HTML to plain text. This transforms requires the "lynx"
  program. Not Configurable.

*python*
  transforms Python source code to colorized HTML. You can configure used
  colors.

*text_to_html*
  transforms plain text file to HTML by replacing new lines with
  <br/>. You can configure allowable inputs for this transform.

*rest_to_text*
  This is an example use of the *identity* transform, which does
  basically nothing :). It's used here to transform ReST files
  (text/x-rst) to text/plain. You can configure allowable inputs and
  outuput on this transform.


Unsafe transforms
`````````````````

*command*
  this is a fully configurable transform based on external commands. For
  instance, you can obtain the same transformation as the previous
  *lynx_dump*:
  
  1. add a new transform named "lynx_dump" with
     "Products.PortalTransforms.unsafe_transforms.command" as module
     (this supposes that you've added a __init__.py file to the
     unsafe_transforms directory to make them importable). 
  2. go to the configure tab of this transform and set the following
     parameters :

     :binary_path:  '/usr/bin/lynx' 

     :command_line: '-dump %s'

     :input:        'text/html'

     :output:       'text/plain'


*xml*
  this transform has been designed to handle XML file on a doctype / DTD
  basis. All the real transformation work is done by a xslt processor. This
  transform only associate XSLT to doctypes or DTD, and use give the correct
  transformation to the processor when some content has to be
  transformed.

  FIXME: add an example on how to setup docbook transform.



Advanced features
=================

Transformation chains
`````````````````````

A transformation chain is an ordered suite of transformations. A chain
itselve is a transformation. You can build a transformations chain
using the ZMI.


Transformation policy
`````````````````````

You can set a simple transformation policies for the transforms
tool. A policy say that when you try to convert content to a given
MIME type, you have to include a given transformation. For instance,
imagine you have a *html_tidy* tranformation which tidy HTML page, you
can say that the transformation path to text/html should include the
*html_tidy* transform.


Caches
``````

For efficiency, transformation's result are cached. You can set the
life time of a cached result using the ZMI. This is a time exprimed in
seconds.

