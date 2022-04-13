# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.ERP5Type.Globals import InitializeClass
from ZODB.POSException import ConflictError
from Products.ERP5Type import Permissions
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5Type.Utils import convertToUpperCase
from erp5.component.mixin.CachedConvertableMixin import CachedConvertableMixin
import os
import re
import six

try:
  import magic
except ImportError:
  magic = None

VALID_ORDER_KEY_LIST = ('user_login', 'content', 'filename', 'file_name',
                        'input')

CONTENT_INFORMATION_FORMAT = '_idiscoverable_content_information'

class ConversionError(Exception):pass

class DiscoverableMixin(CachedConvertableMixin):
  """
  Implements IDiscoverable
  This class provide methods useful for Metadata extraction.
  It inherit from CachedConvertableMixin to access
  Cache storage API.
  As computed data needs to be stored in same backend.
  """
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPropertyDictFromUserLogin')
  def getPropertyDictFromUserLogin(self, user_login=None):
    """
    Based on the user_login, find out as many properties as needed.
    returns properties which should be set on the document
    """
    if user_login is None:
      user_login = getSecurityManager().getUser().getIdOrUserName()
    method = self._getTypeBasedMethod('getPropertyDictFromUserLogin',
        fallback_script_id='Document_getPropertyDictFromUserLogin')
    if method is not None:
      return method(user_login)
    return {}

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPropertyDictFromContent')
  def getPropertyDictFromContent(self):
    """
    Based on the document content, find out as many properties as needed.
    returns properties which should be set on the document
    """
    # accesss data through convert
    _, content = self.convert(None)
    if not content:
       # if document is empty, we will not find anything in its content
      return {}
    method = self._getTypeBasedMethod('getPropertyDictFromContent',
        fallback_script_id='Document_getPropertyDictFromContent')
    if method is not None:
      return method()
    return {}

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPropertyDictFromFilename')
  def getPropertyDictFromFilename(self, filename):
    """
    Based on the file name, find out as many properties as needed.
    returns properties which should be set on the document
    """
    return self.portal_contributions.getPropertyDictFromFilename(filename)


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPropertyDictFromFileName')
  getPropertyDictFromFileName = getPropertyDictFromFilename

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPropertyDictFromInput')
  def getPropertyDictFromInput(self, input_parameter_dict):
    """
    Fetch argument_dict, then filter pass this dictionary
    to getPropertyDictFromInput.
    """
    method = self._getTypeBasedMethod('getPropertyDictFromInput')
    if method is not None:
      return method(input_parameter_dict)
    return {}

  ### Metadata disovery and ingestion methods
  security.declareProtected(Permissions.ModifyPortalContent,
                            'discoverMetadata')
  @UnrestrictedMethod
  def discoverMetadata(self, filename=None, user_login=None,
                       input_parameter_dict=None):
    """
    This is the main metadata discovery function - controls the process
    of discovering data from various sources. The discovery itself is
    delegated to scripts or uses preference-configurable regexps. The
    method returns either self or the document which has been
    merged in the discovery process.

    filename - this parameter is a file name of the form "AA-BBB-CCC-223-en"

    user_login - this is a login string of a person; can be None if the user is
                 currently logged in, then we'll get him from session
    input_parameter_dict - arguments provided to Create this content by user.
    """
    if input_parameter_dict is None:
      input_parameter_dict = {}
    # Preference is made of a sequence of 'user_login', 'content', 'filename', 'input'
    method = self._getTypeBasedMethod('getPreferredDocumentMetadataDiscoveryOrderList')
    order_list = list(method())
    order_list.reverse()
    # build a dictionary according to the order
    kw = {}
    for order_id in order_list:
      result = None
      if order_id not in VALID_ORDER_KEY_LIST:
        # Prevent security attack or bad preferences
        raise AttributeError("%s is not in valid order key list" % order_id)
      method_id = 'getPropertyDictFrom%s' % convertToUpperCase(order_id)
      method = getattr(self, method_id)
      if order_id in ('filename', 'file_name',):
        if filename is not None:
          result = method(filename)
      elif order_id == 'user_login':
        if user_login is not None:
          result = method(user_login)
      elif order_id == 'input':
        if input_parameter_dict is not None:
          result = method(input_parameter_dict)
      else:
        result = method()
      if result is not None:
        for key, value in six.iteritems(result):
          if value not in (None, ''):
            kw[key]=value
    # Prepare the content edit parameters
    # User decision take precedence, never try to change this value
    portal_type = input_parameter_dict.get('portal_type')
    if not portal_type:
      # Read discovered portal_type
      portal_type = kw.pop('portal_type', None)
    if portal_type and portal_type != self.getPortalType():
      # Reingestion is required to update portal_type
      return self.migratePortalType(portal_type)
    # Try not to invoke an automatic transition here
    self._edit(**kw)
    if not portal_type:
      # If no portal_type was dicovered, pass self
      # through to portal_contribution_registry
      # to guess destination portal_type against all properties.
      # If returned portal_type is different, then reingest.
      registry = self.getPortalObject().portal_contribution_registry
      portal_type = registry.findPortalTypeName(context=self)
      if portal_type != self.getPortalType():
        return self.migratePortalType(portal_type)

    def maybeChangeState(document):
      publication_state = input_parameter_dict.get('publication_state')
      if publication_state and document.getValidationState() == 'draft':
        if publication_state == "shared":
          document.share()
        elif publication_state == "released":
          document.release()
        elif publication_state == "published":
          document.publish()


    maybeChangeState(self)
    # Finish ingestion by calling method
    self.finishIngestion() # XXX - is this really the right place ?
    self.reindexObject() # XXX - is this really the right place ?
    # Revision merge is tightly coupled
    # to metadata discovery - refer to the documentation of mergeRevision method
    merged_doc = self.mergeRevision() # XXX - is this really the right place ?
    merged_doc.reindexObject() # XXX - is this really the right place ?
    maybeChangeState(merged_doc)
    return merged_doc # XXX - is this really the right place ?

  security.declareProtected(Permissions.ModifyPortalContent, 'finishIngestion')
  def finishIngestion(self):
    """
    Finish the ingestion process by calling the appropriate script. This
    script can for example allocate a reference number automatically if
    no reference was defined.
    """
    method = self._getTypeBasedMethod('finishIngestion',
                                 fallback_script_id='Document_finishIngestion')
    return method()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getContentTypeFromContent')
  def getContentTypeFromContent(self):
    """
    Return content_type read from metadata extraction of content.
    This method is called by portal_contribution_registry
    """
    # XXX should be cached in a transactional cache, because this method
    # might be called several times by a single call of
    # portal_contribution_registry.findPortalTypeName().
    content = self.getData()
    if not content:
      return
    if magic is not None:
      # This will be delegated soon to external web service
      # like cloudooo
      # ERP5 will no longer handle data itself.
      mimedetector = magic.Magic(mime=True)
      return mimedetector.from_buffer(content)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getExtensionFromFilename')
  def getExtensionFromFilename(self, filename=None):
    """
    Return extension read from filename in lower case.
    """
    if not filename:
      filename = self.getStandardFilename()
    _, extension = os.path.splitext(filename)
    if extension:
      extension = extension[1:].lower() # remove first dot
    return extension

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getContentInformation')
  def getContentInformation(self):
    """
    Call private implementation, then store the result in conversion
    cache storage.
    """
    format_ = CONTENT_INFORMATION_FORMAT
    # How to knows if a instance implement an interface
    try:
      _, cached_value = self.getConversion(format=format_)
      return cached_value
    except KeyError:
      value = self._getContentInformation()
      self.setConversion(value, format=format_)
      return value

  def _getContentInformation(self):
    """
    Returns the content information from the HTML conversion.
    The default implementation tries to build a dictionary
    from the HTML conversion of the document and extract
    the document title.
    """
    result = {}
    try:
      html = self.asEntireHTML()
    except ConflictError:
      raise
    except Exception:
      return result
    if not html:
      return result
    title_list = re.findall(self.title_parser, str(html))
    if title_list:
      result['title'] = title_list[0]
    return result

InitializeClass(DiscoverableMixin)
