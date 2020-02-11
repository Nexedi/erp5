# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

import re
from zLOG import LOG, WARNING
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.CMFCore.utils import _checkPermission
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Utils import deprecated, guessEncodingFromText
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5.Tool.ContributionTool import MAX_REPEAT
from Products.ZSQLCatalog.SQLCatalog import Query, NegatedQuery
from AccessControl import Unauthorized
import zope.interface
from Products.PythonScripts.Utility import allow_class

# Mixin Import
from Products.ERP5.mixin.cached_convertable import CachedConvertableMixin
from Products.ERP5.mixin.text_convertable import TextConvertableMixin
from Products.ERP5.mixin.downloadable import DownloadableMixin
from Products.ERP5.mixin.document import DocumentMixin
from Products.ERP5.mixin.crawlable import CrawlableMixin
from Products.ERP5.mixin.discoverable import DiscoverableMixin
from Products.ERP5.mixin.url import UrlMixin

_MARKER = []

# these property ids are unchangable
FIXED_PROPERTY_IDS = ('id', 'uid', 'rid', 'sid')

# XXX: move to an easier to configure place (System Preference ?)
VALID_TEXT_FORMAT_LIST = ('text', 'txt', 'html', 'base_html',
                          'stripped-html')

VALID_IMAGE_FORMAT_LIST = ('jpg', 'jpeg', 'png', 'gif', 'pnm', 'ppm', 'tiff', 'svg')
VALID_TRANSPARENT_IMAGE_FORMAT_LIST = ('png', 'gif', 'tiff', 'svg')

DEFAULT_DISPLAY_ID_LIST = ('nano', 'micro', 'thumbnail',
                            'xsmall', 'small', 'medium',
                            'large', 'xlarge',)
# default image qualitay (obsoleted use getPreferredImageQuality on a portal_preferences tool)
DEFAULT_IMAGE_QUALITY = 75.0

DEFAULT_CONTENT_TYPE = 'text/html'

class ConversionError(Exception):pass

class DocumentProxyError(Exception):pass

class NotConvertedError(Exception):pass
allow_class(NotConvertedError)

