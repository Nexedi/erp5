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

class PatchedCPSDocument(CPSDocument):

  security = ClassSecurityInfo()

  def _propertyMap(self):
    """
      Returns fake property sheet
    """
    property_sheet = []
    for schema in self.getTypeInfo().getSchemas():
      for field in schema.objectValues():
        #LOG('testjp',0,'field: %s' % str(field))
        f_type = None
        for p in field._properties:
          if p['id'] == 'default':
            f_type = p['type']
        if isinstance(field,CPSImageField):
          f_type = 'object'
        elif isinstance(field,CPSStringField):
          f_type = 'string'
        elif isinstance(field,CPSDateTimeField):
          f_type = 'date'
        elif isinstance(field,CPSFileField):
          f_type = 'object'
        elif isinstance(field,CPSDocument):
          pass
        prop_id = schema.getIdUnprefixed(field.id)
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
    accessor_name = 'get' + UpperCase(key)
    aq_self = aq_base(self)
    if key!='content':
      if hasattr(aq_self, accessor_name):
        method = getattr(self, accessor_name)
        return method()
    prop_type = self.getPropertyType(key) # XXX added by Seb
    if prop_type in ('object',):
      if hasattr(aq_self, key):
        value = getattr(aq_self, key)
        value = aq_base(value)
        return value
      return None
    elif hasattr(aq_self, key):
      value = getattr(aq_self, key)
      if callable(value): value = value()
      return value

CPSDocument.getProperty = PatchedCPSDocument.getProperty
CPSDocument._propertyMap = PatchedCPSDocument._propertyMap
CPSDocument.setProperty = Base.setProperty
CPSDocument._setProperty = Base._setProperty
CPSDocument.asXML = Base.asXML
CPSDocument._edit = Base._edit
