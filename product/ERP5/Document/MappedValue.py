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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Utils import UpperCase

from Products.ERP5.Document.Domain import Domain
from Products.ERP5.Document.Amount import Amount

from zLOG import LOG

class MappedValue(Domain, Amount):
  """
    A MappedValue allows to associate a value to a domain

    Although MappedValue are supposed to be independent of any
    design choice, we have to implement them as subclasses of
    Amount in order to make sure they provide a complete
    variation interface. In particular, we want to be able
    to call getVariationValue / setVariationValue on a
    MappedValue.

    XXX - Amount should be remove from here
  """
  meta_type = 'ERP5 Mapped Value'
  portal_type = 'Mapped Value'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative interfaces
  __implements__ = ( Interface.Predicate, Interface.Variated,)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.Predicate
                      , PropertySheet.Domain
                      , PropertySheet.MappedValue
                    )

  # Factory Type Information
  factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
A bank account number holds a collection of numbers
and codes (ex. SWIFT, RIB, etc.) which may be used to
identify a bank account."""
         , 'icon'           : 'transformed_resource_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addMappedValue'
         , 'immediate_view' : 'mapped_value_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'mapped_value_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'mapped_value_print'
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

  security.declarePrivate( '_edit' )
  def _edit(self, REQUEST=None, force_update = 0, **kw):
    # We must first prepare the mapped value before we do the edit
    if kw.has_key('mapped_value_property_list'):
      self._setProperty('mapped_value_property_list', kw['mapped_value_property_list'])
    if kw.has_key('default_mapped_value_property'):
      self._setProperty('default_mapped_value_property', kw['default_mapped_value_property'])
    if kw.has_key('mapped_value_property'):
      self._setProperty('mapped_value_property', kw['mapped_value_property'])
    if kw.has_key('mapped_value_property_set'):
      self._setProperty('mapped_value_property_set', kw['mapped_value_property_set'])
    Domain._edit(self, REQUEST=REQUEST, force_update = force_update, **kw)

  security.declareProtected( Permissions.AccessContentsInformation, 'getProperty' )
  def getProperty(self, key, d=None):
    """
      Generic accessor. First we check if the value
      exists. Else we call the real accessor
    """
    #try:
    if 1:
      # If mapped_value_property_list is not set
      # then it creates an exception
      if key in self.getMappedValuePropertyList([]):
        if hasattr(self, key):
          return getattr(self, key)
    #except:
    #  LOG("WARNING: ERP5", 0, 'Could not access mapped value property %s' % key)
    #  return None
    # Standard accessor
    try:
      result = Domain.getProperty(self, key, d=d)
    except:
      result = None
    return result

  security.declareProtected( Permissions.ModifyPortalContent, '_setProperty' )
  def _setProperty(self, key, value, type='string'):
    """
      Generic accessor. Calls the real accessor
    """
    #try:
    if 1:
      # If mapped_value_attribute_list is not set
      # then it creates an exception
      if key in self.getMappedValuePropertyList([]):
        return setattr(self, key, value)
    #except:
    #  LOG("WARNING: ERP5", 0, 'Could not set mapped value property %s' % key)
    #  return
    accessor_name = 'set' + UpperCase(key)
    method = getattr(self, accessor_name)
    return method(value)

  # Compatibility method
  def getMappedValuePropertyList(self, *args):
    """
      Return property list managed by this mapped value
      Coramy Compatibility Layer - XXX not for Standard Version
    """
    if hasattr(self, 'mapped_value_attribute_list'):
      # Update Attribute - Coramy Compatibility
      self._baseSetMappedValuePropertyList(self.mapped_value_attribute_list)
      delattr (self, 'mapped_value_attribute_list')
    return self._baseGetMappedValuePropertyList(*args)
