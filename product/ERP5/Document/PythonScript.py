##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Wenjie Zheng <wenjie.zheng@tiolive.com>
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
from AccessControl.class_init import InitializeClass
from Products.ERP5Type import Permissions, PropertySheet
from App.special_dtml import HTMLFile
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Ticket import Ticket
from Products.PythonScripts.PythonScript import \
  PythonScript as ZopePythonScript

# Only needed until skin tool is migrated
manage_addPythonScriptFormThroughZMI = \
  HTMLFile("../dtml/addPythonScriptThroughZMIForm", globals())
def addPythonScriptThroughZMI(self, id, title="", REQUEST=None):
    """Add a Python script to a folder.
    """
    type_info = self.getPortalObject().portal_types.getTypeInfo("Python Script")
    type_info.constructInstance(
      container=self,
      id=id)
    if REQUEST is not None:
        try: u = self.DestinationURL()
        except: u = REQUEST['URL1']
        REQUEST.RESPONSE.redirect(u+'/manage_main')

class PythonScriptThroughZMI(XMLObject):
    """
    Dummy class only used to do construction through zmi of PythonScript

    This class needs to be removed as soon as portal_skins is an ERP5 object
    """
    meta_type = 'ERP5 Python Script'
    constructors =  (manage_addPythonScriptFormThroughZMI,
                     addPythonScriptThroughZMI)
    icon = None

    def __init__(self, *args, **kw):
      assert False

class PythonScript(XMLObject, ZopePythonScript):
    """ Script python for ERP5
    """

    meta_type = 'ERP5 Python Script'
    portal_type = 'Python Script'
    add_permission = Permissions.AddPortalContent
    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    #View content list, Force /view, Standart option in python scripts
    manage_options = ( XMLObject.manage_options[0],
                       {'icon':'', 'label':'View','action':'view'}) \
                       + ZopePythonScript.manage_options

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.PythonScript
                      )

    def __init__(self, *args, **kw):
      """
      override to call __init__ of python scripts in order to set
      correctly bindings
      """
      XMLObject.__init__(self, *args, **kw)
      ZopePythonScript.__init__(self, *args, **kw)

    def _setBody(self, value):
      """
      override to call ZopePythonScript methods to initialize code
      """
      if value is None:
        value = ''
      self.write(value)

    def _setParameterSignature(self, value):
      """
      override to call ZopePythonScript methods to force compiling code
      """
      self._baseSetParameterSignature(value)
      self._compile()

    def _setProxyRoleList(self, value):
      """
      override to call ZopePythonScript methods
      """
      self._baseSetProxyRoleList(value)
      self.manage_proxy(roles=value)

    __call__ = ZopePythonScript.__call__

    def edit(self, **kw):
      XMLObject.edit(self, **kw)
    # We need to take __setstate__ from ZopePythonScript in order to
    # generate _v_ft attributes which is necessary to run the script
    __setstate__ = ZopePythonScript.__setstate__
