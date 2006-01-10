##############################################################################
#
# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved.
#                         Jean-Paul Smets-Solanes <jp@nexedi.com>
#                         Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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

from Products.ERP5.Core.Node import Node
from Products.ERP5.Document.Entity import Entity

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Utils import assertAttributePortalType
from Products.ERP5Type.XMLObject import XMLObject



class Person(Entity, Node, XMLObject):
    """
      An Person object holds the information about
      an person (ex. you, me, someone in the company,
      someone outside of the company, a member of the portal,
      etc.).

      Person objects can contain Coordinate objects
      (ex. Telephone, Url) as well a documents of various types.

      Person objects can be synchronized accross multiple
      sites.

      Person objects inherit from the Node base class
      (one of the 5 base classes in the ERP5 universal business model)
    """

    meta_type = 'ERP5 Person'
    portal_type = 'Person'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Reference
                      , PropertySheet.Person
                      , PropertySheet.Mapping
                      )

    def _setTitle(self, value):
      """
        Here we see that we must define a notion
        of priority in the way fields are updated
      """
      if value != self.getTitle():
        self.title = value

    security.declareProtected(Permissions.View, 'getTitle')
    def getTitle(self, **kw):
      """
        Returns the title if it exists or a combination of
        first name and last name
      """
      if self.title == '':
        name_list = []
        if self.getFirstName() not in (None, ''):
          name_list.append(self.getFirstName())
        if self.getMiddleName() not in (None, ''):
          name_list.append(self.getMiddleName())
        if self.getLastName() not in (None, ''):
          name_list.append(self.getLastName())
        return ' '.join(name_list)
      else:
        return self.title
    Title = getTitle

    security.declareProtected(Permissions.ModifyPortalContent, 'setTitle')
    def setTitle(self, value):
      """
        Updates the title if necessary
      """
      self._setTitle(value)
      self.reindexObject()

    def _setFirstName(self, value):
      """
        Update Title if first_name is modified
      """
      self.first_name = value
      if self.getFirstName()!=None and self.getLastName()!=None:
        self._setTitle(self.getFirstName()+' '+self.getLastName())

    security.declareProtected(Permissions.ModifyPortalContent, 'setFirstName')
    def setFirstName(self, value):
      """
        Updates the first_name if necessary
      """
      self._setFirstName(value)
      self.reindexObject()

    def _setLastName(self, value):
      """
        Update Title if last_name is modified
      """
      self.last_name = value
      if self.getFirstName()!=None and self.getLastName()!=None:
        self._setTitle(self.getFirstName()+' '+self.getLastName())

    security.declareProtected(Permissions.ModifyPortalContent, 'setLastName')
    def setLastName(self, value):
      """
        Updates the last_name if necessary
      """
      self._setLastName(value)
      self.reindexObject()
