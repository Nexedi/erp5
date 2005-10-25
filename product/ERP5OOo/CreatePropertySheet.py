#############################################################################
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


from Products.PythonScripts.Utility import allow_class
from ZPublisher.HTTPRequest import FileUpload
from xml.dom.ext.reader import PyExpat
from xml.dom import Node, minidom
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, get_request
from zipfile import ZipFile, ZIP_DEFLATED
from StringIO import StringIO
from zLOG import LOG
import imghdr
import random
import getopt, sys, os
from urllib import quote

ZOPE_INSTANCE_HOME = os.environ.get("INSTANCE_HOME", "/var/lib/zope/")

class Getter_Setter:
  """
  Create PropertySheet of module
  """
  
  # Declarative security
  security = ClassSecurityInfo()
  

  security.declarePublic('create_PropertySheet')
  def create_PropertySheet(self, name_file = None, personnal_properties = []):
    """
    create PropertySheet in /var/lib/zope/Products/ERP5/PropertySheet/
    """
    path_name_file = os.path.join(ZOPE_INSTANCE_HOME, 'PropertySheet', str(name_file) + '.py')
    file = open(path_name_file,'w')
    file.seek(0)

    string = """
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

    file.write(string)
    
    string = '\n\nclass ' + str(name_file) + ' :\n'
    file.write(string)
    string = 2*' ' + '"""\n'
    file.write(string)
    string = 6*' ' + str(name_file) + ' properties and categories\n'
    file.write(string)
    string = 2*' ' + '"""\n\n'
    file.write(string)
    string = 2*' ' + '_properties = (\n'
    file.write(string)
    string = 6*' ' + '# Personal properties\n'
    file.write(string)
    
    for i in range(len(personnal_properties)):
      string = 6*' ' + "{   'id'          : '" + personnal_properties[i][0][3:] + "' \n"
      file.write(string)

      string = 6*' ' + ",   'description' : '" + personnal_properties[i][1] + "' \n"
      file.write(string)

      string = 6*' ' + ",   'type'        : '" + personnal_properties[i][2] + "' \n"
      file.write(string)

      string = 6*' ' + ",   'mode'        : '" + personnal_properties[i][3] + "' \n"
      file.write(string)

      string = 6*' ' + "}, \n"
      file.write(string)

    string = 2*' ' + ')\n'
    file.write(string)

    string = '\n\n' + 2*' ' + str("_categories = ( 'source_section', 'destination_section')") + '\n'
    file.write(string)    

    file.close()

    # get text to create a new PropertySheet in portal_classes
    file1 = open(path_name_file, 'r')
    lines_list = file1.readlines()
    text = ''
    for line in lines_list:
      text = text + line
    file1.close() 
   
    path_name_file_1 = '/var/lib/zope/Products/ERP5/PropertySheet/' + str(name_file) + '.py'
    file2 = open(path_name_file_1, 'w')
    file2.seek(0)
    file2.write(text)
    file2.close()
    
    return text

  security.declarePublic('create_Document')
  def create_Document(self, name_file = None, object_portal_type = None):
    """
    create PropertySheet in /var/lib/zope/Products/ERP5/Document/
    """
    path_name_file = os.path.join(ZOPE_INSTANCE_HOME, 'Document', str(name_file) + '.py')
    #print path_name_file
    file = open(path_name_file,'w')
    file.seek(0)

    
    string = '############################################################################# \n'
    file.write(string)
    string = '# \n'
    file.write(string)
    string = '# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved. \n'
    file.write(string)
    string = '#                         Jean-Paul Smets-Solanes <jp@nexedi.com> \n'
    file.write(string)
    string = '#                         Kevin Deldycke <kevin@nexedi.com> \n'
    file.write(string)
    string = '#                         Guy Oswald OBAMA <guy@nexedi.com> \n'
    file.write(string)
    string = '# \n'
    file.write(string)
    string = '# WARNING: This program as such is intended to be used by professional \n'
    file.write(string)
    string = '# programmers who take the whole responsability of assessing all potential \n'
    file.write(string)
    string = '# consequences resulting from its eventual inadequacies and bugs \n'
    file.write(string)
    string = '# End users who are looking for a ready-to-use solution with commercial \n'
    file.write(string)
    string = '# garantees and support are strongly adviced to contract a Free Software \n'
    file.write(string)
    string = '# Service Company \n'
    file.write(string)
    string = '# \n'
    file.write(string)
    string = '# This program is Free Software; you can redistribute it and/or \n'
    file.write(string)
    string = '# modify it under the terms of the GNU General Public License \n'
    file.write(string)
    string = '# as published by the Free Software Foundation; either version 2 \n'
    file.write(string)
    string = '# of the License, or (at your option) any later version. \n'
    file.write(string)
    string = '# \n'
    file.write(string)
    string = '# This program is distributed in the hope that it will be useful, \n'
    file.write(string)
    string = '# but WITHOUT ANY WARRANTY; without even the implied warranty of \n'
    file.write(string)
    string = '# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the \n'
    file.write(string)
    string = '# GNU General Public License for more details. \n'
    file.write(string)
    string = '# \n'
    file.write(string)
    string = '# You should have received a copy of the GNU General Public License \n'
    file.write(string)
    string = '# along with this program; if not, write to the Free Software \n'
    file.write(string)
    string = '# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. \n'
    file.write(string)
    string = '# \n'
    file.write(string)
    string = '############################################################################## \n\n\n\n'
    file.write(string)
    
    string = 'from AccessControl import ClassSecurityInfo \n\n'
    file.write(string)
    string = 'from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface \n'
    file.write(string)
    string = 'from Products.ERP5Type.Utils import assertAttributePortalType \n'
    file.write(string)
    string = 'from Products.ERP5Type.XMLObject import XMLObject \n\n'
    file.write(string)
    string = 'from Products.ERP5.Core.Node import Node \n\n'
    file.write(string)
    string = 'from Products.ERP5.Document.Entity import Entity \n\n'
    file.write(string)
    string = '#from Products.ERP5Type.Base import Base \n\n'
    file.write(string)
    string = 'class ' + str(name_file) + '(Node, XMLObject): \n'
    file.write(string)


    string = 2*' ' + '""" \n'
    file.write(string)
    string = 2*' ' + '  An ' + str(name_file) + ' object holds the information about \n'
    file.write(string)
    string = 2*' ' + '  an ' + str(name_file) + '. \n\n'
    file.write(string)

    string = 2*' ' + '  ' + str(name_file) + ' objects can contain Coordinate objects \n'
    file.write(string)
    string = 2*' ' + '  as well a documents of various types. \n'
    file.write(string)

    string = 2*' ' + '  ' + str(name_file) + ' objects can be synchronized accross multiple \n'
    file.write(string)
    string = 2*' ' + '  sites. \n'
    file.write(string)

    string = 2*' ' + '  ' + str(name_file) + ' objects inherit from the Node base class \n'
    file.write(string)
    string = 2*' ' + '  (one of the 5 base classes in the ERP5 universal business model) \n'
    file.write(string)
    string = 2*' ' + '""" \n\n\n'
    file.write(string)
    
    
    string = 2*' ' + "meta_type = 'ERP5 " + str(name_file) + "' \n"
    file.write(string)
    string = 2*' ' + "portal_type = '" + str(object_portal_type) + "' \n"
    file.write(string)
    string = 2*' ' + "add_permission = Permissions.AddPortalContent \n"
    file.write(string)
    string = 2*' ' + "isPortalContent = 1 \n"
    file.write(string)
    string = 2*' ' + "isRADContent = 1 \n\n"
    file.write(string)

    string = 2*' ' + "# Declarative security \n"
    file.write(string)
    string = 2*' ' + "security = ClassSecurityInfo() \n"
    file.write(string)
    string = 2*' ' + "security.declareObjectProtected(Permissions.View) \n\n"
    file.write(string)

    string = 2*' ' + "# Declarative properties \n"
    file.write(string)
    string = 2*' ' + "property_sheets = ( PropertySheet.Base \n"
    file.write(string)
    string = 2*' ' + "                  , PropertySheet.XMLObject \n"
    file.write(string)
    string = 2*' ' + "                  , PropertySheet.CategoryCore \n"
    file.write(string)
    string = 2*' ' + "                  , PropertySheet.DublinCore \n"
    file.write(string)
    string = 2*' ' + "                  , PropertySheet.Arrow \n"
    file.write(string)
    string = 2*' ' + "                  , PropertySheet.Task \n"
    file.write(string)
    string = 2*' ' + "                  , PropertySheet." + str(name_file) + " \n"
    file.write(string)
    string = 2*' ' + "                  ) \n\n"
    file.write(string)
    
    file.close()

    # get text to create a new Document in portal_classes    
    file1 = open(path_name_file,'r')
    lines_list = file1.readlines()
    text = ''
    for line in lines_list:
      text = text + line
    file1.close()

    path_name_file_1 = '/var/lib/zope/Products/ERP5/Document/' + str(name_file) + '.py'
    file2 = open(path_name_file_1,'w')
    file2.seek(0)
    file2.write(text)
    file2.close()    
        
    return text

InitializeClass(Getter_Setter)
allow_class(Getter_Setter)  


        
