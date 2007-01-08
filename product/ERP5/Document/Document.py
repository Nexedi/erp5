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

from AccessControl import ClassSecurityInfo
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
  _cached_time = {}
  # generated files (cache)
  _cached_data = {}
  # mime types for cached formats XXX to be refactored
  _cached_mime = {}

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ModifyPortalContent, 'clearConversionCache')
  def clearConversionCache(self):
    """
    Clear cache (invoked by interaction workflow upon file upload
    needed here to overwrite class attribute with instance attrs
    """
    self._cached_time = {}
    self._cached_data = {}
    self._cached_mime = {}

  security.declareProtected(Permissions.View, 'hasConversion')
  def hasConversion(self, **format):
    """
      Checks whether we have a version in this format
    """
    return self._cached_data.has_key(makeSortedTuple(format))

  security.declareProtected(Permissions.View, 'getCacheTime')
  def getCacheTime(self, **format):
    """
      Checks when if ever was the file produced
    """
    return self._cached_time.get(makeSortedTuple(format), 0)

  security.declareProtected(Permissions.ModifyPortalContent, 'updateConversion')
  def updateConversion(self, **format):
      self._cached_time[makeSortedTuple(format)] = DateTime()

  security.declareProtected(Permissions.ModifyPortalContent, 'setConversion')
  def setConversion(self, data, mime=None, **format):
    """
    Saves a version of the document in a given format; records mime type
    and conversion time (which is right now).
    """
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
    tformat = makeSortedTuple(format)
    return self._cached_mime.get(tformat, ''), self._cached_data.get(tformat, '')

  security.declareProtected(Permissions.View, 'getConversionCacheInfo')
  def getConversionCacheInfo(self):
    """
    Get cache details as string (for debugging)
    """
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
      stored.

      XXX IDEA - ISSUE: generic API for conversion.
        converted_document = document.convert(...)

      Instances can be created directly, or via portal_contributions tool
      which manages document ingestion process whereby a file can be uploaded
      by http or sent in by email or dropped in by webdav or in some other
      way as yet unknown. The ingestion process has the following steps:

      (1) portal type detection
      (2) object creation and upload of data
      (3) metadata discovery (optionally with conversion of data to another format)
      (4) other possible actions

      This class handles (3) and calls a ZMI script to do (4).

      Metadata can be drawn from various sources:

      input     -   data supplied with http request or set on the object during (2) (e.g.
                    discovered from email text)
      file_name -   data which might be encoded in file name
      user_login-   information about user who is contributing the file
      content   -   data which might be derived from document content

      If a certain property is defined in more than one source, it is set according to
      preference order returned by a script 
      Document_getPreferredDocumentMetadataDiscoveryOrderList (or type-based version).
      Methods for discovering metadata are:
        getPropertyDictFromInput
        getPropertyDictFromFileName
        getPropertyDictFromUserLogin
        getPropertyDictFromContent

      The Document class behaviour can be extended / customized through scripts
      (which are type-based so can be adjusted per portal type).

      * Document_getFilenameParsingRegexp - returns a regular expression for extracting
        properties encoded in file name

      * Document_getReferenceLookupRegexp - returns a regular expression for finding
        references to documents within document text content

      * Document_getPropertyListFromUser - finds a user (by user_login or from session)
        and returns properties which should be set on the document

      * Document_getPropertyListFromContent - analyzes document content and returns
        properties which should be set on the document

      * Document_findImplicitSuccessor - finds appropriate version of a document
        based on coordinates (which can be incomplete, depending if a document reference
        found in text content contained version and/or language)

      * Document_findImplicitPredecessorList - finds document predecessors based on
        the document coordinates (can use only complete coordinates, or also partial)

      * Document_getPreferredDocumentMetadataDiscoveryOrderList - returns an order
        in which metadata should be set/overwritten

      * Document_finishIngestion - called by portal_activities after all the ingestion
        is completed (and after document has been converted, so text_content
        is available if the document has it)

      * Document_getNewRevisionNumber - calculates revision number which should be set
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


  ### Content indexing methods
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
  def _getImplicitSuccessorReferenceList(self):
    """
      Private Implementation Method
      
      Find references in text_content, return matches
      with this we can then find objects
      The reference regexp defined in Document_getFilenameParsingRegexp should 
      contain named groups (usually reference, version, language)
      which make keys of the dictionary returned by this function
      This function returns a list of dictionaries.
    """
    if getattr(self,'getTextContent',_MARKER) is _MARKER:
      return []
    if self.getTextContent() is None:
      return []
    try:
      method = self._getTypeBasedMethod('getReferenceLookupRegexp', 
          fallback_script_id = 'Document_getReferenceLookupRegexp')
      rx_search = method()
    except TypeError: # no regexp in preference
      self.log('please set document reference regexp in preferences')
      return []
    res = rx_search.finditer(self.getTextContent())
    res = [(r.group(),r.groupdict()) for r in res]
    return res

  security.declareProtected(Permissions.View, 'getImplicitSuccessorValueList')
  def getImplicitSuccessorValueList(self):
    """
    Find objects which we are referencing (if our text_content contains
    references of other documents). The actual search is delegated to
    Document_findImplicitSuccessor script. We can use only complete coordinate
    triplets (reference-version-language) or also partial (e.g. reference only).
    Normally, Document_findImplicitSuccessor would use getLatestVersionValue to
    return only the most recent/relevant version.
    """
    # XXX results should be cached as volatile attributes
    # XXX-JPS - Please use TransactionCache in ERP5Type for this
    # TransactionCache does all the work for you
    lst = []
    for ref in self._getImplicitSuccessorReferenceList():
      r = ref[1]
      res = self.Document_findImplicitSuccessor(**r)
      if len(res)>0:
        lst.append(res[0].getObject())
    return lst

  security.declareProtected(Permissions.View, 'getImplicitPredecessorValueList')
  def getImplicitPredecessorValueList(self):
    """
      This function tries to find document which are referencing us - by reference only, or
      by reference/language etc.
      Uses customizeable script Document_findImplicitPredecessorList.
      
      It is mostly implementation level - depends on what parameters we use to identify
      document, and on how a doc must reference me to be my predecessor (reference only,
      or with a language, etc
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


  ### Version and language getters
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
    # User portal_catalog
    pass

  security.declareProtected(Permissions.View, 'getVersionValueList')
  def getVersionValueList(self, version=None, language=None):
    """
      Returns a list of documents with same reference, same portal_type
      but different version and given language or any language if not given.
    """
    # User portal_catalog
    pass

  security.declareProtected(Permissions.View, 'isVersionUnique')
  def isVersionUnique(self):
    """
      Returns true if no other document has the same version and language
    """
    # User portal_catalog
    pass

  security.declareProtected(Permissions.View, 'getLatestRevisionValue')
  def getLatestRevisionValue(self):
    """
      Returns the latest revision of ourselves
    """
    # User portal_catalog
    pass

  security.declareProtected(Permissions.View, 'getRevisionValueList')
  def getRevisionValueList(self):
    """
      Returns a list revision strings for a given reference, version, language
    """
    # User portal_catalog
    pass
  
  security.declareProtected(Permissions.ModifyPortalContent, 'setNewRevision')
  def setNewRevision(self):
    """
      Set a new revision number automatically
      Delegates to ZMI script because revision numbering policies can be different.
      Should be called by interaction workflow upon appropriate action.
    """
    # User portal_catalog without security
    method = self._getTypeBasedMethod('getNewRevisionNumber', 
        fallback_script_id = 'Document_getNewRevisionNumber')
    new_rev = method()
    self.setRevision(new_rev)
  
  security.declareProtected(Permissions.View, 'getLanguageList')
  def getLanguageList(self, version=None):
    """
      Returns a list of languages which this document is available in
      for the current user.
    """
    # User portal_catalog
    pass

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
      user_login = self.portal_something.getUserLogin()
    return self._getTypeBasedMethod('getPropertyDictFromUserLogin',
        fallback_script_id='Document_getPropertyDictFromUserLogin')

  security.declareProtected(Permissions.ModifyPortalContent,'getPropertyDictFromContent')
  def getPropertyDictFromContent(self):
    """
      Based on the document content, find out as many properties as needed.
      returns properties which should be set on the document
    """
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
        raise AttributeError, "explain what..."
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
        raise AttributeError, "explain what..."
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
