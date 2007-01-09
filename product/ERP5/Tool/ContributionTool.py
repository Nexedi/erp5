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
  allowed_types = ('File', 'Image') # XXX Is this really needed ?

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainContributionTool', _dtmldir )

  security.declarePrivate('findTypeName')
  def findTypeName(self, name, ob):
    """
      Finds the appropriate portal type based on the file name
      or if necessary the content of ob
    """
    # We should only consider those portal_types which share the
    # same meta_type with the current object
    valid_portal_type_list = []
    for pt in self.portal_types.objectValues():
      if pt.meta_type == ob.meta_type:
        valid_portal_type_list.append(pt.id)

    # Check if the filename tells which portal_type this is
    portal_type = self.getPropertyDictFromFileName(file_name).get('portal_type', None)

    # If it is still None, we need to read the document
    # to check which of the candidates is suitable
    if portal_type is None:
      # The document is now responsible of telling all its properties
      portal_type = ob.getPropertyDictFromContent().get('portal_type', None)

    if portal_type is None:
      # We can not do anything anymore
      return ob.portal_type

    if portal_type not in valid_portal_type_list:
      # We will not be able to migrate ob to portal_type
      return ob.portal_type

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
      file_name = file.name
    else:
      file_name = None

    # If the portal_type was provided, we can go faster
    if portal_type is not None:
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
    # woith PUT_factory
    ob = self.PUT_factory( file_name, None, None )

    # Then put the file inside ourselves for a short while
    BaseTool._setObject(self, name, ob)
    document = self[name]
    
    # Then edit the document contents (so that upload can happen)
    document._edit(**kw)
    
    # Remove the object from ourselves
    self._delObject(name, ob)

    # Move it to where it belongs
    if not discover_metadata: setattr(self, NO_DISCOVER_METADATA_KEY, 1)
    setattr(ob, USER_NAME_KEY, user_login)
    document = self._setObject(name, ob)

    # Reindex it and return it
    document.immediateReindexObject()
    return document

  security.declareProtected( Permissions.AddPortalContent, 'fromXML' )
  def newXML(self, xml):
    """
      Create a new content based on XML data. This is intended for contributing
      to ERP5 from another application.
    """
    pass

  security.declareProtected(Permissions.ModifyPortalContent,'getPropertyDictFromFileName')
  def getPropertyDictFromFileName(self, fname):
    """
      Gets properties from filename. File name is parsed with a regular expression
      set in preferences. The regexp should contain named groups.
    """
    rx_src = self.portal_preferences.getPreferredDocumentFileNameRegularExpression()
    if not rx_src:
      return
    rx_parse = re.compile()
    if rx_parse is None:
      return
    dict = rx_parse.match(fname)
    method = self._getTypeBasedMethod('getPropertyDictFromFileName', 
        fallback_script_id = 'ContributionTool_getPropertyDictFromFileName')
    return method(fname, **dict)

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

    # Return document to newContent method
    return document
    
InitializeClass(ContributionTool)
