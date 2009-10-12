#############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#               Guy Oswald OBAMA <guy@nexedi.com>
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

from Products.ERP5Type.Utils import writeLocalPropertySheet, writeLocalDocument
from Products.PythonScripts.Utility import allow_class
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass

class LocalGenerator:
  """ Create Local PropertySheets and Documents
  """
  
  copyright_text = """
#############################################################################
#
# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved.
#                         Jean-Paul Smets-Solanes <jp@nexedi.com> 
#                         Kevin Deldycke <kevin@nexedi.com> 
#                         Guy Oswald OBAMA <guy@nexedi.com> 
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

"""

  # Declarative security
  security = ClassSecurityInfo()
  
  security.declareProtected( Permissions.ManagePortal,
                             'generateLocalPropertySheet')
  def generateLocalPropertySheet(self, property_sheet_name, properties = []):
    """ Writes a Local PropertySheet.
      `property_sheet_name` : name of this property sheet
      `properties` : a list of dict representing properties 
    """
    class_name = property_sheet_name.replace(' ', '')
    formating_dict = { 'class_name' : class_name,
                       'property_sheet_name': property_sheet_name}
    
    string = self.copyright_text + """
class %(class_name)s :
  \"\"\"%(property_sheet_name)s properties and categories.
  \"\"\"
  _properties = (
"""  % formating_dict

    for prop in properties:
      string += """
    {"""
      for k, v in prop.items() :
        string += """
      '%s'          : '%s',""" % (k, v)
      string += """
    }, """
    
    string += """
    )
  _categories = ('source_section', 'destination_section')
    
"""
    writeLocalPropertySheet(class_name, string)
  
  
  security.declareProtected(Permissions.ManagePortal, 'generateLocalDocument')
  def generateLocalDocument(self, class_name, portal_type_name):
    """Writes local Document.
      `class_name` name of the class to be written
      `portal_type_name` name of the portal type associated to this new class
    """
    formating_dict = {
      'class_name' : class_name,
      'portal_type_name' : portal_type_name
    }
      
    string = self.copyright_text + """
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Core.Node import Node
    
class %(class_name)s(Node, XMLObject):
  \"\"\"An %(portal_type_name)s object holds the information about 
  
  %(class_name)s objects can contain Coordinate objects 
  as well a documents of various types.
  
  %(class_name)s objects can be synchronized accross multiple
  sites
  
  \"\"\"
  
  meta_type       = 'ERP5 %(portal_type_name)s'
  portal_type     = '%(portal_type_name)s'
  add_permission  = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent    = 1

  # Declarative Security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Arrow
                    , PropertySheet.Task
                    , PropertySheet.%(class_name)s
                    )
""" % formating_dict

    writeLocalDocument(class_name, string)

InitializeClass(LocalGenerator)
allow_class(LocalGenerator)
      
