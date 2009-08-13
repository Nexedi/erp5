# -*- coding: utf-8 -*-
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

import re, socket, sys
from DateTime import DateTime
from operator import add
from xmlrpclib import Fault
from zLOG import LOG, INFO
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from Acquisition import aq_base
from Globals import PersistentMapping
from Globals import get_request
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.DateUtils import convertDateToHour, number_of_hours_in_day, number_of_hours_in_year
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.Base import WorkflowMethod
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.ExtensibleTraversable import ExtensibleTraversableMixIn
from Products.ERP5Type.Cache import getReadOnlyTransactionCache, DEFAULT_CACHE_SCOPE
from Products.ERP5.Document.Url import UrlMixIn
from Products.ERP5.Tool.ContributionTool import MAX_REPEAT
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from AccessControl import Unauthorized
import zope.interface
import string
from OFS.Image import Pdata

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

class DocumentProxyError(Exception):pass

class NotConvertedError(Exception):pass

class ConversionCacheMixin:
  """
    This class provides a generic API to store in the ZODB
    various converted versions of a file or of a string.

    Versions are stored in dictionaries; the class stores also
    generation time of every format and its mime-type string.
    Format can be a string or a tuple (e.g. format, resolution).
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getCacheFactory(self):
    """
    """
    if self.isTempObject():
      return
    cache_tool = getToolByName(self, 'portal_caches')
    preference_tool = getToolByName(self, 'portal_preferences')
    cache_factory_name = preference_tool.getPreferredConversionCacheFactory('document_cache_factory')
    cache_factory = cache_tool.getRamCacheRoot().get(cache_factory_name)
    #XXX This conditional statement should be remove as soon as
    #Broadcasting will be enable among all zeo clients.
    #Interaction which update portal_caches should interact with all nodes.
    if cache_factory is None and getattr(cache_tool, cache_factory_name, None) is not None:
      #ram_cache_root is not up to date for current node
      cache_tool.updateCache()
    return cache_tool.getRamCacheRoot().get(cache_factory_name)

  security.declareProtected(Permissions.ModifyPortalContent, 'clearConversionCache')
  def clearConversionCache(self):
    """
    """
    if self.isTempObject():
      self.temp_conversion_data = {}
      return
    for cache_plugin in self._getCacheFactory().getCachePluginList():
      cache_plugin.delete(self.getPath(), DEFAULT_CACHE_SCOPE)

  security.declareProtected(Permissions.View, 'updateConversionCache')
  def updateConversionCache(self):
    """
    """
    if self.isTempObject():
      if getattr(aq_base(self), 'temp_conversion_data', None) is None:
        self.temp_conversion_data = {}
      return
    cache_factory = self._getCacheFactory()
    cache_duration = cache_factory.cache_duration
    for cache_plugin in cache_factory.getCachePluginList():
      cache_plugin.initCacheStorage()
      if not cache_plugin.has_key(self.getPath(), DEFAULT_CACHE_SCOPE):
        cache_dict = {}
        cache_plugin.set(self.getPath(), DEFAULT_CACHE_SCOPE, cache_dict, cache_duration=cache_duration)

  security.declareProtected(Permissions.View, 'hasConversion')
  def hasConversion(self, **kw):
    """
    """
    self.updateConversionCache()
    cache_id = self.generateCacheId(**kw)
    if self.isTempObject():
      temp_conversion_dict = getattr(aq_base(self), 'temp_conversion_data')
      return temp_conversion_dict.has_key(cache_id)
    cache_factory = self._getCacheFactory()
    plugin_list = cache_factory.getCachePluginList()
    #If there is no plugin list return False OR one them is doesn't contain
    #cache_id for givent scope, return False
    for cache_plugin in plugin_list:
      if cache_plugin.has_key(self.getPath(), DEFAULT_CACHE_SCOPE):
        cache_entry = cache_plugin.get(self.getPath(), DEFAULT_CACHE_SCOPE)
        if cache_entry.getValue().has_key(cache_id):
          return True
    return False

  security.declareProtected(Permissions.ModifyPortalContent, 'setConversion')
  def setConversion(self, data, mime=None, calculation_time=None, **kw):
    """
    """
    self.updateConversionCache()
    cache_id = self.generateCacheId(**kw)
    if self.isTempObject():
      temp_conversion_cache = getattr(aq_base(self), 'temp_conversion_data')
      temp_conversion_cache[cache_id] = (mime, aq_base(data))
      return
    cache_factory = self._getCacheFactory()
    cache_duration = cache_factory.cache_duration
    if data is not None:
      for cache_plugin in cache_factory.getCachePluginList():
        if cache_plugin.has_key(self.getPath(), DEFAULT_CACHE_SCOPE):
          cache_entry = cache_plugin.get(self.getPath(), DEFAULT_CACHE_SCOPE)
          cache_dict = cache_entry.getValue()
        else:
          cache_dict = {}
        cache_dict.update({cache_id: (mime, aq_base(data))})
        cache_plugin.set(self.getPath(), DEFAULT_CACHE_SCOPE,
                         cache_dict, calculation_time=calculation_time,
                         cache_duration=cache_duration)

  security.declareProtected(Permissions.View, 'getConversion')
  def getConversion(self, **kw):
    """
    """
    self.updateConversionCache()
    cache_id = self.generateCacheId(**kw)
    if self.isTempObject():
      temp_conversion_cache = getattr(aq_base(self), 'temp_conversion_data')
      return temp_conversion_cache[cache_id]
    for cache_plugin in self._getCacheFactory().getCachePluginList():
      cache_entry = cache_plugin.get(self.getPath(), DEFAULT_CACHE_SCOPE)
      data = cache_entry.getValue().get(cache_id)
      if data:
        return data
    raise KeyError, 'Conversion cache key does not exists for %r' % cache_id

  security.declareProtected(Permissions.View, 'getConversionSize')
  def getConversionSize(self, **kw):
    """
    """
    if self.hasConversion(**kw):
      return len(self.getConversion(**kw))
    return 0

  def generateCacheId(self, **kw):
    """Generate proper cache id based on **kw.
    Function inspired from ERP5Type.Cache
    """
    return str(makeSortedTuple(kw)).translate(string.maketrans('', ''), """[]()<>'", """)

