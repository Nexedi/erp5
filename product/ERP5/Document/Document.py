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

from DateTime import DateTime
from operator import add
from xmlrpclib import Fault
import re
import socket

from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base
from Globals import PersistentMapping
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.WebDAVSupport import TextContent
from Products.ERP5Type.Message import Message
from Products.ERP5Type.Utils import convertToUpperCase, convertToMixedCase
from Products.ERP5.Document.Url import UrlMixIn
from Products.ERP5.Tool.ContributionTool import MAX_REPEAT

from zLOG import LOG

_MARKER = []
VALID_ORDER_KEY_LIST = ('user_login', 'content', 'file_name', 'input')

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
  security.declareProtected(Permissions.View, 'getSearchableReferenceList')
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
    
  security.declareProtected(Permissions.View, 'getImplicitSuccessorValueList')
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

  security.declareProtected(Permissions.View, 'getImplicitPredecessorValueList')
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

  security.declareProtected(Permissions.View, 'getImplicitSimilarValueList')
  def getImplicitSimilarValueList(self):
    """
      Analyses content of documents to find out by the content which documents
      are similar. Not implemented yet. 

      No cloud needed because transitive process
    """
    return []

  security.declareProtected(Permissions.View, 'getSimilarCloudValueList')
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

  security.declareProtected(Permissions.View, 'hasFile')
  def hasFile(self):
    """
    Checks whether we have an initial file
    """
    _marker = []
    if getattr(self,'data', _marker) is not _marker: # XXX-JPS - use propertysheet accessors
      d = getattr(self, 'data')
      return d is not None and d != ''
    return False

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
    kw = dict(reference=self.getReference(), sort_on=(('version','descending'),('revision','descending'),))
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
                   group_by=('revision',),
                   order_by=(('revision', 'descending', 'SIGNED'),)
                  )
    if version: kw['version'] = version
    if language: kw['language'] = language
    return catalog(**kw)

  security.declareProtected(Permissions.View, 'isVersionUnique')
  def isVersionUnique(self):
    """
      Returns true if no other document of the same
      portal_type and reference has the same version and language

      XXX should delegate to script with proxy roles
      XXX-JPS revision ?
    """
    catalog = getToolByName(self, 'portal_catalog', None)
    # XXX why this does not work???
    #return catalog.countResults(portal_type=self.getPortalType(),
                                #reference=self.getReference(),
                                #version=self.getVersion(),
                                #language=self.getLanguage(),
                                #) <= 1
    return len(catalog(portal_type=self.getPortalType(),
                                reference=self.getReference(),
                                version=self.getVersion(),
                                language=self.getLanguage(),
                                )) <= 1

  security.declareProtected(Permissions.View, 'getLatestRevisionValue')
  def getLatestRevisionValue(self):
    """
      Returns the latest revision of ourselves
    """
    if not self._checkCompleteCoordinates():
      return None
    catalog = getToolByName(self, 'portal_catalog', None)
    res = catalog(
        reference=self.getReference(),
        language=self.getLanguage(),
        version=self.getVersion(),
        sort_on=(('revision','descending'),)
        )
    if len(res) == 0:
      return None
    return res[0].getObject()

  security.declareProtected(Permissions.View, 'getRevisionValueList')
  def getRevisionValueList(self):
    """
      Returns a list revision strings for a given reference, version, language
      XXX should it return revision strings, or docs (as the func name would suggest)?

      XXX-JPS return values - getRevisionList returns revisions 
    """
    # Use portal_catalog
    if not self._checkCompleteCoordinates():
      return []
    res = self.portal_catalog(reference=self.getReference(),
                  language=self.getLanguage(),
                  version=self.getVersion()
                  )
    d = {}
    for r in res:
      d[r.getRevision()] = True
      revs = d.keys()
      revs.sort(reverse=True)
    return revs

  security.declarePrivate('_checkCompleteCoordinates')
  def _checkCompleteCoordinates(self):
    """
      test if the doc has all coordinates

      XXX-JPS - revision ?
    """
    reference = self.getReference()
    version = self.getVersion()
    language = self.getLanguage()
    return (reference and version and language)
  
  security.declareProtected(Permissions.ModifyPortalContent, 'setNewRevision')
  def setNewRevision(self, immediate_reindex=False):
    """
      Set a new revision number automatically
      Delegates to ZMI script because revision numbering policies can be different.
      Should be called by interaction workflow upon appropriate action.

      Sometimes we should reindex immediately, to avoid other doc setting
      the same revision (if revisions are global and there is heavy traffic)
    """
    # Use portal_catalog without security (proxy roles on scripts)
    method = self._getTypeBasedMethod('getNewRevision', 
        fallback_script_id = 'Document_getNewRevision')
    new_rev = method()
    self.setRevision(new_rev)
    if immediate_reindex:
      self.immediateReindexObject()
    else:
      self.reindexObject()
  
  security.declareProtected(Permissions.View, 'getLanguageList')
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

  security.declareProtected(Permissions.View, 'getOriginalLanguage')
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
    """
    if hasattr(self, '_backup_input'):
      return getattr(self, '_backup_input')
    kw = {}
    for id in self.propertyIds():
      # We should not consider file data
      if id not in ('data', 'categories_list', 'uid', 'id', 'text_content', ) \
            and self.hasProperty(id):
        kw[id] = self.getProperty(id)
    self._backup_input = kw # We could use volatile and pass kw in activate
                            # if we are garanteed that _backup_input does not
                            # disappear within a given transaction
    return kw


  ### Metadata disovery and ingestion methods
  security.declareProtected(Permissions.ModifyPortalContent, 'discoverMetadata')
  def discoverMetadata(self, file_name=None, user_login=None):
    """
      This is the main metadata discovery function - controls the process
      of discovering data from various sources. The discovery itself is
      delegated to scripts or uses preference-configurable regexps.

      file_name - this parameter is a file name of the form "AA-BBB-CCC-223-en"

      user_login - this is a login string of a person; can be None if the user is
                   currently logged in, then we'll get him from session
    """

    # Get the order
    # Preference is made of a sequence of 'user_login', 'content', 'file_name', 'input'
    self._setSourceReference(file_name) # XXX Who added this ???
                                       # filename is often undefined....
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
        # LOG('discoverMetadata %s' % order_id, 0, repr(result))
        kw.update(result)

    # Prepare the content edit parameters - portal_type should not be changed
    try:
      del(kw['portal_type'])
    except KeyError:
      pass

    self._edit(**kw) # Try not to invoke an automatic transition here
    self.finishIngestion() # Finish ingestion by calling method
    self.reindexObject()

  security.declareProtected(Permissions.ModifyPortalContent, 'finishIngestion')
  def finishIngestion(self):
    """
      Finish the ingestion process by calling the appropriate script. This
      script can for example allocate a reference number automatically if
      no reference was defined.
    """
    return self._getTypeBasedMethod('finishIngestion',
        fallback_script_id='Document_finishIngestion')

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
    """
    if self.hasConversion(format='base-html'):
      mime, data = self.getConversion(format='base-html')
      return data
    mime, html = self.convert(format='html')
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

  # Alarm date calculation
  security.declareProtected(Permissions.AccessContentsInformation, 'getNextAlarmDate')
  def getNextAlarmDate(self):
    """
    This method is only there to have something to test.
    Serious refactoring of Alarm, Periodicity and CalendarPeriod
    classes is needed.
    """
    return DateTime() + 10

  # Standard File Naming
  security.declareProtected(Permissions.AccessContentsInformation, 'getStandardFileName')
  def getStandardFileName(self):
    """
    Returns the document coordinates as a standard file name.

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
  