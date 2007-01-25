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

import re
import string
import pdb

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir
from Products.ERP5.Document.BusinessTemplate import getChainByType
from zLOG import LOG
from DateTime import DateTime
from Acquisition import aq_base

NO_DISCOVER_METADATA_KEY = '_v_no_discover_metadata'
USER_NAME_KEY = '_v_document_user_login'
TEMP_NEW_OBJECT_KEY = '_v_new_object'

_marker = []  # Create a new marker object.

class ContributionTool(BaseTool):
  """
    ContributionTool provides an abstraction layer to unify the contribution
    of documents into an ERP5Site.

    ContributionTool is configured in portal_types in
    such way that it can store Text, Spreadsheet, PDF, etc.

    The method to use is portal_contributions.newContent, which should receive
    either a portal type or a file name from which type can be derived or a file from which
    content type can be derived, otherwise it will fail.

    Configuration Scripts:
      - ContributionTool_getPropertyDictFromFileName: receives file name and a 
        dict derived from filename by regular expression, and does any necesary
        operations (e.g. mapping document type id onto a real portal_type).
  """
  title = 'Contribution Tool'
  id = 'portal_contributions'
  meta_type = 'ERP5 Contribution Tool'
  portal_type = 'Contribution Tool'
  allowed_types = ('File', 'Image', 'Text') # XXX Is this really needed ?

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainContributionTool', _dtmldir )

  security.declarePrivate('findTypeName')
  def findTypeName(self, file_name, ob):
    """
      Finds the appropriate portal type based on the file name
      or if necessary the content of ob
    """
    portal_type = None
    # We should only consider those portal_types which share the
    # same meta_type with the current object
    valid_portal_type_list = []
    for pt in self.portal_types.objectValues():
      if pt.meta_type == ob.meta_type:
        valid_portal_type_list.append(pt.id)

    # Check if the filename tells which portal_type this is
    portal_type_list = self.getPropertyDictFromFileName(file_name).get('portal_type', [])
    if len(portal_type_list) == 1:
      # if we have only one, then this is it
      return portal_type_list[0]

    # If it is still None, we need to read the document
    # to check which of the candidates is suitable
    if portal_type is None:
      # The document is now responsible of telling all its properties
      portal_type = ob.getPropertyDictFromContent().get('portal_type', None)
      if portal_type is not None:
        # we check if it matches the candidate list, if there were any
        if len(portal_type_list)>1 and portal_type not in portal_type_list:
          raise TypeError('%s not in the list of %s' % (portal_type, str(portal_type_list)))
        return portal_type
      else:
        # if not found but the candidate list is there, return the first
        if len(portal_type_list)>0:
          return portal_type_list[0]

    if portal_type is None:
      # We can not do anything anymore
      return ob.portal_type
      #return None

    if portal_type not in valid_portal_type_list:
      # We will not be able to migrate ob to portal_type
      #return ob.portal_type
      return None

    return portal_type

  security.declareProtected(Permissions.AddPortalContent, 'newContent')
  def newContent(self, id=None, portal_type=None,
                       discover_metadata=1, temp_object=0,
                       user_login=None, **kw):
    """
      The newContent method is overriden to implement smart content
      creation by detecting the portal type based on whatever information
      was provided and finding out the most appropriate module to store
      the content.

      user_login is the name under which the content will be created
      XXX - Is this a security hole ?

      NOTE:
        We always generate ID. So, we must prevent using the one
        which we were provided.
    """
    # Temp objects use the standard newContent from Folder
    if temp_object:
      # For temp_object creation, use the standard method
      return BaseTool.newContent(self, id=id, portal_type=portal_type, temp_object=1, **kw)

    # Try to find the file_name
    file = kw.get('file', None)
    if file is not None:
      file_name = file.filename
    else:
      file_name = None

    # If the portal_type was provided, we can go faster
    if portal_type is not None and portal_type != '':
      # We know the portal_type, let us find the module
      module = self.getDefaultModule(portal_type)

      # And return a document
      # NOTE: we use the module ID generator rather than the provided ID
      document = module.newContent(portal_type=portal_type, **kw)
      if discover_metadata: document.discoverMetadata(file_name=file_name, user_login=user_login)
      return document

    # From here, there is no hope unless a file was provided    
    if file is None:
      raise ValueError, "could not determine portal type"

    # So we will simulate WebDAV to get an empty object
    # with PUT_factory
    ob = self.PUT_factory( file_name, None, None )

    # Raise an error if we could not guess the portal type
    # XXX Maybe we should try to pass the typ param
    if ob is None:
      raise ValueError, "Could not determine the document type"

    # Then put the file inside ourselves for a short while
    BaseTool._setObject(self, file_name, ob)
    document = self[file_name]

    # Then edit the document contents (so that upload can happen)
    document._edit(**kw)

    # Remove the object from ourselves
    BaseTool._delObject(self, file_name)

    # Move the document to where it belongs
    if not discover_metadata: setattr(self, NO_DISCOVER_METADATA_KEY, 1)
    setattr(ob, USER_NAME_KEY, user_login)
    document = self._setObject(file_name, ob)

    # Time to empty the cache
    if hasattr(self, '_v_document_cache'):
      if self._v_document_cache.has_key(file_name):
        del self._v_document_cache[file_name]

    # Reindex it and return the document
    # XXX seems we have to commit now, otherwise it is not reindexed properly later
    # dunno why
    get_transaction().commit()
    document.reindexObject()
    return document

  security.declareProtected( Permissions.AddPortalContent, 'fromXML' )
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
    if property_dict.has_key('portal_type'):
      # we have to return portal_type as a tuple
      # because we can allow for having multiple types (candidates)
      property_dict['portal_type'] = (property_dict['portal_type'],)
    else:
      # we have to find candidates by file extenstion
      try:
        index = file_name.rfind('.')
        if index != -1:
          ext = file_name[index+1:]
          property_dict['portal_type'] = self.ContributionTool_getCandidateTypeListByExtension(ext)
      except ValueError: # no dot in file name
        pass
    return property_dict

  # WebDAV virtual folder support
  def _setObject(self, name, ob, user_login=None):
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
    # Find the portal type based on file name and content
    # We provide ob in the context of self to make sure scripting is possible
    portal_type = self.findTypeName(name, ob.__of__(self))
    if portal_type is None:
      raise TypeError, "Unable to determine portal type"
    
    # We know the portal_type, let us find the module
    module = self.getDefaultModule(portal_type)

    # Set the object on the module and fix the portal_type and id
    new_id = module.generateNewId()
    ob.portal_type = portal_type
    ob.id = new_id
    module._setObject(new_id, ob)

    # We can now discover metadata unless NO_DISCOVER_METADATA_KEY was set on ob
    document = module[new_id]
    user_login = getattr(self, USER_NAME_KEY, None)
    if not getattr(ob, NO_DISCOVER_METADATA_KEY, 0): document.discoverMetadata(file_name=name, user_login=user_login)

    # Keep the document close to us
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
    if hasattr(self, '_v_document_cache'):
      document_url = self._v_document_cache.get(id, None)
      if document_url is not None:
        return self.getPortalObject().unrestrictedTraverse(document_url)

    if default is _marker:
      return BaseTool._getOb(self, id)
    else:
      return BaseTool._getOb(self, id, default=default)

  def _delOb(self, id):
    """
    We don't need to delete, since we never set here
    """
    if hasattr(self, '_v_document_cache'):
      document_url = self._v_document_cache.get(id, None)
      if document_url is not None:
        document = self.getPortalObject().unrestrictedTraverse(document_url)
        if document is not None:
          document.getParentValue()._delOb(document.getId())
          del self._v_document_cache[id]
          return

    return BaseTool._delOb(self, id)

InitializeClass(ContributionTool)

# vim: filetype=python syntax=python shiftwidth=2 