class PermanentURLMixIn(ExtensibleTraversableMixIn):
  """
    Provides access to documents through their permanent URL.
    This class must be inherited by all document classes so
    that documents displayed outside a Web Site / Web Section
    can also use the permanent URL principle.
  """

  # Declarative security
  security = ClassSecurityInfo()

  ### Extensible content
  def _getExtensibleContent(self, request, name):
    # Permanent URL traversal
    # First we must get the logged user by forcing identification
    cache = getReadOnlyTransactionCache(self)
    # LOG('getReadOnlyTransactionCache', 0, repr(cache)) # Currently, it is always None
    if cache is not None:
      key = ('__bobo_traverse__', self, 'user')
      try:
        user = cache[key]
      except KeyError:
        user = _MARKER
    else:
      user = _MARKER
    old_user = getSecurityManager().getUser()
    if user is _MARKER:
      user = None # By default, do nothing
      if old_user is None or old_user.getUserName() == 'Anonymous User':
        user_folder = getattr(self.getPortalObject(), 'acl_users', None)
        if user_folder is not None:
          try:
            if request.get('PUBLISHED', _MARKER) is _MARKER:
              # request['PUBLISHED'] is required by validate
              request['PUBLISHED'] = self
              has_published = False
            else:
              has_published = True
            try:
              user = user_folder.validate(request)
            except AttributeError:
              # This kind of error happens with unrestrictedTraverse,
              # because the request object is a fake, and it is just
              # a dict object.
              user = None
            if not has_published:
              try:
                del request.other['PUBLISHED']
              except AttributeError:
                # The same here as above. unrestrictedTraverse provides
                # just a plain dict, so request.other does not exist.
                del request['PUBLISHED']
          except:
            LOG("ERP5 WARNING",0,
                "Failed to retrieve user in __bobo_traverse__ of WebSection %s" % self.getPath(),
                error=sys.exc_info())
            user = None
      if user is not None and user.getUserName() == 'Anonymous User':
        user = None # If the user which is connected is anonymous,
                    # do not try to change SecurityManager
      if cache is not None:
        cache[key] = user
    if user is not None:
      # We need to perform identification
      old_manager = getSecurityManager()
      newSecurityManager(get_request(), user)
    # Next get the document per name
    portal = self.getPortalObject()
    document = self.getDocumentValue(name=name, portal=portal)
    # Last, cleanup everything
    if user is not None:
      setSecurityManager(old_manager)
    if document is not None:
      document = aq_base(document.asContext(id=name, # Hide some properties to permit locating the original
                                            original_container=document.getParentValue(),
                                            original_id=document.getId(),
                                            editable_absolute_url=document.absolute_url()))
      return document.__of__(self)

    # no document found for current user, still such document may exists
    # in some cases user (like Anonymous) can not view document according to portal catalog
    # but we may ask him to login if such a document exists
    isAuthorizationForced = getattr(self, 'isAuthorizationForced', None)
    if isAuthorizationForced is not None and isAuthorizationForced():
      getDocumentValue = UnrestrictedMethod(self.getDocumentValue)
      if getDocumentValue(name=name, portal=portal) is not None:
        # force user to login as specified in Web Section
        raise Unauthorized

  security.declareProtected(Permissions.View, 'getDocumentValue')
  def getDocumentValue(self, name=None, portal=None, **kw):
    """
      Return the default document with the given
      name. The name parameter may represent anything
      such as a document reference, an identifier,
      etc.

      If name is not provided, the method defaults
      to returning the default document by calling
      getDefaultDocumentValue.

      kw parameters can be useful to filter content
      (ex. force a given validation state)

      This method must be implemented through a
      portal type dependent script:
        WebSection_getDocumentValue
    """
    if name is None:
      return self.getDefaultDocumentValue()

    cache = getReadOnlyTransactionCache(self)
    method = None
    if cache is not None:
      key = ('getDocumentValue', self)
      try:
        method = cache[key]
      except KeyError:
        pass

    if method is None:
      method = self._getTypeBasedMethod('getDocumentValue', 
              fallback_script_id='WebSection_getDocumentValue')

    if cache is not None:
      if cache.get(key, _MARKER) is _MARKER:
        cache[key] = method

    document = method(name, portal=portal, **kw)
    if document is not None:
      document = document.__of__(self)
    return document

