##############################################################################
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


from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import _dtmldir
from Products.ERP5Type import PropertySheet, Permissions
from Products.ERP5Type.Utils import convertToUpperCase

from Core.Folder import Folder
from zLOG import LOG

class XMLObject( Folder ):
    """
        This is the base class for all ERP5 Zope objects.
        It defines object attributes which are necessary to implement
        relations and data synchronisation

        id  --  the standard object id
        rid --  the standard object id in the master ODB the object was
                subsribed from
        uid --  a global object id which is unique to each ZODB
        sid --  the id of the subscribtion/syncrhonisation object which
                this object was generated from

        The XMLObject acts as a folder as soon as an object is added to it.
        This allows to save memory by creating the BTree only if needed.
    """
    meta_type = 'ERP5 XML Object'
    portal_type = 'XML Object'
    isPortalContent = 1
    isRADContent = 1

    # The only declarative factory_type_information in ERP5
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : "ERP5 default document. Supports synchronisation and XML."
         , 'icon'           : 'document_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addXMLObject'
         , 'immediate_view' : 'XMLObject_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'XMLObject_view'
          , 'permissions'   : ( Permissions.View, )
          },
        )
      }

    # Declarative security
    security = ClassSecurityInfo()

    # Declarative properties
    property_sheets = ( PropertySheet.XMLObject, )

    # Inheritance fixes
    security.declareProtected( Permissions.ModifyPortalContent, 'setDescription' )
    def setDescription(self, value):
      """
          Sets the description by invoking the Accessor
          based method rather than the one inherited from CMF.
          This is require to make sure that value is casted
      """
      self._setDescription(value)
      self.reindexObject()

    security.declareProtected( Permissions.ModifyPortalContent, 'XUpdateDocument' )
    def XUpdateDocument(self, xupdate):
      """
          Update a document by providing an xupdate XML file
      """
      pass


    security.declareProtected( Permissions.ModifyPortalContent, 'fromXML' )
    def fromXML(self, xml):
      """
          Replace the content of this object by providing an xml content
      """
      from Products.ERP5SyncML.Conduit.ERP5Conduit import ERP5Conduit
      conduit = ERP5Conduit()
      conduit.addNode(object=self, xml=xml)

    # Hash method
    def __hash__(self):
      return hash(self.getUid())


InitializeClass(XMLObject)
