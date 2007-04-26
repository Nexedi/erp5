##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

import re, socket
from DateTime import DateTime
from operator import add
from xmlrpclib import Fault
from zLOG import LOG, INFO
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base
from Globals import PersistentMapping
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.WebDAVSupport import TextContent
from Products.ERP5Type.Message import Message
from Products.ERP5Type.Utils import convertToUpperCase, convertToMixedCase
from Products.ERP5.Document.Url import UrlMixIn
from Products.ERP5.Tool.ContributionTool import MAX_REPEAT

_MARKER = []
VALID_ORDER_KEY_LIST = ('user_login', 'content', 'file_name', 'input')
# these property ids are unchangable
FIXED_PROPERTY_IDS =  ('id', 'uid', 'rid', 'sid') 

def makeSortedTuple(kw):
  items = kw.items()
  items.sort()
  return tuple(items)

class SnapshotMixin:
  """
    This class provides a generic API to store in the ZODB
    PDF snapshots of objects and documents with the
    goal to keep a facsimile copy of documents as they
    were at a given date.
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ModifyPortalContent, 'createSnapshot')
  def createSnapshot(self):
    """
      Create a snapshot (PDF). This is the normal way to modifiy
      snapshot_data. Once a snapshot is taken, a new snapshot
      can not be taken.

      NOTE: use getSnapshotData and hasSnapshotData accessors
      to access a snapshot.

      NOTE2: implementation of createSnapshot should probably
      be delegated to a types base method since this it
      is configuration dependent.
    """
    if self.hasSnapshotData():
      raise ConversionError('This document already has a snapshot.')
    self._setSnapshotData(self.convert(format='pdf'))

  security.declareProtected(Permissions.ManagePortal, 'deleteSnapshot')
  def deleteSnapshot(self):
    """
      Deletes the snapshot - in theory this should never be done.
      It is there for programmers and system administrators.
    """
    try:
      del(self.snapshot_data)
    except AttributeError:
      pass

class ConversionError(Exception):pass

class ConversionCacheMixin:
  """
    This class provides a generic API to store in the ZODB
    various converted versions of a file or of a string.

    Versions are stored in dictionaries; the class stores also
    generation time of every format and its mime-type string.
    Format can be a string or a tuple (e.g. format, resolution).

    TODO:
    * Implement ZODB BLOB
  """
  # time of generation of various formats
  _cached_time = None # Defensive programming - prevent caching to RAM
  # generated files (cache)
  _cached_data = None # Defensive programming - prevent caching to RAM
  # mime types for cached formats XXX to be refactored
  _cached_mime = None # Defensive programming - prevent caching to RAM

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ModifyPortalContent, 'clearConversionCache')
  def clearConversionCache(self):
    """
    Clear cache (invoked by interaction workflow upon file upload
    needed here to overwrite class attribute with instance attrs
    """
    self._cached_time = PersistentMapping()
    self._cached_data = PersistentMapping()
    self._cached_mime = PersistentMapping()

  security.declareProtected(Permissions.View, 'updateConversionCache')
  def updateConversionCache(self):
    aself = aq_base(self)
    if not hasattr(aself, '_cached_time') or self._cached_time is None:
      self._cached_time = PersistentMapping()
    if not hasattr(aself, '_cached_data') or self._cached_data is None:
      self._cached_data = PersistentMapping()
    if not hasattr(aself, '_cached_mime') or self._cached_mime is None:
      self._cached_mime = PersistentMapping()

  security.declareProtected(Permissions.View, 'hasConversion')
  def hasConversion(self, **format):
    """
      Checks whether we have a version in this format
    """
    self.updateConversionCache()
    return self._cached_data.has_key(makeSortedTuple(format))

  security.declareProtected(Permissions.View, 'getCacheTime')
  def getCacheTime(self, **format):
    """
      Checks when if ever was the file produced
    """
    self.updateConversionCache()
    return self._cached_time.get(makeSortedTuple(format), 0)

  security.declareProtected(Permissions.ModifyPortalContent, 'updateConversion')
  def updateConversion(self, **format):
    self.updateConversionCache()
    self._cached_time[makeSortedTuple(format)] = DateTime()

  security.declareProtected(Permissions.ModifyPortalContent, 'setConversion')
  def setConversion(self, data, mime=None, **format):
    """
    Saves a version of the document in a given format; records mime type
    and conversion time (which is right now).
    """
    self.updateConversionCache()
    tformat = makeSortedTuple(format)
    if mime is not None:
      self._cached_mime[tformat] = mime
    if data is not None:
      self._cached_data[tformat] = data
      self.updateConversion(**format)
    self._p_changed = 1

  security.declareProtected(Permissions.View, 'getConversion')
  def getConversion(self, **format):
    """
    Returns version of the document in a given format, if it has it; otherwise
    returns empty string (the caller should check hasConversion before calling
    this function.

    (we could be much cooler here - pass testing and updating methods to this function
    so that it does it all by itself; this'd eliminate the need for setConversion public method)
    XXX-BG: I'm not sure now what I meant by this...
    """
    self.updateConversionCache()
    tformat = makeSortedTuple(format)
    return self._cached_mime.get(tformat, ''), self._cached_data.get(tformat, '')

  security.declareProtected(Permissions.ViewManagementScreens, 'getConversionCacheInfo')
  def getConversionCacheInfo(self):
    """
    Get cache details as string (for debugging)
    """
    self.updateConversionCache()
    s = 'CACHE INFO:<br/><table><tr><td>format</td><td>size</td><td>time</td><td>is changed</td></tr>'
    for f in self._cached_time.keys():
      t = self._cached_time[f]
      data = self._cached_data.get(f)
      if data:
        if isinstance(data, str):
          ln = len(data)
        else:
          ln = 0
          while data is not None:
            ln += len(data.data)
            data = data.next
      else:
        ln = 'no data!!!'
      s += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (f, str(ln), str(t), '-')
    s += '</table>'
    return s


class Document(XMLObject, UrlMixIn, ConversionCacheMixin, SnapshotMixin):
  """
      Document is an abstract class with all methods
      related to document management in ERP5. This includes
      searchable text, explicit relations, implicit relations,
      metadata, versions, languages, etc.

      Documents may either store their content directly or
      cache content which is retrieved from a specified URL.
      The second case if often referred as "External Document".
      Standalone "External Documents" may be created by specifying
      a URL to the contribution tool which is in charge of initiating
      the download process and selecting the appropriate document type.
      Groups of "External Documents" may also be generated from
      so-called "External Source" (refer to ExternalSource class
      for more information).

      External Documents may be downloaded once or updated at
      regular interval. The later can be useful to update the content
      of an external source. Previous versions may be stored
      in place or kept in a separate file. This feature
      is known as the crawling API. It is mostly implemented
      in ContributionTool with wrappers in the Document class.
      It can be useful for create a small search engine.

      There are currently two types of Document subclasses:

      * File for binary file based documents. File
        has subclasses such as Image, OOoDocument,
        PDFDocument, etc. to implement specific conversion
        methods.

      * TextDocument for text based documents. TextDocument
        has subclasses such as Wiki to implement specific
        methods. TextDocument itself has a subclass
        (XSLTDocument) which provides XSLT based analysis
        and transformation of XML content based on XSLT
        templates. 

      Document classes which implement conversion should use
      the ConversionCacheMixin class so that converted values are
      stored inside ZODB and do not need to be recalculated.
      More generally, conversion should be achieved through
      the convert method and other methods of the conversion
      API (convertToBaseFormat, etc.). Moreover, any Document
      subclass must ne able to convert documents to text
      (asText method) and HTML (asHTML method). Text is required
      for full text indexing. HTML is required for crawling.

      Instances can be created directly, or via portal_contributions tool
      which manages document ingestion process whereby a file can be uploaded
      by http or sent in by email or dropped in by webdav or in some other
      way as yet unknown. The ingestion process has the following steps:

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

      Methods for processing content are implemented either in 
      Document class or in Base class:

        getSearchableReferenceList (Base)
        getSearchableText (Base)
        index_html (overriden in Document subclasses)

      Methods for handling relations are implemented either in 
      Document class or in Base class:

        getImplicitSuccessorValueList (Base)
        getImplicitPredecessorValueList (Base)
        getImplicitSimilarValueList (Base)
        getSimilarCloudValueList (Document)

      Implicit relations consist in finding document references inside
      searchable text (ex. INV-23456) and deducting relations from that.
      Two customisable methods required. One to find a list of implicit references
      inside the content (getSearchableReferenceList) and one to convert a given
      document reference into a list of reference strings which could
      be present in other content (asSearchableReferenceList).

      document.getSearchableReferenceList() returns
        [
         {'reference':' INV-12367'},
         {'reference': 'INV-1112', 'version':'012}', 
         {'reference': 'AB-CC-DRK', 'version':'011', 'language': 'en'}
        ]

      The Document class behaviour can be extended / customized through scripts
      (which are type-based so can be adjusted per portal type).

      * Document_getPropertyDictFromUserLogin - finds a user (by user_login or from session)
        and returns properties which should be set on the document

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
    the association of (reference, version, language) must be unique
    accross the whole system. This means that a given document in a given
    version in a given language is unique. The underlying idea is similar
    to the one in a Wiki system in which each page is unique and acts
    the the atom of collaboration. In the case of ERP5, if a team collaborates
    on a Text document written with an offline word processor, all
    updates should be placed inside the same object. A Contribution
    will thus modify an existing document, if allowed from security
    point of view, and increase the revision number. Same goes for
    properties (title). Each change generates a new revision.
  """

  meta_type = 'ERP5 Document'
  portal_type = 'Document'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isDocument = 1
  __dav_collection__=0

  # Regular expressions
  href_parser = re.compile('<a[^>]*href=[\'"](.*?)[\'"]',re.IGNORECASE)
  body_parser = re.compile('<body[^>]*>(.*?)</body>', re.IGNORECASE + re.DOTALL)
  title_parser = re.compile('<title[^>]*>(.*?)</title>', re.IGNORECASE + re.DOTALL)
  base_parser = re.compile('<base[^>]*href=[\'"](.*?)[\'"][^>]*>', re.IGNORECASE + re.DOTALL)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Document
                    , PropertySheet.ExternalDocument
                    , PropertySheet.Url
                    , PropertySheet.Periodicity
                    , PropertySheet.Snapshot
                    )

  # Declarative interfaces
  __implements__ = ()

  searchable_property_list = ('asText', 'title', 'description', 'id', 'reference',
                              'version', 'short_title',
                              'subject', 'source_reference', 'source_project_title',)

  data = '' # some day this will be in property sheets
  base_format = 'base storage format'

  ### Content processing methods
  security.declareProtected(Permissions.View, 'index_html')
  def index_html(self, REQUEST, RESPONSE, format=None, **kw):
    """
      We follow here the standard Zope API for files and images
      and extend it to support format conversion. The idea
      is that an image which ID is "something.jpg" should
      ne directly accessible through the URL
      /a/b/something.jpg. The same is true for a file and
      for any document type which primary purpose is to
      be used by a helper application rather than displayed
      as HTML in a web browser. Exceptions to this approach
      include Web Pages which are intended to be primarily rendered
      withing the layout of a Web Site or withing a standard ERP5 page.
      Please refer to the index_html of TextDocument.

      Should return appropriate format (calling convert
      if necessary) and set headers.

      format -- the format specied in the form of an extension
      string (ex. jpeg, html, text, txt, etc.)

      **kw -- can be various things - e.g. resolution

      TODO:
      - implement guards API so that conversion to certain
        formats require certain permission
    """
    pass

  security.declareProtected(Permissions.View, 'getSearchableText')
  def getSearchableText(self, md=None):
    """
      Used by the catalog for basic full text indexing.
      Uses searchable_property_list attribute to put together various properties
      of the document into one searchable text string.

      XXX-JPS - This method is nice. It should probably be moved to Base class
      searchable_property_list could become a standard class attribute.

      TODO (future): Make this property a per portal type property.
    """
    def getPropertyListOrValue(property):
      """
        we try to get a list, else we get value and convert to list
      """
      method = getattr(self, property, None)
      if method is not None:
        if callable(method):
          val = method()
          if isinstance(val, list) or isinstance(val, tuple):
            return list(val)
          return [str(val)]
      val = self.getPropertyList(property)
      if val is None:
        val = self.getProperty(property)
        if val is not None and val != '':
          val = [val]
        else:
          val = []
      else:
        val = list(val)
      return val

    searchable_text = reduce(add, map(lambda x: getPropertyListOrValue(x),
                                                self.searchable_property_list))
    searchable_text = ' '.join(searchable_text)
    return searchable_text

  # Compatibility with CMF Catalog
  SearchableText = getSearchableText

  security.declareProtected(Permissions.AccessContentsInformation, 'isExternalDocument')
  def isExternalDocument(self):
    """
    Return true if this document was obtained from an external source
    """
    return bool(self.getUrlString())

  ### Relation getters
  security.declareProtected(Permissions.AccessContentsInformation, 'getSearchableReferenceList')
  def getSearchableReferenceList(self):
    """
      This method returns a list of dictionaries which can
      be used to find objects by reference. It uses for
      that a regular expression defined at system level
      preferences.
    """
    text = self.getSearchableText() # XXX getSearchableText or asText ?
    regexp = self.portal_preferences.getPreferredDocumentReferenceRegularExpression()
    try:
      rx_search = re.compile(regexp)
    except TypeError: # no regexp in preference
      LOG('ERP5/Document/Document.getSearchableReferenceList', 0,
          'Document regular expression must be set in portal preferences')
      return ()
    res = rx_search.finditer(text)
    res = [(r.group(), r.groupdict()) for r in res]
    return res
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getImplicitSuccessorValueList')
  def getImplicitSuccessorValueList(self):
    """
      Find objects which we are referencing (if our text_content contains
      references of other documents). The whole implementation is delegated to
      Base_getImplicitSuccessorValueList script.

      The implementation goes in 2 steps:

    - Step 1: extract with a regular expression
      a list of distionaries with various parameters such as 
      reference, portal_type, language, version, user, etc. This
      part is configured through a portal preference.

    - Step 2: read the list of dictionaries
      and build a list of values by calling portal_catalog
      with appropriate parameters (and if possible build 
      a complex query whenever this becomes available in
      portal catalog)
      
      The script is reponsible for calling getSearchableReferenceList
      so that it can use another approach if needed.
      
      NOTE: passing a group_by parameter may be useful at a
      later stage of the implementation.
    """
    # XXX results should be cached as volatile attributes
    refs = [r[1] for r in self.getSearchableReferenceList()]
    res = self.Base_getImplicitSuccessorValueList(refs)
    # get unique latest (most relevant) versions
    res = [r.getObject().getLatestVersionValue() for r in res]
    res_dict = dict.fromkeys(res)
    return res_dict.keys()

  security.declareProtected(Permissions.AccessContentsInformation, 'getImplicitPredecessorValueList')
  def getImplicitPredecessorValueList(self):
    """
      This function tries to find document which are referencing us - by reference only, or
      by reference/language etc. Implementation is passed to 
        Base_getImplicitPredecessorValueList

      The script should proceed in two steps:

      Step 1: build a list of references out of the context
      (ex. INV-123456, 123456, etc.)

      Step 2: search using the portal_catalog and use
      priorities (ex. INV-123456 before 123456)
      ( if possible build  a complex query whenever 
      this becomes available in portal catalog )

      NOTE: passing a group_by parameter may be useful at a
      later stage of the implementation.
    """
    # XXX results should be cached as volatile attributes
    method = self._getTypeBasedMethod('getImplicitPredecessorValueList', 
        fallback_script_id = 'Base_getImplicitPredecessorValueList')
    lst = method()
    # make it unique first time (before getting lastversionvalue)
    di = dict.fromkeys([r.getObject() for r in lst])
    # then get latest version and make unique again
    di = dict.fromkeys([o.getLatestVersionValue() for o in di.keys()])
    ref = self.getReference()
    return [o for o in di.keys() if o.getReference() != ref] # every object has its own reference in SearchableText

  security.declareProtected(Permissions.AccessContentsInformation, 'getImplicitSimilarValueList')
  def getImplicitSimilarValueList(self):
    """
      Analyses content of documents to find out by the content which documents
      are similar. Not implemented yet. 

      No cloud needed because transitive process
    """
    return []

  security.declareProtected(Permissions.AccessContentsInformation, 'getSimilarCloudValueList')
  def getSimilarCloudValueList(self, depth=0):
    """
      Returns all documents which are similar to us, directly or indirectly, and
      in both directions. In other words, it is a transitive closure of similar 
      relation. Every document is returned in the latest version available.
    """
    lista = {}
    depth = int(depth)

    #gettername = 'get%sValueList' % convertToUpperCase(category)
    #relatedgettername = 'get%sRelatedValueList' % convertToUpperCase(category)

    def getRelatedList(ob, level=0):
      level += 1
      #getter = getattr(self, gettername)
      #relatedgetter = getattr(self, relatedgettername)
      #res = getter() + relatedgetter()
      res = ob.getSimilarValueList() + ob.getSimilarRelatedValueList()
      for r in res:
        if lista.get(r) is None:
          lista[r] = True # we use dict keys to ensure uniqueness
          if level != depth:
            getRelatedList(r, level)

    getRelatedList(self)
    lista_latest = {}
    for o in lista.keys():
      lista_latest[o.getLatestVersionValue()] = True # get latest versions avoiding duplicates again
    if lista_latest.has_key(self): 
      lista_latest.pop(self) # remove this document
    if lista_latest.has_key(self.getLatestVersionValue()): 
      lista_latest.pop(self()) # remove this document

    return lista_latest.keys()

  ### Version and language getters - might be moved one day to a mixin class in base
  security.declareProtected(Permissions.View, 'getLatestVersionValue')
  def getLatestVersionValue(self, language=None):
    """
      Tries to find the latest version with the latest revision
      of self which the current user is allowed to access.

      If language is provided, return the latest document
      in the language.

      If language is not provided, return the latest version
      in original language or in the user language if the version is
      the same.
    """
    if not self.getReference():
      return self
    catalog = getToolByName(self, 'portal_catalog', None)
    kw = dict(reference=self.getReference(), sort_on=(('version','descending'),))
    if language is not None: kw['language'] = language
    res = catalog(**kw)

    original_language = self.getOriginalLanguage()
    user_language = self.Localizer.get_selected_language()

    # if language was given return it
    if language is not None:
      return res[0].getObject()
    else:
      first = res[0]
      in_original = None
      for ob in res:
        if ob.getLanguage() == original_language:
          # this is in original language
          in_original = ob
        if ob.getVersion() != first.getVersion():
          # we are out of the latest version - return in_original or first
          if in_original is not None:
            return in_original.getObject()
          else:
            return first.getObject() # this shouldn't happen in real life
        if ob.getLanguage() == user_language:
          # we found it in the user language
          return ob.getObject()
    # this is the only doc in this version
    return self

  security.declareProtected(Permissions.View, 'getVersionValueList')
  def getVersionValueList(self, version=None, language=None):
    """
      Returns a list of documents with same reference, same portal_type
      but different version and given language or any language if not given.
    """
    catalog = getToolByName(self, 'portal_catalog', None)
    kw = dict(portal_type=self.getPortalType(),
                   reference=self.getReference(),
                   order_by=(('version', 'descending', 'SIGNED'),)
                  )
    if version: kw['version'] = version
    if language: kw['language'] = language
    return catalog(**kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'isVersionUnique')
  def isVersionUnique(self):
    """
      Returns true if no other document exists with the same
      reference, version and language, or if the current
      document has no reference.
    """
    if not self.getReference():
      return 1
    catalog = getToolByName(self, 'portal_catalog', None)
    self_count = catalog.unrestrictedCountResults(portal_type=self.getPortalDocumentTypeList(),
                                            reference=self.getReference(),
                                            version=self.getVersion(),
                                            language=self.getLanguage(),
                                            uid=self.getUid(),
                                            validation_state="!=cancelled"
                                            )[0][0]
    count = catalog.unrestrictedCountResults(portal_type=self.getPortalDocumentTypeList(),
                                            reference=self.getReference(),
                                            version=self.getVersion(),
                                            language=self.getLanguage(),
                                            validation_state="!=cancelled"
                                            )[0][0]
    # If self is not indexed yet, then if count == 1, version is not unique
    return count <= self_count

  security.declareProtected(Permissions.ModifyPortalContent, 'setUniqueReference')
  def setUniqueReference(self, suffix='auto'):
    """
      Create a unique reference for the current document
      based on a suffix
    """
    # Change the document reference
    reference = self.getReference() + '-%s-' % suffix + '%s'
    ref_count = 0
    kw = dict(portal_type=self.getPortalDocumentTypeList())
    if self.getVersion(): kw['version'] = self.getVersion()
    if self.getLanguage(): kw['language'] = self.getLanguage()
    while catalog.unrestrictedCountResults(reference=reference % ref_count, **kw)[0][0]:
      ref_count += 1
    self._setReference(reference % ref_count)
  
  security.declareProtected(Permissions.AccessContentsInformation, 'getRevision')
  def getRevision(self):
    """
      Returns the current revision by analysing the change log
      of the current object. The return value is a string
      in order to be consistent with the property sheet
      definition.
      
      NOTE: for now, workflow choice is hardcoded. This is
      an optimisation hack. If a document does neither use
      edit_workflow or processing_status_workflow, the
      first workflow in the chain has prioriot. Better
      implementation would require to be able to define
      which workflow in a chain is the default one for
      revision tracking (and for modification date).
    """
    portal_workflow = getToolByName(self, 'portal_workflow')
    wf_list = list(portal_workflow.getWorkflowsFor(self))
    wf = portal_workflow.getWorkflowById('edit_workflow')
    if wf is not None: wf_list = [wf] + wf_list
    wf = portal_workflow.getWorkflowById('processing_status_workflow')
    if wf is not None: wf_list = [wf] + wf_list
    for wf in wf_list:
      history = wf.getInfoFor(self, 'history', None)
      if history:
        return str(len(filter(lambda x:x.get('action', None) in ('edit', 'upload'), history)))
    return ''

  security.declareProtected(Permissions.AccessContentsInformation, 'getRevisionList')
  def getRevisionList(self):
    """
      Returns the list of revision numbers of the current document
      by by analysing the change log of the current object.
    """
    return range(0, self.getRevision())

  security.declareProtected(Permissions.ModifyPortalContent, 'mergeRevision')
  def mergeRevision(self):
    """
      Merge the current document with any previous revision
      or change its version to make sure it is still unique.

      NOTE: revision support is implemented in the Document
      class rather than within the ContributionTool
      because the ingestion process requires to analyse the content
      of the document first. Hence, it is not possible to
      do any kind of update operation until the whole ingestion
      process is completed, since update requires to know
      reference, version, language, etc. In addition,
      we have chosen to try to merge revisions after each
      metadata discovery as a way to make sure that any
      content added in the system through the ContributionTool
      (ex. through webdav) will be merged if necessary.
      It may be posssible though to split disoverMetadata and
      finishIngestion.
    """
    document = self
    catalog = getToolByName(self, 'portal_catalog', None)
    if self.getReference():
      # Find all document with same (reference, version, language)
      kw = dict(portal_type=self.getPortalDocumentTypeList(),
                reference=self.getReference(),
                validation_state="!=cancelled")
      if self.getVersion(): kw['version'] = self.getVersion()
      if self.getLanguage(): kw['language'] = self.getLanguage()
      document_list = catalog.unrestrictedSearchResults(**kw)
      existing_document = None
      # Select the first one which is not self and which
      # shares the same coordinates
      document_list = list(document_list)
      document_list.sort(lambda x,y: cmp(x.getId(), y.getId() ))
      LOG('[DMS] Existing documents for %s' %self.getSourceReference(), INFO, len(document_list))
      for o in document_list:
        if o.getRelativeUrl() != self.getRelativeUrl() and\
           o.getVersion() == self.getVersion() and\
           o.getLanguage() == self.getLanguage():
          existing_document = o.getObject()
          break
      # We found an existing document to update
      if existing_document is not None:
        document = existing_document
        if existing_document.getPortalType() != self.getPortalType():
          raise ValueError, "[DMS] Ingestion may not change the type of an existing document"
        elif not _checkPermission(Permissions.ModifyPortalContent, existing_document):
          self.setUniqueReference(suffix='unauthorized')
          raise Unauthorized, "[DMS] You are not allowed to update this document"
        else:
          update_kw = {}
          for k in self.propertyIds():
            if k not in FIXED_PROPERTY_IDS and self.hasProperty(k):
              update_kw[k] = self.getProperty(k)
          existing_document.edit(**update_kw)
          # Erase self
          self.delete() # XXX Do we want to delete by workflow or for real ?
    return document

  security.declareProtected(Permissions.AccessContentsInformation, 'getLanguageList')
  def getLanguageList(self, version=None):
    """
      Returns a list of languages which this document is available in
      for the current user.
    """
    if not self.getReference(): return []
    catalog = getToolByName(self, 'portal_catalog', None)
    kw = dict(portal_type=self.getPortalType(),
                           reference=self.getReference(),
                           group_by=('language',))
    if version is not None:
      kw['version'] = version
    return map(lambda o:o.getLanguage(), catalog(**kw))

  security.declareProtected(Permissions.AccessContentsInformation, 'getOriginalLanguage')
  def getOriginalLanguage(self):
    """
      Returns the original language of this document.

      XXX-JPS not implemented yet ?
    """
    # Approach 1: use portal_catalog and creation dates
    # Approach 2: use workflow analysis (delegate to script if necessary)
    #             workflow analysis is the only way for multiple orginals
    # XXX - cache or set?
    reference = self.getReference()
    if not reference:
      return 
    catalog = getToolByName(self, 'portal_catalog', None)
    res = catalog(reference=self.getReference(), sort_on=(('creation_date','ascending'),))
    # XXX this should be security-unaware - delegate to script with proxy roles
    return res[0].getLanguage() # XXX what happens if it is empty?
    

  ### Property getters
  # Property Getters are document dependent so that we can
  # handle the weird cases in which needed properties change with the type of document
  # and the usual cases in which accessing content changes with the meta type
  security.declareProtected(Permissions.ModifyPortalContent,'getPropertyDictFromUserLogin')
  def getPropertyDictFromUserLogin(self, user_login=None):
    """
      Based on the user_login, find out as many properties as needed.
      returns properties which should be set on the document
    """
    if user_login is None:
      user_login = str(getSecurityManager().getUser())
    method = self._getTypeBasedMethod('getPropertyDictFromUserLogin',
        fallback_script_id='Document_getPropertyDictFromUserLogin')
    return method(user_login)

  security.declareProtected(Permissions.ModifyPortalContent,'getPropertyDictFromContent')
  def getPropertyDictFromContent(self):
    """
      Based on the document content, find out as many properties as needed.
      returns properties which should be set on the document
    """
    if not self.hasBaseData():
      self.convertToBaseFormat()
    method = self._getTypeBasedMethod('getPropertyDictFromContent',
        fallback_script_id='Document_getPropertyDictFromContent')
    return method()

  security.declareProtected(Permissions.ModifyPortalContent,'getPropertyDictFromFileName')
  def getPropertyDictFromFileName(self, file_name):
    """
      Based on the file name, find out as many properties as needed.
      returns properties which should be set on the document
    """
    return self.portal_contributions.getPropertyDictFromFileName(file_name)

  security.declareProtected(Permissions.ModifyPortalContent,'getPropertyDictFromInput')
  def getPropertyDictFromInput(self):
    """
      Get properties which were supplied explicitly to the ingestion method
      (discovered or supplied before the document was created).

      The implementation consists in saving document properties
      into _backup_input by supposing that original input parameters were
      set on the document by ContributionTool.newContent as soon
      as the document was created.
    """
    if hasattr(self, '_backup_input'):
      return getattr(self, '_backup_input')
    kw = {}
    for id in self.propertyIds():
      # We should not consider file data
      if id not in ('data', 'categories_list', 'uid', 'id',
                    'text_content', 'base_data',) \
            and self.hasProperty(id):
        kw[id] = self.getProperty(id)
    self._backup_input = kw # We could use volatile and pass kw in activate
                            # if we are garanteed that _backup_input does not
                            # disappear within a given transaction
    return kw

  security.declareProtected(Permissions.AccessContentsInformation, 'getStandardFileName')
  def getStandardFileName(self):
    """
    Returns the document coordinates as a standard file name. This
    method is the reverse of getPropertyDictFromFileName.

    NOTE: this method must be overloadable by types base method with fallback
    """
    if self.getReference():
      file_name = self.getReference()
    else:
      file_name = self.getTitleOrId()
    if self.getVersion():
      file_name = file_name + '-%s' % self.getVersion()
    if self.getLanguage():
      file_name = file_name + '-%s' % self.getLanguage()
    return file_name

  ### Metadata disovery and ingestion methods
  security.declareProtected(Permissions.ModifyPortalContent, 'discoverMetadata')
  def discoverMetadata(self, file_name=None, user_login=None):
    """
      This is the main metadata discovery function - controls the process
      of discovering data from various sources. The discovery itself is
      delegated to scripts or uses preference-configurable regexps. The
      method returns either self or the document which has been
      merged in the discovery process.

      file_name - this parameter is a file name of the form "AA-BBB-CCC-223-en"

      user_login - this is a login string of a person; can be None if the user is
                   currently logged in, then we'll get him from session
    """   
    if file_name is not None:
      # filename is often undefined....
      self._setSourceReference(file_name)
    # Preference is made of a sequence of 'user_login', 'content', 'file_name', 'input'
    method = self._getTypeBasedMethod('getPreferredDocumentMetadataDiscoveryOrderList', 
        fallback_script_id = 'Document_getPreferredDocumentMetadataDiscoveryOrderList')
    order_list = list(method())
    order_list.reverse()
    # Start with everything until content - build a dictionary according to the order
    kw = {}
    for order_id in order_list:
      result = None
      if order_id not in VALID_ORDER_KEY_LIST:
        # Prevent security attack or bad preferences
        raise AttributeError, "%s is not in valid order key list" % order_id
      method_id = 'getPropertyDictFrom%s' % convertToUpperCase(order_id)
      method = getattr(self, method_id)
      if order_id == 'file_name':
        if file_name is not None:
          result = method(file_name)
      elif order_id == 'user_login':
        if user_login is not None:
          result = method(user_login)
      else:
        result = method()
      if result is not None:
        kw.update(result)

    # Prepare the content edit parameters - portal_type should not be changed
    kw.pop('portal_type', None)
    # Try not to invoke an automatic transition here
    self._edit(**kw)
    # Finish ingestion by calling method
    self.finishIngestion() 
    self.reindexObject()
    # Revision merge is tightly coupled
    # to metadata discovery - refer to the documentation of mergeRevision method
    return self.mergeRevision() 

  security.declareProtected(Permissions.ModifyPortalContent, 'finishIngestion')
  def finishIngestion(self):
    """
      Finish the ingestion process by calling the appropriate script. This
      script can for example allocate a reference number automatically if
      no reference was defined.
    """
    method = self._getTypeBasedMethod('finishIngestion', fallback_script_id='Document_finishIngestion')
    return method()

  # Conversion methods
  security.declareProtected(Permissions.ModifyPortalContent, 'convert')
  def convert(self, format, **kw):
    """
      Main content conversion function, returns result which should
      be returned and stored in cache.
      format - the format specied in the form of an extension
      string (ex. jpeg, html, text, txt, etc.)
      **kw can be various things - e.g. resolution

      Default implementation returns an empty string (html, text)
      or raises an error.

      TODO:
      - implement guards API so that conversion to certain
        formats require certain permission
    """
    if format == 'html':
      return 'text/html', ''
    if format in ('text', 'txt'):
      return 'text/plain', ''
    raise NotImplementedError

  security.declareProtected(Permissions.View, 'asText')
  def asText(self):
    """
      Converts the content of the document to a textual representation.
    """
    mime, data = self.convert(format='txt')
    return data

  security.declareProtected(Permissions.View, 'asHTML')
  def asHTML(self):
    """
      Returns a complete HTML representation of the document
      (with body tags, etc.). Adds if necessary a base
      tag so that the document can be displayed in an iframe
      or standalone.

      Actual conversion is delegated to _asHTML
    """
    html = self._asHTML()
    if self.getUrlString():
      # If a URL is defined, add the base tag
      # if base is defined yet.
      html = str(html)
      if not html.find('<base') >= 0:
        base = '<base href="%s">' % self.getContentBaseURL()
        html = html.replace('<head>', '<head>%s' % base)
      # We do not implement cache yet since it increases ZODB
      # for probably no reason. More research needed
      # self.setConversion(html, mime='text/html', format='base-html')
    return html

  security.declarePrivate('_asHTML')
  def _asHTML(self):
    """
      A private method which converts to HTML. This method
      is the one to override in subclasses.
    """
    if self.hasConversion(format='base-html'):
      mime, data = self.getConversion(format='base-html')
      return data
    mime, html = self.convert(format='html')
    return html

  security.declareProtected(Permissions.View, 'asStrippedHTML')
  def asStrippedHTML(self):
    """
      Returns a stripped HTML representation of the document
      (without html and body tags, etc.) which can be used to inline
      a preview of the document.
    """
    if self.hasConversion(format='stripped-html'):
      mime, data = self.getConversion(format='stripped-html')
      return data
    mime, html = self.convert(format='html')
    body_list = re.findall(self.body_parser, str(html))
    if len(body_list):
      return body_list[0]
    return html

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentInformation')
  def getContentInformation(self):
    """
    Returns the content information from the HTML conversion.
    The default implementation tries to build a dictionnary
    from the HTML conversion of the document and extract
    the document title.
    """
    result = {}
    html = self.asHTML()
    if not html: return result
    title_list = re.findall(self.title_parser, str(html))
    if title_list:
      result['title'] = title_list[0]
    return result

  # Base format support
  security.declareProtected(Permissions.ModifyPortalContent, 'convertToBaseFormat')
  def convertToBaseFormat(self):
    """
      Converts the content of the document to a base format
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
    try:
      msg = self._convertToBaseFormat() # Call implemetation method
      self.clearConversionCache() # Conversion cache is now invalid
      if msg is None:
        msg = 'Converted to %s.' % self.base_format
      self.convertFile(comment=msg) # Invoke workflow method
    except NotImplementedError:# we don't do any workflow action if nothing has been done
      msg = '' 
    except ConversionError, e:
      msg = 'Problem: %s' % (str(e) or 'undefined.')
      self.processFile(comment=msg)
    except Fault, e:
      msg = 'Problem: %s' % (repr(e) or 'undefined.')
      self.processFile(comment=msg)
    except socket.error, e:
      msg = 'Problem: %s' % (repr(e) or 'undefined.')
      self.processFile(comment=msg)
    return msg

  def _convertToBaseFormat(self):
    """
      Placeholder method. Must be subclassed by classes
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
    raise NotImplementedError

  security.declareProtected(Permissions.ModifyPortalContent, 'updateBaseMetadata')
  def updateBaseMetadata(self, **kw):
    """
    Update the base format data with the latest properties entered
    by the user. For example, if title is changed in ERP5 interface,
    the base format file should be updated accordingly.

    Default implementation does nothing. Refer to OOoDocument class
    for an example of implementation.
    """
    pass

  # Transformation API
  security.declareProtected(Permissions.ModifyPortalContent, 'populateContent')
  def populateContent(self):
    """
      Populates the Document with subcontent based on the
      document base data.

      This can be used for example to transform the XML
      of an RSS feed into a single piece per news or
      to transform an XML export from a database into
      individual records. Other application: populate
      an HTML text document with its images, used in
      conversion with convertToBaseFormat.
    """
    try:
      method = self._getTypeBasedMethod('populateContent')
    except KeyError, AttributeError:
      method = None
    if method is not None: method()

  # Crawling API
  security.declareProtected(Permissions.AccessContentsInformation, 'getContentURLList')
  def getContentURLList(self):
    """
      Returns a list of URLs referenced by the content of this document.
      Default implementation consists in analysing the document
      converted to HTML. Subclasses may overload this method
      if necessary. However, it is better to extend the conversion
      methods in order to produce valid HTML, which is useful to
      many people, rather than overload this method which is only
      useful for crawling.
    """
    html_content = self.asStrippedHTML()
    return re.findall(self.href_parser, str(html_content))

  security.declareProtected(Permissions.ModifyPortalContent, 'updateContentFromURL')
  def updateContentFromURL(self, repeat=MAX_REPEAT, crawling_depth=0):
    """
      Download and update content of this document from its source URL.
      Implementation is handled by ContributionTool.
    """
    self.portal_contributions.updateContentFromURL(self, repeat=repeat, crawling_depth=crawling_depth)

  security.declareProtected(Permissions.ModifyPortalContent, 'crawlContent')
  def crawlContent(self):
    """
      Initialises the crawling process on the current document.
    """
    self.portal_contributions.crawlContent(self)

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentBaseURL')
  def getContentBaseURL(self):
    """
      Returns the content base URL based on the actual content or
      on its URL.
    """
    base_url = self.asURL()
    base_url_list = base_url.split('/')
    if len(base_url_list):
      if base_url_list[-1] and base_url_list[-1].find('.') > 0:
        # Cut the trailing part in http://www.some.site/at/trailing.html
        # but not in http://www.some.site/at
        base_url = '/'.join(base_url_list[:-1])
    return base_url

  # Alarm date calculation - this method should be moved out ASAP
  security.declareProtected(Permissions.AccessContentsInformation, 'getNextAlarmDate')
  def getNextAlarmDate(self):
    """
    This method is only there to have something to test.
    Serious refactoring of Alarm, Periodicity and CalendarPeriod
    classes is needed.
    """
    return DateTime() + 10
