# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
"""
Products.ERP5.interfaces.document
"""

from zope.interface import Interface

class IDocument(Interface):
  """Document is an abstract class with all methods related to document
  management in ERP5. This includes searchable text, explicit relations,
  implicit relations, metadata, versions, languages, etc.

  Documents may either store their content directly or cache content
  which is retrieved from a specified URL. The second case if often
  referred as "External Document". Standalone "External Documents" may
  be created by specifying a URL to the contribution tool which is in
  charge of initiating the download process and selecting the appropriate
  document type. Groups of "External Documents" may also be generated from
  so-called "External Source" (refer to ExternalSource class for more
  information).

  External Documents may be downloaded once or updated at regular interval.
  The later can be useful to update the content of an external source.
  Previous versions may be stored in place or kept in a separate file.
  This feature is known as the crawling API. It is mostly implemented
  in ContributionTool with wrappers in the Document class. It can be useful
  for create a small search engine.

  There are currently two types of Document subclasses:

  * File for binary file based documents. File has subclasses such as Image,
    OOoDocument, PDFDocument, etc. to implement specific conversion methods.

  * TextDocument for text based documents. TextDocument has subclasses such
    as Wiki to implement specific methods. 
    TextDocument itself has a subclass (XSLTDocument) which provides
    XSLT based analysis and transformation of XML content based on XSLT
    templates. 

  Conversion should be achieved through the convert method and other methods
  of the conversion API (convertToBaseFormat, etc.).
  Moreover, any Document subclass must ne able to convert documents to text
  (asText method) and HTML (asHTML method). Text is required for full text
  indexing. HTML is required for crawling.

  Instances can be created directly, or via portal_contributions tool which
  manages document ingestion process whereby a file can be uploaded by http
  or sent in by email or dropped in by webdav or in some other way as yet
  unknown. The ingestion process has the following steps:

  (1) portal type detection
  (2) object creation and upload of data
  (3) metadata discovery (optionally with conversion of data to another format)
  (4) other possible actions to finalise the ingestion (ex. by assigning
      a reference)

  This class handles (3) and calls a ZMI script to do (4).

  Metadata can be drawn from various sources:

  input      -   data supplied with http request or set on the object during (2) (e.g.
                 discovered from email text)
  file_name  -   data which might be encoded in file name
  user_login -   information about user who is contributing the file
  content    -   data which might be derived from document content

  If a certain property is defined in more than one source, it is set according to
  preference order returned by a script 
     Document_getPreferredDocumentMetadataDiscoveryOrderList
     (or any type-based version since discovery is type dependent)

  Methods for discovering metadata are:

    getPropertyDictFromInput
    getPropertyDictFromFileName
    getPropertyDictFromUserLogin
    getPropertyDictFromContent

  Methods for processing content are implemented either in Document class
  or in Base class:

    getSearchableReferenceList (Base)
    getSearchableText (Base)
    index_html (overriden in Document subclasses)

  Methods for handling relations are implemented either in Document class
  or in Base class:

    getImplicitSuccessorValueList (Base)
    getImplicitPredecessorValueList (Base)
    getImplicitSimilarValueList (Base)
    getSimilarCloudValueList (Document)

  Implicit relations consist in finding document references inside
  searchable text (ex. INV-23456) and deducting relations from that.
  Two customisable methods required. One to find a list of implicit references
  inside the content (getSearchableReferenceList) and one to convert a given
  document reference into a list of reference strings which could be present
  in other content (asSearchableReferenceList).

  document.getSearchableReferenceList() returns
    [
     {'reference':' INV-12367'},
     {'reference': 'INV-1112', 'version':'012}', 
     {'reference': 'AB-CC-DRK', 'version':'011', 'language': 'en'}
    ]

  The Document class behaviour can be extended / customized through scripts
  (which are type-based so can be adjusted per portal type).

  * Document_getPropertyDictFromUserLogin - finds a user (by user_login or
    from session) and returns properties which should be set on the document

  * Document_getPropertyDictFromContent - analyzes document content and returns
    properties which should be set on the document

  * Base_getImplicitSuccessorValueList - finds appropriate all documents
    referenced in the current content

  * Base_getImplicitPredecessorValueList - finds document predecessors based on
    the document coordinates (can use only complete coordinates, or also partial)

  * Document_getPreferredDocumentMetadataDiscoveryOrderList - returns an order
    in which metadata should be set/overwritten

  * Document_finishIngestion - called by portal_activities after all the ingestion
    is completed (and after document has been converted, so text_content
    is available if the document has it)

  * Document_getNewRevision - calculates revision number which should be set
    on this document. Implementation depends on revision numbering policy which
    can be very different. Interaction workflow should call setNewRevision method.

  * Document_populateContent - analyses the document content and produces
    subcontent based on it (ex. images, news, etc.). This scripts can
    involve for example an XSLT transformation to process XML.

  Subcontent: documents may include subcontent (files, images, etc.)
  so that publication of rich content can be path independent. Subcontent
  can also be used to help the rendering in HTML of complex documents
  such as ODF documents.

  Consistency checking:
    Default implementation uses DocumentReferenceConstraint to check if the 
    reference/language/version triplet is unique. Additional constraints
    can be added if necessary.

  NOTE: Document.py supports a notion of revision which is very specific.
  The underlying concept is that, as soon as a document has a reference,
  the association of (reference, version, language) must be unique accross
  the whole system. This means that a given document in a given version in a
  given language is unique. The underlying idea is similar to the one in a Wiki
  system in which each page is unique and acts the the atom of collaboration.
  In the case of ERP5, if a team collaborates on a Text document written with
  an offline word processor, all updates should be placed inside the same object.
  A Contribution will thus modify an existing document, if allowed from security
  point of view, and increase the revision number. Same goes for properties
  (title). Each change generates a new revision.
  """

  def convert(format, **kw):
    """Call a wrapped function with CachingMethod and
    return always converted result.

    format - the format specied in the form of an extension
    string (ex. jpeg, html, text, txt, etc.)
    **kw can be various things - e.g. resolution
    """

  def generateCacheId(**kw):
    """Return string to identify Document in cache pool with
    all arguments used to convert the document
    """

  def convertToBaseFormat(**kw):
    """Converts the content of the document to a base format
    which is later used for all conversions. This method
    is common to all kinds of documents and handles
    exceptions in a unified way.

    Implementation is delegated to _convertToBaseFormat which
    must be overloaded by subclasses of Document which
    need a base format.

    convertToBaseFormat is called upon file upload, document
    ingestion by the processing_status_workflow.

    NOTE: the data of the base format conversion should be stored
    using the base_data property. Refer to Document.py propertysheet.
    Use accessors (getBaseData, setBaseData, hasBaseData, etc.)
    """

  def _convertToBaseFormat():
    """Placeholder method. Must be subclassed by classes
    which need a base format. Refer to OOoDocument
    for an example of ODF base format which is used
    as a way to convert about any file format into
    about any file format.

    Other possible applications: conversion of HTML
    text to tiddy HTML such as described here:
    http://www.xml.com/pub/a/2004/09/08/pyxml.html
    so that resulting text can be processed more
    easily by XSLT parsers. Conversion of internal
    links to images of an HTML document to local
    links (in combindation with populate).
    """

  def clearConversionCache():
    """Clear cache (invoked by interaction workflow upon file upload
    needed here to overwrite class attribute with instance attrs
    """

  def hasConversion(**kw):
    """Return a boolean if conversion is cached
    """

  def setConversion(data, mime=None, calculation_time=None, **kw):
    """Saves a version of the document in a given format; records mime type
    and conversion time (which is right now).
    """

  def getConversion(**kw):
    """Returns version of the document in a given format, if it has it; otherwise
    returns empty string (the caller should check hasConversion before calling
    this function.
    """

  def getConversionSize(**kw):
    """Returns the size of the converted document.
    """

  def _getCacheFactory():
    """Return list of cache plugins
    """

  def isSupportBaseDataConversion():
    """This is a public interface to check a document that is support conversion
    to base format and can be overridden in subclasses.
    """
