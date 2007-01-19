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

from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base
from Globals import PersistentMapping
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.WebDAVSupport import TextContent
from Products.ERP5Type.Message import Message

_MARKER = []
VALID_ORDER_KEY_LIST = ('user', 'content', 'file_name', 'input')

def makeSortedTuple(kw):
  items = kw.items()
  items.sort()
  return tuple(items)


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
    if not hasattr(aself, '_cached_time'):
      self._cached_time = PersistentMapping()
    if not hasattr(aself, '_cached_data'):
      self._cached_data = PersistentMapping()
    if not hasattr(aself, '_cached_mime'):
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

  security.declareProtected(Permissions.View, 'getConversionCacheInfo')
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


class Document(XMLObject):
  """
      Document is an abstract class with all methods
      related to document management in ERP5. This includes
      searchable text, explicit relations, implicit relations,
      metadata, versions, languages, etc.

      There are currently two types of Document subclasses:

      * File for binary file based documents. File
        has subclasses such as Image, OOoDocument,
        PDFDocument, etc. to implement specific conversion
        methods.

      * TextDocument for text based documents. TextDocument
        has subclasses such as Wiki to implement specific
        methods.

      Document classes which implement conversion should use
      the ConversionCacheMixin class so that converted values are
      stored inside ZODB and do not need to be recalculated.

      XXX IDEA - ISSUE: generic API for conversion.
        converted_document = document.convert(...)

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
      file_name  -    data which might be encoded in file name
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
        index_html (Document)

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

      * Base_getImplicitSuccesorValueList - finds appropriate all documents
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

      Subcontent: documents may include subcontent (files, images, etc.)
      so that publication of rich content can be path independent.

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
                    )

  # Declarative interfaces
  __implements__ = ()

  searchable_property_list = ('title', 'description', 'id', 'reference',
                              'version', 'short_title', 'keyword',
                              'subject', 'source_reference', 'source_project_title')


  ### Content processing methods
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

      format - the format specified in the form of an extension
      string (ex. jpeg, html, text, txt, etc.)
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
      val = self.getPropertyList(property)
      if val is None:
        val = self.getProperty(property)
        if val is not None and val != '':
          val=[val]
      return val
        
    searchable_text = reduce(add, map(lambda x: self.getPropertyListOrValue(x) or ' ',
                                                self.searchable_property_list))
    return searchable_text

  # Compatibility with CMF Catalog
  SearchableText = getSearchableText # XXX-JPS - Here wa have a security issue - ask seb what to do

  ### Relation getters
  def getSearchableReferenceList(self):
    """
      Public Method
      
      This method returns a list of dictionaries which can
      be used to find objects by reference. It uses for
      that a regular expression defined at system level
      preferences.
    """
    text = self.getSearchableText()
    regexp = self.getPreferredReferenceLookupRegexp()
    try:
      rx_search = re.compile(regexp)
    except TypeError: # no regexp in preference
      self.log('please set document reference regexp in preferences')
      return []
    res = rx_search.finditer(text)
    res = [(r.group(),r.groupdict()) for r in res]
    return res
    
  security.declareProtected(Permissions.View, 'getImplicitSuccessorValueList')
  def getImplicitSuccessorValueList(self):
    """
    Find objects which we are referencing (if our text_content contains
    references of other documents). The whole implementation is delegated to
    Document_getImplicitSuccessorValueList script.

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
    # XXX-JPS - Please use TransactionCache in ERP5Type for this
    # TransactionCache does all the work for you
    lst = []
    for ref in self.getSearchableReferenceList():
      r = ref[1]
      res = self.Document_findImplicitSuccessor(**r)
      if len(res)>0:
        lst.append(res[0].getObject())
    return lst

  security.declareProtected(Permissions.View, 'getImplicitPredecessorValueList')
  def getImplicitPredecessorValueList(self):
    """
      This function tries to find document which are referencing us - by reference only, or
      by reference/language etc. Implementation is passed to 
        Document_getImplicitPredecessorValueList

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
    method = self._getTypeBasedMethod('findImplicitPredecessorList', 
        fallback_script_id = 'Document_findImplicitPredecessorList')
    lst = method()
    lst = [r.getObject() for r in lst]
    di = dict.fromkeys(lst) # make it unique
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
  def getSimilarCloudValueList(self):
    """
      Returns all documents which are similar to us, directly or indirectly, and
      in both directions. In other words, it is a transitive closure of similar 
      relation. Every document is returned in the latest version available.
    """
    lista = {}
    depth = int(depth)

    gettername = 'get%sValueList' % upperCase(category)
    relatedgettername = 'get%sRelatedValueList' % upperCase(category)

    def getRelatedList(self, level=0):
      level += 1
      getter = getattr(self, gettername)
      relatedgetter = getattr(self, relatedgettername)
      res = getter() + relatedgetter()
      for r in res:
        if lista.get(r) is None:
          lista[r] = True # we use dict keys to ensure uniqueness
        if level != depth:
          getRelatedList(r, level)

    getRelatedList(context)
    lista_latest = {}
    for o in lista.keys():
      lista_latest[o.getLatestVersionValue()] = True # get latest versions avoiding duplicates again
    if lista_latest.has_key(context): lista_latest.pop(context) # remove this document
    if lista_latest.has_key(context.getLatestVersionValue()): lista_latest.pop(contextLatestVersionValue()) # remove this document

    return lista_latest.keys()

  ### Version and language getters - might be moved one day to a mixin class in base
  security.declareProtected(Permissions.View, 'getLatestVersionValue')
  def getLatestVersionValue(self, language=None):
    """
    Tries to find the latest version with the latest revions
    of self which the current user is allowed to access.

    If language is provided, return the latest document
    in the language.

    If language is not provided, return the latest version
    in any language or in the user language if the version is
    the same.
    """
    # Use portal_catalog
    pass

  security.declareProtected(Permissions.View, 'getVersionValueList')
  def getVersionValueList(self, version=None, language=None):
    """
      Returns a list of documents with same reference, same portal_type
      but different version and given language or any language if not given.
    """
    catalog = getToolByName(self, 'portal_catalog', None)
    return catalog(portal_type=self.getPortalType(),
                   reference=self.getReference(),
                   version=version,
                   language=language,
                   group_by=('revision',),
                   order_by=(('revision', 'descending', 'SIGNED'),)
                  )

  security.declareProtected(Permissions.View, 'isVersionUnique')
  def isVersionUnique(self):
    """
      Returns true if no other document of the same
      portal_type and reference has the same version and language
    """
    catalog = getToolByName(self, 'portal_catalog', None)
    return catalog.countResults(portal_type=self.getPortalType(),
                                reference=self.getReference(),
                                version=self.getVersion(),
                                language=self.getLanguage(),
                                ) <= 1

  security.declareProtected(Permissions.View, 'getLatestRevisionValue')
  def getLatestRevisionValue(self):
    """
      Returns the latest revision of ourselves
    """
    # Use portal_catalog
    pass

  security.declareProtected(Permissions.View, 'getRevisionValueList')
  def getRevisionValueList(self):
    """
      Returns a list revision strings for a given reference, version, language
    """
    # Use portal_catalog
    pass
  
  security.declareProtected(Permissions.ModifyPortalContent, 'setNewRevision')
  def setNewRevision(self):
    """
      Set a new revision number automatically
      Delegates to ZMI script because revision numbering policies can be different.
      Should be called by interaction workflow upon appropriate action.
    """
    # Use portal_catalog without security
    method = self._getTypeBasedMethod('getNewRevision', 
        fallback_script_id = 'Document_getNewRevision')
    new_rev = method()
    self.setRevision(new_rev)
  
  security.declareProtected(Permissions.View, 'getLanguageList')
  def getLanguageList(self, version=None):
    """
      Returns a list of languages which this document is available in
      for the current user.
    """
    catalog = getToolByName(self, 'portal_catalog', None)
    return map(lambda o:o.getLanguage(),
                   catalog(portal_type=self.getPortalType(),
                           reference=self.getReference(),
                           version=version,
                           group_by=('language',),
                           ))

  security.declareProtected(Permissions.View, 'getOriginalLanguage')
  def getOriginalLanguage(self):
    """
      Returns the original language of this document.
    """
    # Approach 1: use portal_catalog and creation dates
    # Approach 2: use workflow analysis (delegate to script if necessary)
    #             workflow analysis is the only way for multiple orginals
    # XXX - cache or set?
    pass

  ### Property getters
  # Property Getters are document dependent so that we can
  # handle the weird cases in which needed properties change with the type of document
  # and the usual cases in which accessing content changes with the meta type
  security.declareProtected(Permissions.ModifyPortalContent,'getPropertyDictFromUserLogin')
  def getPropertyDictFromUserLogin(self, user_login):
    """
      Based on the user_login, find out as many properties as needed.
      returns properties which should be set on the document
    """
    if user_login is None:
      user_login = str(getSecurityManager().getUser())
    method = self._getTypeBasedMethod('getPropertyDictFromUserLogin',
        fallback_script_id='Document_getPropertyDictFromUserLogin')
    return method()

  security.declareProtected(Permissions.ModifyPortalContent,'getPropertyDictFromContent')
  def getPropertyDictFromContent(self):
    """
      Based on the document content, find out as many properties as needed.
      returns properties which should be set on the document
    """
    # XXX this method should first make sure we have text content
    # or do a conversion
    return self._getTypeBasedMethod('getPropertyDictFromContent',
        fallback_script_id='Document_getPropertyDictFromContent')

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
      if id is not 'data' and self.hasProperty(id):
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
    delegated to scripts or uses preferences-configurable regexps.

    file_name - this parameter is a file name of the form "AA-BBB-CCC-223-en"

    user_login - this is a login string of a person; can be None if the user is
      currently logged in, then we'll get him from session
    """

    # Get the order
    # Preference is made of a sequence of 'user_login', 'content', 'file_name', 'input'
    method = self._getTypeBasedMethod('getPreferredDocumentMetadataDiscoveryOrderList', 
        fallback_script_id = 'Document_getPreferredDocumentMetadataDiscoveryOrderList')
    order_list = method()

    # Start with everything until content
    content_index = order_list.index('content')

    # XXX should be done in the reverse order
    # Start with everything until content - build a dictionnary according to the order
    kw = {}
    for order_id in order_list[0:content_index-1]:
      if order_id not in VALID_ORDER_KEY_LIST:
        # Prevent security attack or bad preferences
        raise AttributeError, "%s is not in valid order key list" % order_id
      method_id = 'getPropertyDictFrom%s' % convertToUpperCase(order_id)
      method = getattr(self, method_id)
      if order_id == 'file_name':
        result = method(file_name)
      elif order_id == 'user_login':
        result = method(file_name)
      else:
        result = method()
      kw.update(result)
      
    # Edit content
    self.edit(kw)

    # Finish in second stage
    self.activate().finishMetadataDiscovery()
    
  security.declareProtected(Permissions.ModifyPortalContent, 'finishMetadataDiscovery')
  def finishMetadataDiscovery(self):
    """
    This is called by portal_activities, to leave time-consuming procedures
    for later. It converts the OOoDocument (later maybe some other formats) and
    does things that can be done only after it is converted).
    """
    # Get the order from preferences
    # Preference is made of a sequence of 'user_login', 'content', 'file_name', 'input'
    method = self._getTypeBasedMethod('getPreferredDocumentMetadataDiscoveryOrderList', 
        fallback_script_id = 'Document_getPreferredDocumentMetadataDiscoveryOrderList')
    order_list = method()

    # Start with everything until content
    content_index = order_list.index('content')

    # Start with everything until content - build a dictionnary according to the order
    kw = {}
    for order_id in order_list[content_index:]:
      if order_id not in VALID_ORDER_KEY_LIST:
        # Prevent security attack or bad preferences
        raise AttributeError, "%s is not in valid order key list" % order_id
      method_id = 'getPropertyDictFrom%s' % convertToUpperCase(order_id)
      method = getattr(self, method_id)
      if order_id == 'file_name':
        result = method(file_name)
      elif order_id == 'user_login':
        result = method(file_name)
      else:
        result = method()
      kw.update(result)
      
    # Edit content
    self.edit(kw)

    # Erase backup attributes
    delattr(self, '_backup_input')

    # Finish ingestion by calling method
    self.finishIngestion()

  security.declareProtected(Permissions.ModifyPortalContent, 'finishIngestion')
  def finishIngestion(self):
    """
      Finish the ingestion process by calling the appropriate script
    """
    return self._getTypeBasedMethod('finishIngestion',
        fallback_script_id='Document_finishIngestion')

# vim: filetype=python syntax=python shiftwidth=2 