class DocumentProxyMixin:
  """
  Provides access to documents referenced by the follow_up field
  """
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'index_html' )
  def index_html(self, REQUEST, RESPONSE, format=None, **kw):
    """ Only a proxy method """
    self.getProxiedDocument().index_html(REQUEST, RESPONSE, format, **kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getProxiedDocument' )
  def getProxiedDocument(self):
    """
    Try to retrieve the original document
    """
    proxied_document = self.getDocumentProxyValue()
    if proxied_document is None:
      raise DocumentProxyError("Unable to find a proxied document")
    return proxied_document

class UpdateMixIn:
  """
    Provides an API to compute a date index based on the update
    frequency of the document.
  """

  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation, 'getFrequencyIndex')
  def getFrequencyIndex(self):
    """
      Returns the document update frequency as an integer
      which is used by alamrs to decide which documents
      must be updates at which time. The index represents
      a time slot (ex. all days in a month, all hours in a week).
    """
    try:
      return self.getUpdateFrequencyValue().getIntIndex()
    except AttributeError:
      # Catch Attribute error or Key error - XXX not beautiful
      return 0

  security.declareProtected(Permissions.AccessContentsInformation, 'getCreationDateIndex')
  def getCreationDateIndex(self, at_date = None):
    """
    Returns the document Creation Date Index which is the creation 
    date converted into hours modulo the Frequency Index.
    """
    frequency_index = self.getFrequencyIndex()
    if not frequency_index: return -1 # If not update frequency is provided, make sure we never update
    hour = convertDateToHour(date=self.getCreationDate())
    creation_date_index = hour % frequency_index
    # in the case of bisextile year, we substract 24 hours from the creation date,
    # otherwise updating documents (frequency=yearly update) created the last
    # 24 hours of bissextile year will be launched once every 4 years.
    if creation_date_index >= number_of_hours_in_year:
      creation_date_index = creation_date_index - number_of_hours_in_day

    return creation_date_index

  security.declareProtected(Permissions.AccessContentsInformation, 'isUpdatable')
  def isUpdatable(self):
    """
      This method is used to decide which document can be updated
      in the crawling process. This can depend for example on
      workflow states (publication state,
      validation state) or on roles on the document.
    """
    method = self._getTypeBasedMethod('isUpdatable', 
        fallback_script_id = 'Document_isUpdatable')
    return method()


