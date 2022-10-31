##############################################################################
#
# Copyright (c) 2022 Nexedi SA and Contributors. All Rights Reserved.
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

import six

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet
from App.special_dtml import HTMLFile
from Products.ERP5Type.XMLObject import XMLObject
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.ERP5Type.mixin.expression import ExpressionMixin


manage_addPageTemplateFormThroughZMI = \
  HTMLFile("../dtml/addPageTemplateThroughZMIForm", globals())
def addPageTemplateThroughZMI(self, id, title="", REQUEST=None):
  """Add a Page Template to a folder.
  """
  type_info = self.getPortalObject().portal_types.getTypeInfo("Page Template")
  type_info.constructInstance(
    container=self,
    id=id)
  # TODO title
  # TODO content type etc ?
  if REQUEST is not None:
    try:
      u = self.DestinationURL()
    except Exception:
      u = REQUEST['URL1']
    REQUEST.RESPONSE.redirect(u+'/manage_main')


class PageTemplateThroughZMI(XMLObject):
  """
  Dummy class only used to do construction through zmi of PageTemplate

  This class needs to be removed as soon as portal_skins is an ERP5 object
  """
  meta_type = 'ERP5 Page Template'
  constructors =  (
    manage_addPageTemplateFormThroughZMI,
                  addPageTemplateThroughZMI,)
  icon = None

  def __init__(self, *args, **kw):
    assert False


class PageTemplate(XMLObject, ZopePageTemplate, ExpressionMixin('expression')):
  """Page Template for ERP5
  """

  meta_type = 'ERP5 Page Template'
  portal_type = 'Page Template'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # View content list, Force /view, Standard option in python scripts
  manage_options = ( ZopePageTemplate.manage_options[0],
                      {'icon':'', 'label': 'View', 'action': 'view'}) \
                      + ( XMLObject.manage_options[0], ) \
                      + ZopePageTemplate.manage_options[1:]

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.Data # for content type
                    , PropertySheet.DublinCore
                    , PropertySheet.PageTemplate
                    , PropertySheet.Reference
                    )

  isPrincipiaFolderish = False

  def __init__(self, *args, **kw):
    """
    override to call __init__ of page template in order to set
    correctly bindings
    """
    XMLObject.__init__(self, *args, **kw)
    ZopePageTemplate.__init__(self, *args, **kw)

  __call__ = ZopePageTemplate.__call__

  # keep `text` stored as unicode for page template engine, but exposed
  # as an utf-8 encoded string for ERP5 interface.
  def _setText(self, value):
    print ('_setText', repr(value))
    if six.PY2 and isinstance(value, str):
      value = value.decode('utf-8')
    self.pt_edit(value, self.getContentType())

  def getText(self, default=''):
    print('getText')
    value = self._text or default
    if six.PY2:
      value = value.encode('utf-8')
    return value

  # TODO name text text content ?

  def _setContentType(self, value):
    print ('_setContentType', repr(value))
    self.pt_edit(self._text, value)


# TODO
# use pt_setTitle for setTitle ?

# TODO do we need
  # We need to take __setstate__ from ZopePageTemplate in order to
  # generate _v_ft attributes which is necessary to run the script
  __setstate__ = ZopePageTemplate.__setstate__

# TODO test:
"""
add
set / get / edit and property type (for title, text and content type)
    also check setProperty / getProperty
render page template
view ZMI
find with catalog ?
Errors when editing
"""
