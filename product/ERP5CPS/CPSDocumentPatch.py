# (C) Copyright 2004 Nexedi SARL <http://nexedi.com>
# Authors: Sebastien Robin <seb@nexedi.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#

from Products.CPSDocument.CPSDocument import CPSDocument
from Products.CPSSchemas.BasicFields import CPSImageField, CPSFileField, CPSDateTimeField
from Products.CPSSchemas.BasicFields import CPSStringField
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Utils import UpperCase
from Acquisition import aq_base, aq_inner
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import View
from zLOG import LOG

class PatchedCPSDocument(CPSDocument):

  security = ClassSecurityInfo()

  security.declareProtected( View, '_propertyMap' )
  def _propertyMap(self):
    """
      Returns fake property sheet
    """
    property_sheet = []
    property_sheet.append(
      {
        'id'    :   'layout_and_schema',
        'type'  :   'object'
      }
      )
    field_list = self.getTypeInfo().getDataModel(self)._fields.items()
    field_list.sort()
    for (prop_id,field) in field_list:
      #for field in schema.objectValues():
      #LOG('testjp',0,'field: %s' % str(field))
      f_type = None
      #for p in field._properties:
      #  if p['id'] == 'default':
      #    f_type = p['type']
      if isinstance(field,CPSImageField):
        f_type = 'object'
      elif isinstance(field,CPSStringField):
        f_type = 'string'
      elif isinstance(field,CPSDateTimeField):
        f_type = 'string'
      elif isinstance(field,CPSFileField):
        f_type = 'object'
      elif isinstance(field,CPSDocument):
        pass
      #prop_id = schema.getIdUnprefixed(field.id)
      #if prop_id in ('file_text','content','attachedFile',
      #                      'attachedFile_html','attachedFile_text', 'content'):
      #  f_type = 'object' # this should be string, but this strings
                          # do so bad xml
      #if not (prop_id in ('file_text','content','attachedFile','attachedFile_html','attachedFile_text')):
      #if not (prop_id in ('content',)):
      if f_type is not None:
        property_sheet.append(
          {
            'id'    :   prop_id,
            'type'  :   f_type
          }
          )
    return tuple(property_sheet + list(getattr(self, '_local_properties', ())))


  security.declareProtected( View, 'getProperty' )
  def getProperty(self, key, d=None):
    """
      Previous Name: getValue

      Generic accessor. Calls the real accessor
    """
    data_model = self.getTypeInfo().getDataModel(self)
    accessor_name = 'get' + UpperCase(key)
    base = aq_base(self)
    if data_model.has_key(key):
      return data_model.get(key)
    elif hasattr(base,accessor_name):
      method = getattr(base,accessor_name)
      return method()
    return None

  security.declarePrivate('getLayoutAndSchema' )
  def getLayoutAndSchema(self):
    return (aq_base(self._getOb(".cps_layouts")),aq_base(self._getOb(".cps_schemas")))

  security.declarePrivate('setLayoutAndSchema' )
  def setLayoutAndSchema(self, data):
    """
    data must be : (layout,schema)
    """
    self._setOb(".cps_layouts",data[0])
    self._setOb(".cps_schemas",data[1])

  security.declarePrivate('_setProperty' )
  def _setProperty(self, key, value, type='string'):
    """
      Set the property for cps objects
    """
    LOG('PatchCPSDoc._setProperty',0,'key: %s, value: %s' % (repr(key),repr(value)))
    data_model = self.getTypeInfo().getDataModel(self)
    #data_model.set(key,value)
    type_info = self.getTypeInfo()
    kw = {key:value}
    type_info.editObject(self,kw)

  security.declarePrivate('edit' )
  def edit(self, REQUEST=None, force_update = 0, reindex_object = 0, **kw):
    return self._edit(REQUEST=REQUEST, force_update=force_update, reindex_object=reindex_object, **kw)


  # Object attributes update method
  security.declarePrivate( '_edit' )
  def _edit(self, REQUEST=None, force_update = 0, reindex_object = 0, **kw):
    """
      Generic edit Method for all ERP5 object
      The purpose of this method is to update attributed, eventually do
      some kind of type checking according to the property sheet and index
      the object.
  
      Each time attributes of an object are updated, they should
      be updated through this generic edit method
    """
    LOG('PatchCPSDoc._edit, kw: ',0,kw)
    try:
      categoryIds = self._getCategoryTool().getBaseCategoryIds()
    except:
      categoryIds = []
    if kw.has_key('layout_and_schema'):
      self.setLayoutAndSchema(kw['layout_and_schema'])
    for key in kw.keys():
      #if key in categoryIds:
      #  self._setCategoryMembership(key, kw[key])
      if key != 'id' and key!= 'layout_and_schema':
        # We only change if the value is different
        # This may be very long.... 
        self._setProperty(key, kw[key])


CPSDocument.getProperty = PatchedCPSDocument.getProperty
CPSDocument.getLayoutAndSchema = PatchedCPSDocument.getLayoutAndSchema
CPSDocument.setLayoutAndSchema = PatchedCPSDocument.setLayoutAndSchema
CPSDocument._propertyMap = PatchedCPSDocument._propertyMap
CPSDocument.setProperty = Base.setProperty
CPSDocument._setProperty = PatchedCPSDocument._setProperty
CPSDocument.asXML = Base.asXML
CPSDocument._edit = PatchedCPSDocument._edit
CPSDocument.edit = PatchedCPSDocument._edit
