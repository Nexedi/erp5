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
from Products.CMFCore.WorkflowCore import WorkflowAction

from Products.CMFPhoto.CMFPhoto import CMFPhoto

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.Domain import Domain
from Products.ERP5.Document.Image import Image

from zLOG import LOG

class CorrespondanceMesures(XMLObject, XMLMatrix, Image):
    """
      A matrix which provides default mesure_code and mesure_name
    """
    meta_type = 'CORAMY Correspondance Mesures'
    portal_type = 'Correspondance Mesures'
    add_permission = Permissions.AddERP5Content
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
                      , PropertySheet.CorrespondanceMesures
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
une grille de correspondance de tailles..."""
         , 'icon'           : 'correspondance_mesures_icon.gif'
         , 'product'        : 'Coramy'
         , 'factory'        : 'addCorrespondanceMesures'
         , 'immediate_view' : 'correspondance_mesures_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Set Mapped Value',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'correspondance_mesures_view'
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
          , 'action'        : 'correspondance_mesures_print'
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

    def __init__(self, id, **kw):
      Image.__init__(self, id, **kw)
      XMLObject.__init__(self, id, **kw)

    # Inheritance
    _edit = Image._edit
    security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
    edit = WorkflowAction( _edit )

    security.declareProtected('View', 'index_html')
    index_html = Image.index_html

    security.declareProtected('AccessContentsInformation', 'content_type')
    content_type = Image.content_type

    def manage_afterClone(self, item):
      XMLObject.manage_afterClone(self, item)
      CMFPhoto.manage_afterClone(self, item)

    def manage_afterAdd(self, item, container):
      XMLObject.manage_afterAdd(self, item, container)
      CMFPhoto.manage_afterAdd(self, item, container)

    def manage_beforeDelete(self, item, container):
      CMFPhoto.manage_beforeDelete(self, item, container)

    # Main methods
    security.declareProtected(Permissions.ModifyPortalContent, '_setMatrixCellRange')
    def _setMatrixCellRange(self):
      line = self.getCategoryMembershipList('mesure_vetement',base=0)
      if len(line) == 0 :
        line = [None]
      column = self.getCategoryMembershipList('reference_mesure',base=0)
      if len(column) == 0 :
        column = [None]
      self._setCellRange(line, column, base_id='mesure_client')
      # Empty cells if no variation
      if line == [[None]] and column == [[None]]:
        self.delCells(base_id='mesure_client')
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

    security.declareProtected(Permissions.ModifyPortalContent, '_setReferenceMesureList')
    def _setReferenceMesureList(self,value):
      self._categorySetReferenceMesureList(value)
      self._setMatrixCellRange()

    security.declareProtected(Permissions.ModifyPortalContent, '_setMesureVetementList')
    def _setMesureVetementList(self,value):
      self._categorySetMesureVetementList(value)
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
        domain_base_category_list = ('reference_mesure', 'mesure_vetement',),
        predicate_operator = 'SUPERSET_OF',
        mapped_value_property_list = ['mesure_client'] )
      for k in self.getCellKeys(base_id = 'mesure_client'):
        kw={}
        kw['base_id'] = 'mesure_client'
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