import base64
enc = base64.encodestring
dec = base64.decodestring
DOCUMENT_CONVERSION_SERVER_PROXY_TIMEOUT = 360
DOCUMENT_CONVERSION_SERVER_RETRY = 0
# store time (as int) where we had last failure in order
# to try using proxy server that worked the most recently
global_server_proxy_uri_failure_time = {}
from Products.CMFCore.utils import getToolByName
from functools import partial
from xmlrpclib import Fault, ServerProxy, ProtocolError
from AccessControl import Unauthorized
from Products.ERP5Type.ConnectionPlugin.TimeoutTransport import TimeoutTransport
from socket import error as SocketError
from DateTime import DateTime
class DocumentConversionServerProxy():
  """
  xmlrpc-like ServerProxy object adapted for conversion server
  """
  def __init__(self, context):
    self._serverproxy_list = []
    preference_tool = getToolByName(context, 'portal_preferences')
    self._ooo_server_retry = (
      preference_tool.getPreferredDocumentConversionServerRetry() or
      DOCUMENT_CONVERSION_SERVER_RETRY)
    uri_list = preference_tool.getPreferredDocumentConversionServerUrlList()
    if not uri_list:
      address = preference_tool.getPreferredOoodocServerAddress()
      port = preference_tool.getPreferredOoodocServerPortNumber()
      if not (address and port):
        raise ConversionError('OOoDocument: cannot proceed with conversion:'
              ' conversion server url is not defined in preferences')

      LOG('Document', WARNING, 'PreferredOoodocServer{Address,PortNumber}' + \
          ' are DEPRECATED please use PreferredDocumentServerUrl instead', error=True)

      uri_list =  ['%s://%s:%s' % ('http', address, port)]

    timeout = (preference_tool.getPreferredOoodocServerTimeout() or
               DOCUMENT_CONVERSION_SERVER_PROXY_TIMEOUT)
    for uri in uri_list:
      if uri.startswith("http://"):
        scheme = "http"
      elif uri.startswith("https://"):
        scheme = "https"
      else:
        raise ConversionError('OOoDocument: cannot proceed with conversion:'
              ' preferred conversion server url is invalid')

      transport = TimeoutTransport(timeout=timeout, scheme=scheme)

      self._serverproxy_list.append((uri, ServerProxy(uri, allow_none=True, transport=transport)))

  def _proxy_function(self, func_name, *args, **kw):
    result_error_set_list = []
    protocol_error_list = []
    socket_error_list = []
    fault_error_list = []
    count = 0
    serverproxy_list = self._serverproxy_list
    # we have list of tuple (uri, ServerProxy()). Sort by uri having oldest failure
    serverproxy_list.sort(key=lambda x: global_server_proxy_uri_failure_time.get(x[0], 0))
    while True:
      retry_server_list = []
      for uri, server_proxy in serverproxy_list:
        func = getattr(server_proxy, func_name)
        failure = True
        try:
          # Cloudooo return result in (200 or 402, dict(), '') format or just based type
          # 402 for error and 200 for ok
          result_set =  func(*args, **kw)
        except SocketError, e:
          message = 'Socket Error: %s' % (repr(e) or 'undefined.')
          socket_error_list.append(message)
          retry_server_list.append((uri, server_proxy))
        except ProtocolError, e:
          # Network issue
          message = "%s: %s %s" % (e.url, e.errcode, e.errmsg)
          if e.errcode == -1:
            message = "%s: Connection refused" % (e.url)
          protocol_error_list.append(message)
          retry_server_list.append((uri, server_proxy))
        except Fault, e:
          # Return not supported data types
          fault_error_list.append(e)
        else:
          failure = False

        if not(failure):
          try:
            response_code, response_dict, response_message = result_set
          except ValueError:
            # Compatibility for old oood, result is based type, like string
             response_code = 200

          if response_code == 200:
            return result_set
          else:
            # If error, try next one
            result_error_set_list.append(result_set)

        # Still there ? this means we had no result,
        # avoid using same server again
        global_server_proxy_uri_failure_time[uri] = int(DateTime())

      # All servers are failed
      if count == self._ooo_server_retry or len(retry_server_list) == 0:
        break
      count += 1
      serverproxy_list = retry_server_list

    # Check error type
    # Return only one error result for compability
    if len(result_error_set_list):
      return result_error_set_list[0]

    if len(protocol_error_list):
      raise ConversionError("Protocol error while contacting OOo conversion: "
                          "%s" % (','.join(protocol_error_list)))
    if len(socket_error_list):
      raise SocketError("%s" % (','.join(socket_error_list)))
    if len(fault_error_list):
      raise fault_error_list[0]

  def __getattr__(self, attr):
    return partial(self._proxy_function, attr)

from Products.ERP5.mixin.extensible_traversable import DocumentExtensibleTraversableMixin

