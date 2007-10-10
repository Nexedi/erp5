##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets <jp@nexedi.com>
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

import cStringIO
import re
import string
import socket
import md5
import urllib2, urllib

from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir
from Products.ERP5.Document.Url import no_crawl_protocol_list, no_host_protocol_list

from zLOG import LOG
from DateTime import DateTime
from Acquisition import aq_base

# Install openers
import ContributionOpener
opener = urllib2.build_opener(ContributionOpener.DirectoryFileHandler)
urllib2.install_opener(opener)

# A temporary hack until urllib2 supports timeout setting - XXX
import socket
socket.setdefaulttimeout(600) # 1 minute timeout

# Global parameters
TEMP_NEW_OBJECT_KEY = '_v_new_object'
MAX_REPEAT = 10

_marker = []  # Create a new marker object.

class ContributionTool(BaseTool):
  """
    ContributionTool provides an abstraction layer to unify the contribution
    of documents into an ERP5 Site.

    ContributionTool needs to be configured in portal_types (allowed contents) so
    that it can store Text, Spreadsheet, PDF, etc. 

    The main method of ContributionTool is newContent. This method can
    be provided various parameters from which the portal type and document
    metadata can be derived. 

    Configuration Scripts:

      - ContributionTool_getPropertyDictFromFileName: receives file name and a 
        dict derived from filename by regular expression, and does any necesary
        operations (e.g. mapping document type id onto a real portal_type).

    Problems which are not solved

      - handling of relative links in HTML contents (or others...)
        some text rewriting is necessary.

  """
  title = 'Contribution Tool'
  id = 'portal_contributions'
  meta_type = 'ERP5 Contribution Tool'
  portal_type = 'Contribution Tool'

  # Regular expressions
  simple_normaliser = re.compile('#.*')

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainContributionTool', _dtmldir )

  security.declarePrivate('findTypeName')
  def findTypeName(self, file_name, document, container=None):
    """
      Finds the appropriate portal type based on the file name
      or if necessary the content of the document.

      NOTE: XXX This implementation can be greatly accelerated by
      caching a dict resulting which combines getContentTypeRegistryTypeDict
      and valid_portal_type_list
    """
    def getContentTypeRegistryTypeDict():
      result = {}
      for id, pred in self.content_type_registry.listPredicates():
        (p, type) = pred
        result[type] = None
      return result

    portal_type = None
    # We should only consider those portal_types which share the
    # same constructor with the current object and which are not
    # part of the definitions of content_type_registry. For
    # example if content type registry has a definition for
    # RSS feed, then there is no reason to consider this type
    # whenever receiving some text/html content although both
    # types share the same constructor. However, if Memo has
    # same constructor as Text and Memo is not in content_type_registry
    # then it should be considered.
    extra_valid_portal_type_list = []
    content_registry_type_dict = getContentTypeRegistryTypeDict()
    portal_type_tool = self.portal_types
    for pt in portal_type_tool.objectValues():
      if hasattr(pt, 'factory') and pt.factory == portal_type_tool[document.getPortalType()].factory:
        if not content_registry_type_dict.has_key(pt.id):
          extra_valid_portal_type_list.append(pt.id)

    if not extra_valid_portal_type_list:
      # There is really no ambiguity here
      # The portal_type set by PUT_factory is appropriate
      # This is the best case we can get
      # LOG('findTypeName no ambiguity', 0, document.portal_type)
      return document.portal_type

    valid_portal_type_list = [document.portal_type] + extra_valid_portal_type_list
    # LOG('valid_portal_type_list', 0, str(valid_portal_type_list))

    # If a container is defined, filter valid portal types with allowedContentTypes
    if container is not None:
      allowed_type_list = map(lambda x: x.id, container.allowedContentTypes())
      # LOG('allowed_type_list', 0, str(allowed_type_list))
      valid_portal_type_list = filter(lambda x: x in allowed_type_list, valid_portal_type_list)
      # LOG('filtered valid_portal_type_list', 0, str(valid_portal_type_list))

    # Check if there is any intersection with index portal types
    # If not, we do not need to even check if content is an index
    is_index_candidate = False
    for index_type in self.getPortalCrawlerIndexTypeList():
      if index_type in valid_portal_type_list:
        is_index_candidate = True
        candidate_index_type = index_type

    if is_index_candidate and document.isIndexContent(container=container):
      # If this document has to be created inside an External Source (container)
      # we need to analyse its content to determine whether it is or not
      # an index document. Index documents should not be searchable as documents
      # and should not be considered in the depth calculation of the crawling 
      # process
      return candidate_index_type # We suppose that there is only one index type in allowed content types

    # Check if the filename tells which portal_type this is
    portal_type_list = self.getPropertyDictFromFileName(file_name).get('portal_type', [])
    if isinstance(portal_type_list, str): portal_type_list = [portal_type_list]
    portal_type_list = filter(lambda x: x in valid_portal_type_list, portal_type_list)
    if not portal_type_list:
      portal_type_list = valid_portal_type_list
    if len(portal_type_list) == 1:
      # if we have only one, then this is it
      # LOG('findTypeName single portal_type_list', 0, portal_type_list[0])
      return portal_type_list[0]

    # If it is still None, we need to read the document
    # to check which of the candidates is suitable
    # Let us give a chance to getPropertyDictFromContent to
    # tell us what is the portal type of this document
    content_portal_type_list = document.getPropertyDictFromContent().get('portal_type', None)
    if content_portal_type_list:
      if isinstance(portal_type, str):
        content_portal_type_list = [content_portal_type_list]
      # Filter valid candidates
      content_portal_type_list = filter(lambda x: x in portal_type_list, content_portal_type_list)
      if content_portal_type_list:
        # if we have more than one, then return the first one
        # LOG('findTypeName from content', 0, content_portal_type_list[0])
        return content_portal_type_list[0]

    # If portal_type_list is not empty, return the first one
    # LOG('findTypeName from first portal_type_list', 0, portal_type_list[0])
    return portal_type_list[0]

  security.declareProtected(Permissions.AddPortalContent, 'newContent')
  def newContent(self, id=None, portal_type=None, url=None, container=None,
                       container_path=None,
                       discover_metadata=1, temp_object=0,
                       user_login=None, data=None, file_name=None, **kw):
    """
      The newContent method is overriden to implement smart content
      creation by detecting the portal type based on whatever information
      was provided and finding out the most appropriate module to store
      the content.

      user_login is the name under which the content will be created
      XXX - this is a security hole which needs to be fixed by
      making sure only Manager can use this parameter

      container -- if specified, it is possible to define
      where to contribute the content. Else, ContributionTool
      tries to guess.

      container_path -- if specified, defines the container path
      and has precedence over container

      url -- if specified, content is download from the URL.

      NOTE:
        We always generate ID. So, we must prevent using the one
        which we were provided.
    """
    if file_name is not None: kw['file_name'] = file_name
    if data is not None: kw['data'] = data # This is only used to make sure
                                           # we can pass file as parameter to ZPublisher
                                           # whenever we ingest email
    # Temp objects use the standard newContent from Folder
    if temp_object:
      # For temp_object creation, use the standard method
      return BaseTool.newContent(self, id=id, portal_type=portal_type, temp_object=1, **kw)

    # Try to find the file_name
    file_name = None
    mime_type = None
    if not url:
      # check if file was provided
      file = kw.get('file', None)
      if file is not None:
        file_name = file.filename
      else:
        # some channels supply data and file-name separately
        # this is the case for example for email ingestion
        # in this case, we build a file wrapper for it
        data = kw.get('data', None)
        if data is not None:
          file_name = kw.get('file_name', None)
          if file_name is not None:
            file = cStringIO.StringIO()
            file.write(data)
            file.seek(0)
            kw['file'] = file
            del kw['data']
            del kw['file_name']
    else:
      # build a new file from the url
      url_file = urllib2.urlopen(url)
      data = url_file.read() # time out must be set or ... too long XXX
      file = cStringIO.StringIO()
      file.write(data)
      file.seek(0)
      # Create a file name based on the URL and quote it
      file_name = url.split('/')[-1] or url.split('/')[-2]
      file_name = urllib.quote(file_name, safe='')
      file_name = file_name.replace('%', '')
      # For URLs, we want an id by default equal to the encoded URL 
      if id is None: id = self.encodeURL(url)
      if hasattr(url_file, 'headers'):
        headers = url_file.headers
        if hasattr(headers, 'type'):
          mime_type = headers.type
      kw['file'] = file

    # If the portal_type was provided, we can go faster
    if portal_type and container is None:
      # We know the portal_type, let us find the default module
      # and use it as container
      container = self.getDefaultModule(portal_type)

    if portal_type and container is not None:
      # We could simplify things here and return a document immediately
      # NOTE: we use the module ID generator rather than the provided ID
      #document = module.newContent(portal_type=portal_type, **kw)
      #if discover_metadata:
      #  document.activate().discoverMetadata(file_name=file_name, user_login=user_login)
      #return document
      pass # XXX - This needs to be implemented once the rest is stable

    # From here, there is no hope unless a file was provided
    if file is None:
      raise ValueError, "could not determine portal type"

    # So we will simulate WebDAV to get an empty object
    # with PUT_factory - we provide the mime_type as
    # parameter
    # LOG('new content', 0, "%s -- %s" % (file_name, mime_type))
    ob = self.PUT_factory(file_name, mime_type, None)

    # Raise an error if we could not guess the portal type
    if ob is None:
      raise ValueError, "Could not determine the document type"

    # Prevent any reindexing operations
    ob.isIndexable = 0

    # Then put the file inside ourselves for a short while
    BaseTool._setObject(self, file_name, ob)
    document = BaseTool._getOb(self, file_name)

    try:
      # Then edit the document contents (so that upload can happen)
      document._edit(set_filename__=0, **kw)
      if url:
        document.fromURL(url)
    finally:
      # Remove the object from ourselves
      BaseTool._delObject(self, file_name)

    # Move the document to where it belongs
    if container_path is not None:
      container = self.getPortalObject().restrictedTraverse(container_path)
    document = self._setObject(file_name, ob, user_login=user_login, id=id,
                               container=container, discover_metadata=discover_metadata,
                               )
    document = self._getOb(file_name) # Call _getOb to purge cache

    # Notify workflows
    #document.notifyWorkflowCreated()

    # Allow reindexing, reindex it and return the document
    delattr(document, 'isIndexable')
    document.reindexObject()
    return document

  security.declareProtected( Permissions.AddPortalContent, 'newXML' )
  def newXML(self, xml):
    """
      Create a new content based on XML data. This is intended for contributing
      to ERP5 from another application.
    """
    pass

  security.declareProtected(Permissions.ModifyPortalContent,'getPropertyDictFromFileName')
  def getPropertyDictFromFileName(self, file_name):
    """
      Gets properties from filename. File name is parsed with a regular expression
      set in preferences. The regexp should contain named groups.
    """
    if file_name is None:
      return {}
    property_dict = {}
    rx_src = self.portal_preferences.getPreferredDocumentFileNameRegularExpression()
    if rx_src in ('', None):
      # we must have file name regular expression defined in preferences
      raise ValueError, '[DMS] No file name regular expression defined in preferences.'
    if rx_src:
      rx_parse = re.compile(rx_src)
      if rx_parse is not None:
        try:
          property_dict = rx_parse.match(file_name).groupdict()
        except AttributeError: # no match
          pass
    method = self._getTypeBasedMethod('getPropertyDictFromFileName', 
        fallback_script_id = 'ContributionTool_getPropertyDictFromFileName')
    property_dict = method(file_name, property_dict)
    if property_dict.get('portal_type', None) is not None:
      # we have to return portal_type as a tuple
      # because we should allow for having multiple candidate types
      property_dict['portal_type'] = (property_dict['portal_type'],)
    else:
      # we have to find candidates by file extenstion
      if file_name.rfind('.')!= -1:
        ext = file_name.split('.')[-1]
        property_dict['portal_type'] = self.ContributionTool_getCandidateTypeListByExtension(ext)
    return property_dict

  # WebDAV virtual folder support
  def _setObject(self, name, ob, user_login=None, container=None,
                       id=None, discover_metadata=1):
    """
      The strategy is to let NullResource.PUT do everything as
      usual and at the last minute put the object in a different
      location with a different portal type. This means that
      NullResource.PUT creates an empty document with PUT_factory
      then upload document data by invoking PUT on the empty
      document and finally sets the object. By overriding _setObject
      we get a chance to fix the portal_type of the document
      (as long as the one we find is compatible) and move the
      document to the appropriate module.

      content_type_registry must be set up so that an appropriate
      portal_type with appropriate meta_type is found for every
      kind of document. However, a different portal_type might
      be used in the end.

      The ContributionTool instance must be configured in such
      way that _verifyObjectPaste will return TRUE.

      Refer to: NullResource.PUT
    """
    # _setObject is called by constructInstance at a time
    # when the object has no portal_type defined yet. It
    # will be removed later on. We can safely store the
    # document inside us at this stage. Else we
    # must find out where to store it.
    if not ob.__dict__.has_key('portal_type'):
      BaseTool._setObject(self, name, ob)
      document = self[name]
    else:
      # We give the system a last chance to analyse the
      # portal_type based on the document content
      # (ex. a Memo is a kind of Text which can be identified
      # by the fact it includes some specific content)
      portal_type = self.findTypeName(name, ob.__of__(self), container=container)
      if portal_type is None: portal_type = ob.portal_type
      ob._setPortalTypeName(portal_type) # This is redundant with finishConstruction
                                       # but necessary to move objects to appropriate
                                       # location based on their content. Since the
                                       # object is already constructed here, we
                                       # can safely change its portal_type
      # Now we know the portal_type, let us find the module
      # to which we should move the document to
      if container is None:
        module = self.getDefaultModule(ob.portal_type)
      else:
        module = container
      if id is None:
        new_id = module.generateNewId()
      else:
        new_id = id
      ob.id = new_id
      existing_document = module.get(new_id, None)
      if existing_document is None:
        # There is no preexisting document - we can therefore
        # set the new object
        module._setObject(new_id, ob)
        # We can now discover metadata
        document = module[new_id]
        if discover_metadata:
          # Metadata disovery is done as an activity by default
          # If we need to discoverMetadata synchronously, it must
          # be for user interface and should thus be handled by
          # ZODB scripts
          document.activate().discoverMetadata(file_name=name, user_login=user_login)
      else:
        if document.isExternalDocument():
          document = existing_document
          # If this is an external document, update its content
          # document.activate().updateContentFromURL() # XXX I think this is no longer useful with alarms
          # XXX - Make sure this does not increase ZODB
          # XXX - what to do also with parameters (put again edit_kw) ?
          # Providing some information to the use about the fact
          # this was an existing document would also be great
        else:
          # We may have to implement additional revision support
          # to support in place contribution (ie. for a given ID)
          # but is this really useful ?
          raise NotImplementedError

      # Keep the document close to us - this is only useful for
      # file upload from webdav
      if not hasattr(self, '_v_document_cache'):
        self._v_document_cache = {}
      self._v_document_cache[name] = document.getRelativeUrl()

    # Return document to newContent method
    return document

  def _getOb(self, id, default=_marker):
    """
    Check for volatile temp object info first
    and try to find it
    """
    # Use the document cache if possible and return result immediately
    # this is only useful for webdav
    if hasattr(self, '_v_document_cache'):
      document_url = self._v_document_cache.get(id, None)
      if document_url is not None:
        del self._v_document_cache[id]
        return self.getPortalObject().unrestrictedTraverse(document_url)

    # Try first to return the real object inside
    # This is much safer than trying to access objects displayed by listDAVObjects
    # because the behaviour of catalog is unpredicatble if a string is passed
    # for a UID. For example 
    #   select path from catalog where uid = "001193.html";
    # will return the same as
    #   select path from catalog where uid = 1193;
    # This was the source of an error in which the contribution tool
    # was creating a web page and was returning a Base Category
    # when
    #   o = folder._getOb(id)
    # was called in DocumentConstructor
    result = BaseTool._getOb(self, id, default=default)
    if result is not _marker:
      return result

    # Return an object listed by listDAVObjects
    uid = str(id).split('-')[-1]
    object = self.getPortalObject().portal_catalog.unrestrictedGetResultValue(uid=uid)
    if object is not None:
      return object.getObject() # Make sure this does not break security. XXX

    # Raise an AttributeError the same way as in OFS.ObjectManager._getOb
    raise AttributeError, id


  def listDAVObjects(self):
    """
      Get all contents contributed by the current user. This is
      delegated to a script in order to help customisation.
    """
    method = getattr(self, 'ContributionTool_getMyContentList', None)
    if method is not None:
      object_list = method()
    else:
      sm = getSecurityManager()
      user = sm.getUser()
      object_list = self.portal_catalog(portal_type=self.getPortalMyDocumentTypeList(),
                                        owner=str(user))

    def wrapper(o_list):
      for o in o_list:
        o = o.getObject()
        reference = o.getReference()
        if reference:
          id = '%s-%s' % (reference, o.getUid())
        else:
          id = '%s' % o.getUid()
        yield o.getObject().asContext(id=id)

    return wrapper(object_list)

  # Crawling methods
  security.declareProtected(Permissions.View, 'normaliseURL')
  def normaliseURL(self, url, base_url=None):
    """
      Returns a normalised version of the url so
      that we do not download twice the same content.
      URL normalisation is an important part in crawlers.
      The current implementation is obviously simplistic.
      Refer to http://en.wikipedia.org/wiki/Web_crawler
      and study Harvestman for more ideas.
    """
    url = self.simple_normaliser.sub('', url)
    url_split = url.split(':')
    url_protocol = url_split[0]
    if url_protocol in no_host_protocol_list:
      return url
    if base_url and len(url_split) == 1:
      # Make relative URL absolute
      url = '%s/%s' % (base_url, url)
    return url

  security.declareProtected(Permissions.View, 'encodeURL')
  def encodeURL(self, url):
    """
    Returns the URL as an ID. ID should be chosen in such
    way that it is optimal with HBTreeFolder (ie. so that
    distribution of access time on a cluster is possible)

    NOTE: alternate approach is based on a url table
    and catalog lookup. It is faster ? Not sure. Since
    we must anyway insert objects in btrees and this
    is simimar in cost to accessing them.
    """
    # Produce an MD5 from the URL
    hex_md5 = md5.md5(url).hexdigest()
    # Take the first part in the URL which is not empty
    # LOG("encodeURL", 0, url)
    url_segment = url.split(':')[1]
    url_segment_list = url_segment.split('/')
    url_domain = None
    for url_part in url_segment_list:
      if url_part:
        url_domain = url_part
        break
    # Return encoded url
    if url_domain:
      url_domain = urllib.quote(url_domain, safe='')
      url_domain = url_domain.replace('%', '')
      return "%s-%s" % (url_domain, hex_md5)
    return hex_md5
    url = urllib.quote(url, safe='')
    url = url.replace('_', '__')
    url = url.replace('%', '_')
    return url

  security.declareProtected(Permissions.AddPortalContent, 'crawlContent')
  def crawlContent(self, content, container=None):
    """
      Analyses content and download linked pages

      XXX: missing is the conversion of content local href to something
      valid.
    """
    depth = content.getCrawlingDepth()
    if depth < 0:
      # Do nothing if crawling depth is reached
      # (this is not a duplicate code but a way to prevent
      # calling isIndexContent unnecessarily)
      return
    if not content.isIndexContent(): # Decrement depth only if it is a content document
      depth = depth - 1
    if depth < 0:
      # Do nothing if crawling depth is reached
      return
    base_url = content.getContentBaseURL()
    url_list = map(lambda url: self.normaliseURL(url, base_url), set(content.getContentURLList()))
    for url in set(url_list):
      # LOG('trying to crawl', 0, url)
      # Some url protocols should not be crawled
      if url.split(':')[0] in no_crawl_protocol_list:
        continue
      if container is None:
        #if content.getParentValue()
        # in place of not ?
        container = content.getParentValue()
      # Calculate the id under which content will be stored
      id = self.encodeURL(url)
      # Try to access the document if it already exists
      document = container.get(id, None)
      if document is None:
        # XXX - This call is not working due to missing group_method_id
        # therefore, multiple call happen in parallel and eventually fail
        # (the same URL is created multiple times)
        # LOG('activate newContentFromURL', 0, url)
        self.activate(activity="SQLQueue").newContentFromURL(container_path=container.getRelativeUrl(),
                                                      id=id, url=url, crawling_depth=depth)
      elif depth and document.getCrawlingDepth() < depth:
        # Update the crawling depth if necessary
        document._setCrawlingDepth(depth)
        document.activate().crawlContent()

  security.declareProtected(Permissions.AddPortalContent, 'updateContentFromURL')
  def updateContentFromURL(self, content, repeat=MAX_REPEAT, crawling_depth=0):
    """
      Updates an existing content.
    """
    # First, test if the document is updatable according to
    # its workflow states (if it has a workflow associated with)
    if content.isUpdatable():
      # Step 0: update crawling_depth if required
      if crawling_depth > content.getCrawlingDepth():
        content._setCrawlingDepth(crawling_depth)
      # Step 1: download new content
      try:
        url = content.asURL()
        data = urllib2.urlopen(url).read()
        file = cStringIO.StringIO()
        file.write(data)
        file.seek(0)
      except urllib2.HTTPError, error:
        if repeat == 0:
          # XXX - Call the extendBadURLList method,--NOT Implemented--
          # IDEA : ajouter l'url en question dans une list "bad_url_list" puis lors du crawling au lieu que de boucler sur 
          #        la liste des url extraites de la page web on fait un test supplementaire qui verifie que l'url n'est pas 
          #        dans la liste bad_url_lis
          raise urllib2.HTTPError
        content.activate(at_date=DateTime() + 1).updateContentFromURL(repeat=repeat - 1)
        return
      except urllib2.URLError, error:
        if repeat == 0:
          # XXX - Call the extendBadURLList method,--NOT Implemented--
          raise urllib2.URLError
        content.activate(at_date=DateTime() + 1).updateContentFromURL(repeat=repeat - 1)
        return

      # Step 2: compare and update if necessary (md5)
      # md5 stuff to compare contents
      new_content_md5 = md5.md5(data).hexdigest()
      content_md5 = content.getContentMd5()
      if content_md5 == new_content_md5:
        return
      content._edit(file=file)# Please make sure that if content is the same
                              # we do not update it
                              # This feature must be implemented by Base or File
                              # not here (look at _edit in Base)
      # Step 3: convert to base format
      content.convertToBaseFormat()
      # Step 4: activate populate (unless interaction workflow does it)
      content.activate().populateContent()
      # Step 5: activate crawlContent
      depth = content.getCrawlingDepth()
      if depth > 0:
        content.activate().crawlContent()
      content.setContentMd5(new_content_md5)

  security.declareProtected(Permissions.AddPortalContent, 'newContentFromURL')
  def newContentFromURL(self, container_path=None, id=None, repeat=MAX_REPEAT, **kw):
    """
      A wrapper method for newContent which provides extra safety
      in case or errors (ie. download, access, conflict, etc.).
      The method is able to handle a certain number of exceptions
      and can postpone itself through an activity based on
      the type of exception (ex. for a 404, postpone 1 day), using
      the at_date parameter and some standard values.

      NOTE: implementation needs to be done.
    """
    # First of all, make sure do not try to create an existing document
    if container_path is not None and id is not None:
      container = self.restrictedTraverse(container_path)
      document = container.get(id, None)
      if document is not None:
        # Document aleardy exists: no need to keep on crawling
        return
    try:
      document = self.newContent(container_path=container_path, id=id, **kw)
      if document.isIndexContent() and document.getCrawlingDepth() >= 0:
        # If this is an index document, keep on crawling even if crawling_depth is 0
        document.activate().crawlContent()
      elif document.getCrawlingDepth() > 0:
        # If this is an index document, stop crawling if crawling_depth is 0
        document.activate().crawlContent()
    except urllib2.HTTPError, error:
      if repeat == 0:
        # here we must call the extendBadURLList method,--NOT Implemented--
        # which had to add this url to bad URL list, so next time we avoid
        # crawling bad URL
        raise urllib2.HTTPError
      # Catch any HTTP error
      self.activate(at_date=DateTime() + 1).newContentFromURL(
                        container_path=container_path, id=id,
                        repeat=repeat - 1, **kw)
    except urllib2.URLError, error:
      if repeat == 0:
        # XXX - Call the extendBadURLList method, --NOT Implemented--
        raise urllib2.URLError
      print error.reason
      #if getattr(error.reason,'args',None):
        #if error.reason.args[0] == socket.EAI_AGAIN:
          ## Temporary failure in name resolution - try again in 1 day
      self.activate(at_date=DateTime() + 1,
                    activity="SQLQueue").newContentFromURL(
                      container_path=container_path, id=id,
                      repeat=repeat - 1, **kw)

InitializeClass(ContributionTool)