class Document(PermanentURLMixIn, XMLObject, UrlMixIn, ConversionCacheMixin, SnapshotMixin, UpdateMixIn):
  """
  """

  meta_type = 'ERP5 Document'
  portal_type = 'Document'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isDocument = 1
  __dav_collection__=0

  zope.interface.implements( interfaces.IDocument, )

  # Regular expressions
  href_parser = re.compile('<a[^>]*href=[\'"](.*?)[\'"]',re.IGNORECASE)
  body_parser = re.compile('<body[^>]*>(.*?)</body>', re.IGNORECASE + re.DOTALL)
  title_parser = re.compile('<title[^>]*>(.*?)</title>', re.IGNORECASE + re.DOTALL)
  base_parser = re.compile('<base[^>]*href=[\'"](.*?)[\'"][^>]*>', re.IGNORECASE + re.DOTALL)
  charset_parser = re.compile('charset="?([a-z0-9\-]+)', re.IGNORECASE)

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

  searchable_property_list = ('asText', 'title', 'description', 'id', 'reference',
                              'version', 'short_title',
                              'subject', 'source_reference', 'source_project_title',)

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
    raise NotImplementedError

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
          val = [str(val)]
        else:
          val = []
      else:
        val = [str(v) for v in list(val) if v is not None]
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
    result = []
    tmp = {}
    for match in rx_search.finditer(text):
      group = match.group()
      group_item_list = match.groupdict().items()
      group_item_list.sort()
      key = (group, tuple(group_item_list))
      tmp[key] = None
    for group, group_item_tuple in tmp.keys():
      result.append((group, dict(group_item_tuple)))
    return result

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
    tv = getTransactionalVariable(self) # XXX Performance improvement required
    cache_key = ('getImplicitSuccessorValueList', self.getPhysicalPath())
    try:
      return tv[cache_key]
    except KeyError:
      pass

    reference_list = [r[1] for r in self.getSearchableReferenceList()]
    result = self.Base_getImplicitSuccessorValueList(reference_list)
    tv[cache_key] = result
    return result

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
    tv = getTransactionalVariable(self) # XXX Performance improvement required
    cache_key = ('getImplicitPredecessorValueList', self.getPhysicalPath())
    try:
      return tv[cache_key]
    except KeyError:
      pass

    method = self._getTypeBasedMethod('getImplicitPredecessorValueList', 
        fallback_script_id = 'Base_getImplicitPredecessorValueList')
    result = method()
    tv[cache_key] = result
    return result

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
      # remove last version of document itself from related documents
      lista_latest.pop(self.getLatestVersionValue()) 

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

    # if language was given return it (if there are any docs in this language)
    if language is not None:
      try:
        return res[0].getObject()
      except IndexError:
        return None
    else:
      first = res[0]
      in_original = None
      for ob in res:
        if ob.getVersion() != first.getVersion():
          # we are out of the latest version - return in_original or first
          if in_original is not None:
            return in_original.getObject()
          else:
            return first.getObject() # this shouldn't happen in real life
        if ob.getLanguage() == user_language:
          # we found it in the user language
          return ob.getObject()
        if ob.getLanguage() == original_language:
          # this is in original language
          in_original = ob
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

  security.declareProtected(Permissions.AccessContentsInformation, 'getRevision')
  def getRevision(self):
    """
      Returns the current revision by analysing the change log
      of the current object. The return value is a string
      in order to be consistent with the property sheet
      definition.
    """
    getInfoFor = getToolByName(self, 'portal_workflow').getInfoFor
    revision = len(getInfoFor(self, 'history', (), 'edit_workflow'))
    # XXX Also look at processing_status_workflow for compatibility.
    for history_item in getInfoFor(self, 'history', (),
                                   'processing_status_workflow'):
      if history_item.get('action') == 'edit':
        revision += 1
    return str(revision)

  security.declareProtected(Permissions.AccessContentsInformation, 'getRevisionList')
  def getRevisionList(self):
    """
      Returns the list of revision numbers of the current document
      by by analysing the change log of the current object.
    """
    return map(str, range(1, 1 + int(self.getRevision())))

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
                where_expression="validation_state NOT IN ('cancelled', 'deleted')")
      if self.getVersion(): kw['version'] = self.getVersion()
      if self.getLanguage(): kw['language'] = self.getLanguage()
      document_list = catalog.unrestrictedSearchResults(**kw)
      existing_document = None
      # Select the first one which is not self and which
      # shares the same coordinates
      document_list = list(document_list)
      document_list.sort(key=lambda x: x.getId())
      #LOG('[DMS] Existing documents for %s' %self.getSourceReference(), INFO, len(document_list))
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
          raise Unauthorized, "[DMS] You are not allowed to update the existing document which has the same coordinates (id %s)" % existing_document.getId()
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
      raise NotConvertedError
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
    """
    method = self._getTypeBasedMethod('getStandardFileName', 
        fallback_script_id = 'Document_getStandardFileName')
    return method()

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
    # Preference is made of a sequence of 'user_login', 'content', 'file_name', 'input'
    method = self._getTypeBasedMethod('getPreferredDocumentMetadataDiscoveryOrderList', 
        fallback_script_id = 'Document_getPreferredDocumentMetadataDiscoveryOrderList')
    order_list = list(method())
    order_list.reverse()
    # build a dictionary according to the order
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

    if file_name is not None:
      # filename is often undefined....
      kw['source_reference'] = file_name
    # Prepare the content edit parameters - portal_type should not be changed
    kw.pop('portal_type', None)
    # Try not to invoke an automatic transition here
    self._edit(**kw)
    # Finish ingestion by calling method
    self.finishIngestion()
    self.reindexObject()
    # Revision merge is tightly coupled
    # to metadata discovery - refer to the documentation of mergeRevision method
    merged_doc = self.mergeRevision()
    merged_doc.reindexObject()
    return merged_doc

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
      return 'text/html', '' # XXX - Why ?
    if format in ('text', 'txt'):
      return 'text/plain', '' # XXX - Why ?
    raise NotImplementedError

  def getConvertedSize(self, format):
    """
      Returns the size of the converted document
    """
    format, data = self.convert(format)
    return len(data)

  security.declareProtected(Permissions.View, 'asSubjectText')
  def asSubjectText(self, **kw):
    """
      Converts the subject of the document to a textual representation.
    """
    subject = self.getSubject()
    if not subject:
      # XXX not sure if this fallback is a good idea.
      subject = self.getTitle()
    if subject is None:
      subject = ''
    return str(subject)

  security.declareProtected(Permissions.View, 'asText')
  def asText(self, **kw):
    """
      Converts the content of the document to a textual representation.
    """
    kw['format'] = 'txt'
    mime, data = self.convert(**kw)
    return str(data)

  security.declareProtected(Permissions.View, 'asEntireHTML')
  def asEntireHTML(self, **kw):
    """
      Returns a complete HTML representation of the document
      (with body tags, etc.). Adds if necessary a base
      tag so that the document can be displayed in an iframe
      or standalone.

      Actual conversion is delegated to _asHTML
    """
    html = self._asHTML(**kw)
    if self.getUrlString():
      # If a URL is defined, add the base tag
      # if base is defined yet.
      html = str(html)
      if not html.find('<base') >= 0:
        base = '<base href="%s">' % self.getContentBaseURL()
        html = html.replace('<head>', '<head>%s' % base)
      self.setConversion(html, mime='text/html', format='base-html')
    return html

  security.declarePrivate('_asHTML')
  def _asHTML(self, **kw):
    """
      A private method which converts to HTML. This method
      is the one to override in subclasses.
    """
    if not self.hasBaseData():
      raise ConversionError('This document has not been processed yet.')
    if self.hasConversion(format='base-html'):
      # FIXME: no substitution may occur in this case.
      mime, data = self.getConversion(format='base-html')
      return data
    kw['format'] = 'html'
    mime, html = self.convert(**kw)
    return html

  security.declareProtected(Permissions.View, 'asStrippedHTML')
  def asStrippedHTML(self, **kw):
    """
      Returns a stripped HTML representation of the document
      (without html and body tags, etc.) which can be used to inline
      a preview of the document.
    """
    if not self.hasBaseData():
      return ''
    if self.hasConversion(format='stripped-html'): # XXX this is redundant since we never set it
      # FIXME: no substitution may occur in this case.
      mime, data = self.getConversion(format='stripped-html')
      return data
    kw['format'] = 'html'
    mime, html = self.convert(**kw)
    return self._stripHTML(str(html))

  def _guessEncoding(self, string):
    """
      Try to guess the encoding for this string.
      Returns None if no encoding can be guessed.
    """
    try:
      import chardet
    except ImportError:
      return None
    return chardet.detect(string).get('encoding', None)

  def _stripHTML(self, html, charset=None):
    """
      A private method which can be reused by subclasses
      to strip HTML content
    """
    body_list = re.findall(self.body_parser, str(html))
    if len(body_list):
      stripped_html = body_list[0]
    else:
      stripped_html = html
    # find charset and convert to utf-8
    charset_list = self.charset_parser.findall(str(html)) # XXX - Not efficient if this 
                                         # is datastream instance but hard to do better
    if charset and not charset_list:
      # Use optional parameter is we can not find encoding in HTML
      charset_list = [charset]
    if charset_list and charset_list[0] not in ('utf-8', 'UTF-8'):
      try:
        stripped_html = unicode(str(stripped_html), 
                                charset_list[0]).encode('utf-8')
      except (UnicodeDecodeError, LookupError):
        return str(stripped_html)
    return stripped_html


  security.declareProtected(Permissions.AccessContentsInformation, 'getContentInformation')
  def getContentInformation(self):
    """
    Returns the content information from the HTML conversion.
    The default implementation tries to build a dictionnary
    from the HTML conversion of the document and extract
    the document title.
    """
    result = {}
    html = self.asEntireHTML()
    if not html: return result
    title_list = re.findall(self.title_parser, str(html))
    if title_list:
      result['title'] = title_list[0]
    return result

  # Base format support
  security.declareProtected(Permissions.ModifyPortalContent, 'convertToBaseFormat')
  def convertToBaseFormat(self, **kw):
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
      message = self._convertToBaseFormat() # Call implemetation method
      self.clearConversionCache() # Conversion cache is now invalid
      if message is None:
        # XXX Need to translate.
        message = 'Converted to %s.' % self.getBaseContentType()
      self.convertFile(comment=message) # Invoke workflow method
    except NotImplementedError:
      message = ''
    return message

  def _convertToBaseFormat(self):
    """
    """
    raise NotImplementedError

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isSupportBaseDataConversion')
  def isSupportBaseDataConversion(self):
    """
    """
    return False

  def convertFile(self, **kw):
    """
    Workflow transition invoked when conversion occurs.
    """
  convertFile = WorkflowMethod(convertFile)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMetadataMappingDict')
  def getMetadataMappingDict(self):
    """
    Return a dict of metadata mapping used to update base metadata of the
    document
    """
    try:
      method = self._getTypeBasedMethod('getMetadataMappingDict')
    except KeyError, AttributeError:
      method = None
    if method is not None: 
      return method()
    else:
      return {}

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

  security.declareProtected(Permissions.View, 'isIndexContent')
  def isIndexContent(self, container=None):
    """
      Ask container if we are and index, or a content.
      In the vast majority of cases we are content.
      This method is required in a crawling process to make
      a difference between URLs which return an index (ex. the 
      list of files in remote server which is accessed through HTTP)
      and the files themselves.
    """
    if container is None:
      container = self.getParentValue()
    if hasattr(aq_base(container), 'isIndexContent'):
      return container.isIndexContent(self)
    return False

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

  security.declareProtected(Permissions.ModifyPortalContent, '_setBaseData')
  def _setBaseData(self, data):
    self._baseSetBaseData(Pdata(data))

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBaseData')
  def getBaseData(self, default=None):
    """return BaseData as str."""
    base_data = self._baseGetBaseData()
    if base_data is None:
      return None
    else:
      return str(base_data)

  security.declareProtected(Permissions.ModifyPortalContent, '_setData')
  def _setData(self, data):
    self._baseSetData(Pdata(data))

  security.declareProtected(Permissions.AccessContentsInformation, 'getData')
  def getData(self, default=None):
    """return Data as str."""
    data = self._baseGetData()
    if data is None:
      return None
    else:
      return str(data)