class Document(DocumentExtensibleTraversableMixin, XMLObject, UrlMixin,
               CachedConvertableMixin, CrawlableMixin, TextConvertableMixin,
               DownloadableMixin, DocumentMixin, DiscoverableMixin):
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
  filename   -   data which might be encoded in filename
  user_login -   information about user who is contributing the file
  content    -   data which might be derived from document content

  If a certain property is defined in more than one source, it is set according to
  preference order returned by a script
     Document_getPreferredDocumentMetadataDiscoveryOrderList
     (or any type-based version since discovery is type dependent)

  Methods for discovering metadata are:

    getPropertyDictFromInput
    getPropertyDictFromFilename
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

    conversion API - not same as document - XXX BAD
    XXX make multiple interfaces

  TODO:
    - move all implementation bits to MixIn classes
    - in the end, Document class should have zero code
      and only serve as a quick and easy way to create
      new types of documents (one could even consider
      that this class should be trashed)
    -
  """

  meta_type = 'ERP5 Document'
  portal_type = 'Document'
  add_permission = Permissions.AddPortalContent
  isDocument = ConstantGetter('isDocument', value=True)
  __dav_collection__=0

  zope.interface.implements(interfaces.IConvertable,
                            interfaces.ITextConvertable,
                            interfaces.IHtmlConvertable,
                            interfaces.ICachedConvertable,
                            interfaces.IVersionable,
                            interfaces.IDownloadable,
                            interfaces.ICrawlable,
                            interfaces.IDocument,
                            interfaces.IDiscoverable,
                            interfaces.IUrl,
                           )

  # Regular expressions
  # XXX those regex are weak, fast but not reliable.
  # this is a valid url than regex are not able to parse
  # http://www.example.com//I don't care i put what/ i want/
  href_parser = re.compile('<a[^>]*href=[\'"](.*?)[\'"]',re.IGNORECASE)
  body_parser = re.compile('<body[^>]*>(.*?)</body>', re.IGNORECASE + re.DOTALL)
  title_parser = re.compile('<title[^>]*>(.*?)</title>', re.IGNORECASE + re.DOTALL)
  base_parser = re.compile('<base[^>]*href=[\'"](.*?)[\'"][^>]*>', re.IGNORECASE + re.DOTALL)
  charset_parser = re.compile('(?P<keyword>charset="?)(?P<charset>[a-z0-9\-]+)', re.IGNORECASE)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Reference
                    , PropertySheet.Document
                    , PropertySheet.ExternalDocument
                    , PropertySheet.Url
                    , PropertySheet.Periodicity
                    )

  index_html = DownloadableMixin.index_html

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
    return self._getSearchableReferenceList(text)

  security.declareProtected(Permissions.AccessContentsInformation, 'isSearchableReference')
  def isSearchableReference(self):
    """
      Determine if current document's reference can be used for searching - i.e. follows
      certain defined at system level preferences format.
    """
    reference = self.getReference()
    if reference is not None:
      return len(self._getSearchableReferenceList(reference))
    return False

  def _getSearchableReferenceList(self, text):
    """
      Extract all reference alike strings from text using for that a
      regular expression defined at system level preferences.
    """
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
    tv = getTransactionalVariable() # XXX Performance improvement required
    cache_key = ('getImplicitSuccessorValueList', self.getPhysicalPath())
    try:
      return tv[cache_key]
    except KeyError:
      pass

    reference_list = [r[1] for r in self.getSearchableReferenceList()]
    result = self._getTypeBasedMethod('getImplicitSuccessorValueList')(reference_list)
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
    return self._getTypeBasedMethod('getImplicitPredecessorValueList')()

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

    # remove this document
    lista_latest.pop(self, None)
    # remove last version of document itself from related documents
    lista_latest.pop(self.getLatestVersionValue(), None)

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
    catalog = self.getPortalObject().portal_catalog
    kw = dict(reference=self.getReference(),
              sort_on=(('version', 'descending', 'SIGNED'),))
    if language is not None:
      kw['language'] = language
    result_list = catalog(**kw)

    original_language = self.getOriginalLanguage()
    user_language = self.Localizer.get_selected_language()

    # if language was given return it (if there are any docs in this language)
    if language is not None:
      try:
        return result_list[0].getObject()
      except IndexError:
        return None
    elif result_list:
      first =  result_list[0].getObject()
      in_original = None
      for record in result_list:
        document = record.getObject()
        if document.getVersion() != first.getVersion():
          # we are out of the latest version - return in_original or first
          if in_original is not None:
            return in_original
          else:
            return first # this shouldn't happen in real life
        if document.getLanguage() == user_language:
          # we found it in the user language
          return document
        if document.getLanguage() == original_language:
          # this is in original language
          in_original = document
    # this is the only doc in this version
    return self

  security.declareProtected(Permissions.View, 'getVersionValueList')
  def getVersionValueList(self, version=None, language=None):
    """
      Returns a list of documents with same reference, same portal_type
      but different version and given language or any language if not given.
    """
    catalog = self.getPortalObject().portal_catalog
    kw = dict(portal_type=self.getPortalType(),
                   reference=self.getReference(),
                   sort_on=(('version', 'descending', 'SIGNED'),)
                  )
    if version:
      kw['version'] = version
    if language:
      kw['language'] = language
    return catalog(**kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'isVersionUnique')
  def isVersionUnique(self):
    """
      Returns true if no other document exists with the same
      reference, version and language, or if the current
      document has no reference.
    """
    if not self.getReference():
      return True
    kw = dict(portal_type=self.getPortalDocumentTypeList(),
              reference=self.getReference(),
              version=self.getVersion(),
              language=self.getLanguage(),
              query=NegatedQuery(Query(validation_state=('cancelled', 'deleted'))))
    catalog = self.getPortalObject().portal_catalog
    self_count = catalog.unrestrictedCountResults(uid=self.getUid(), **kw)[0][0]
    count = catalog.unrestrictedCountResults(**kw)[0][0]
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
    getInfoFor = self.getPortalObject().portal_workflow.getInfoFor
    revision = len(getInfoFor(self, 'history', (), 'edit_workflow'))
    # XXX Also look at processing_status_workflow for compatibility.
    revision += len([history_item for history_item in\
                 getInfoFor(self, 'history', (), 'processing_status_workflow')\
                 if history_item.get('action') == 'edit'])
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
    if self.getReference():
      invalid_validation_state_list = ('archived', 'cancelled', 'deleted')
      catalog = self.getPortalObject().portal_catalog
      # Find all document with same (reference, version, language)
      kw = dict(portal_type=self.getPortalType(),
                reference=self.getReference(),
                query=NegatedQuery(Query(validation_state=invalid_validation_state_list)),
                sort_on='creation_date')

      if self.getVersion():
        kw['version'] = self.getVersion()
      if self.getLanguage():
        kw['language'] = self.getLanguage()
      document_list = catalog.unrestrictedSearchResults(**kw)
      existing_document = None
      # Select the first one which is not self and which
      # shares the same coordinates
      for o in document_list:
        if o.getRelativeUrl() != self.getRelativeUrl() and\
           o.getVersion() == self.getVersion() and\
           o.getLanguage() == self.getLanguage():
          existing_document = o.getObject()
          if existing_document.getValidationState() not in \
            invalid_validation_state_list:
            break
      else:
        existing_document = None

      # We found an existing document to update
      if existing_document is not None:
        document = existing_document
        if not _checkPermission(Permissions.ModifyPortalContent, existing_document):
          raise Unauthorized, "[DMS] You are not allowed to update the existing document which has the same coordinates (id %s)" % existing_document.getId()
        else:
          update_kw = {}
          for k in self.propertyIds():
            if k not in FIXED_PROPERTY_IDS and self.hasProperty(k):
              update_kw[k] = self.getProperty(k)
          existing_document.edit(**update_kw)
          # Erase self
          self.getParentValue().manage_delObjects([self.getId(),])
    return document

  security.declareProtected(Permissions.AccessContentsInformation, 'getLanguageList')
  def getLanguageList(self, version=None):
    """
      Returns a list of languages which this document is available in
      for the current user.
    """
    if not self.getReference(): return []
    catalog = self.getPortalObject().portal_catalog
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
    catalog = self.getPortalObject().portal_catalog
    result_list = catalog.unrestrictedSearchResults(
                                      reference=self.getReference(),
                                      sort_on=(('creation_date',
                                                'ascending'),))
    if result_list:
      return result_list[0].getLanguage()
    return

  security.declareProtected(Permissions.View, 'asSubjectText')
  def asSubjectText(self, **kw):
    """
      Converts the subject of the document to a textual representation.
    """
    subject = self.getSubject('')
    if not subject:
      # XXX not sure if this fallback is a good idea.
      subject = self.getTitle('')
    return str(subject)

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
        base = '<base href="%s"/>' % self.getContentBaseURL()
        html = html.replace('<head>', '<head>%s' % base, 1)
      self.setConversion(html, mime='text/html', format='base-html')
    return html

  security.declarePrivate('_asHTML')
  def _asHTML(self, **kw):
    """
      A private method which converts to HTML. This method
      is the one to override in subclasses.
    """
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
    return self._stripHTML(self._asHTML(**kw))

  security.declarePrivate('_guessEncoding')
  @deprecated
  def _guessEncoding(self, string, mime='text/html'):
    """
      Deprecated method
    """
    return guessEncodingFromText(string, content_type=mime)

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
    return stripped_html

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMetadataMappingDict')
  def getMetadataMappingDict(self):
    """
    Return a dict of metadata mapping used to update base metadata of the
    document
    """
    try:
      method = self._getTypeBasedMethod('getMetadataMappingDict')
    except (KeyError, AttributeError):
      method = None
    if method is not None:
      return method()
    else:
      return {}

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
    except (KeyError, AttributeError):
      method = None
    if method is not None: method()

  security.declareProtected(Permissions.ModifyPortalContent, 'updateContentFromURL')
  def updateContentFromURL(self, repeat=MAX_REPEAT, crawling_depth=0,
                           repeat_interval=1, batch_mode=True):
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

