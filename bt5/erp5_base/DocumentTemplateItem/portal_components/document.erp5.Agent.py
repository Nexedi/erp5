##############################################################################
#
# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved.
#               Sebastien Robin <seb@nexedi.com>
#               Kevin Deldycke <kevin@nexedi.com>
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
from erp5.component.document.Image import Image
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Core.Folder import Folder


class Agent(Folder, Image):
  """
    An Agent is a Person who is permitted to perform some actions on the bank
    account according to Privileges.
  """
  # CMF Type Definition
  meta_type = 'ERP5 Agent'
  portal_type = 'Agent'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.Agent
                    )

  # content_type property is also a method from PortalFolder, so we need a
  # valid type by default.
  content_type = ''

  def __init__(self, *args, **kw):
    Folder.__init__(self, *args, **kw)
    Image.__init__(self, *args, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'viewImage')
  viewImage = Image.index_html

  security.declareProtected(Permissions.ModifyPortalContent, 'importSignature')
  def importSignature(self, import_file=None, form_id=None, REQUEST=None, **kw):
    """
      Imports a scan of a signature.
    """
    if REQUEST is None:
      REQUEST = getattr(self, 'REQUEST', None)

    if (import_file is None) or (len(import_file.read()) == 0) :
      if REQUEST is not None :
        REQUEST.RESPONSE.redirect("%s?portal_status_message=No+file+or+an+empty+file+was+specified"
                                  % self.absolute_url())
        return
      else :
        raise RuntimeError, 'No file or an empty file was specified'

    import_file.seek(0)
    self.manage_upload(file=import_file)
    #    self._data = import_file.read()

    if REQUEST is not None:
      ret_url = self.absolute_url() + '/' + REQUEST.get('form_id', 'view')
      REQUEST.RESPONSE.redirect("%s?portal_status_message=Signature+Imported+Successfully"
                                % ret_url)
