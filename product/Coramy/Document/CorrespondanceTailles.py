##############################################################################
#
# Copyright (c) 2002 Coramy SAS and Contributors. All Rights Reserved.
#                    Thierry_Faucher <Thierry_Faucher@coramy.com>
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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.Domain import Domain

from zLOG import LOG

class CorrespondanceTailles(XMLObject, XMLMatrix):
    """
      A matrix which provides taille_client
      for a given taille Coramy
    """

    meta_type = 'CORAMY Correspondance Tailles'
    portal_type = 'Correspondance Tailles'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.VariationRange
                      , PropertySheet.CorrespondanceTailles
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
une grille de correspondance de tailles..."""
         , 'icon'           : 'correspondance_tailles_icon.gif'
         , 'product'        : 'Coramy'
         , 'factory'        : 'addCorrespondanceTailles'
         , 'immediate_view' : 'correspondance_tailles_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Set Mapped Value',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'correspondance_tailles_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'list'
          , 'name'          : 'Object Contents'
          , 'category'      : 'object_action'
          , 'action'        : 'folder_contents'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'correspondance_tailles_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

    security.declareProtected(Permissions.ModifyPortalContent, '_setMatrixCellRange')
    def _setMatrixCellRange(self):
      line = self.getCategoryMembershipList('morpho_type',base=0)
      if len(line) == 0 :
        line = [None]
      column = self.getCategoryMembershipList('taille',base=0)
      if len(column) == 0 :
        column = [None]
      self._setCellRange(line, column, base_id='taille_client')
      # Empty cells if no variation
      if line == [[None]] and column == [[None]]:
        self.delCells(base_id='taille_client')
      # And fix it in case the cells are not renamed (XXX this will be removed in the future)
      self._checkConsistency(fixit=1)

    security.declareProtected(Permissions.ModifyPortalContent, 'setMatrixCellRange')
    def setMatrixCellRange(self):
      """
        Defines the possible variations which taille_client value
        variate on and reindex the object
      """
      self._setMatrixCellRange()
      self.reindexObject()

    # Methods for matrix UI widgets
    security.declareProtected(Permissions.AccessContentsInformation, 'getLineItemList')
    def getLineItemList(self):
      clist = self.getCategoryMembershipList('morpho_type',base=0)
      if len(clist) == 0 :
        clist = [None]
      result = []
      for c in clist:
        result += [(c,c)]
      return result

    security.declareProtected(Permissions.ModifyPortalContent, '_setTailleList')
    def _setTailleList(self,value):
      self._categorySetTailleList(value)
      self._setMatrixCellRange()

    security.declareProtected(Permissions.ModifyPortalContent, '_setMorphoTypeList')
    def _setMorphoTypeList(self,value):
      self._categorySetMorphoTypeList(value)
      self._setMatrixCellRange()

    def _setTitle(self, value):
      """
        Here we see that we must define an notion
        of priority in the way fields are updated
      """
      if value != self.getTitle():
        self.title = value

    security.declareProtected(Permissions.View, 'getTitle')
    def getTitle(self):
      """
        Returns the title if it exists or a combination of
        first name and last name
      """
      if self.title == '':
        return self.getId()
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

    # Inheritance solving
    security.declareProtected(Permissions.ModifyPortalContent, 'checkConsistency')
    checkConsistency = XMLMatrix.checkConsistency

    security.declarePrivate('_checkConsistency')
    def _checkConsistency(self, fixit=0):
      """
        Check the constitency of transformation elements
      """
      error_list = XMLMatrix._checkConsistency(self, fixit=fixit)

      # First quantity
      # We build an attribute equality and look at all cells
      constraint = Constraint.AttributeEquality(
        domain_base_category_list = ('taille', 'morpho_type',),
        predicate_operator = 'SUPERSET_OF',
        mapped_value_property_list = ['taille_client'] )
      for k in self.getCellKeys(base_id = 'taille_client'):
        kw={}
        kw['base_id'] = 'taille_client'
        c = self.getCell(*k, **kw)
        if c is not None:
          predicate_value = []
          for p in k:
            if p is not None: predicate_value += [p]
          constraint.edit(predicate_value_list = predicate_value)
          if fixit:
            error_list += constraint.fixConsistency(c)
          else:
            error_list += constraint.checkConsistency(c)

      return error_list

