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
from Products.ERP5Type.Base import Base

class PatchedCPSDocument(CPSDocument):

    def _propertyMap(self):
      """
        Returns fake property sheet
      """
      property_sheet = []
      for schema in self.getTypeInfo().getSchemas():
        for field in schema.objectValues():
          #LOG('testjp',0,'field: %s' % str(field))
          f_type = ''
          for p in field._properties:
            if p['id'] == 'default':
              f_type = p['type']
          if isinstance(field,CPSImageField):
            #f_type = 'image'
            f_type = 'pickle'
          if isinstance(field,CPSDateTimeField):
            f_type = 'date'
          if isinstance(field,CPSFileField):
            #f_type = 'file'
            f_type = 'pickle'
          if isinstance(field,CPSDocument):
            #f_type = 'document'
            f_type = 'pickle'
          prop_id = schema.getIdUnprefixed(field.id)
          if prop_id in ('file_text','content','attachedFile',
                                 'attachedFile_html','attachedFile_text', 'content'):
            f_type = 'pickle' # this should be string, but this strings
                              # do so bad xml
          #if not (prop_id in ('file_text','content','attachedFile','attachedFile_html','attachedFile_text')):
          #if not (prop_id in ('content',)):
          if 1:
            property_sheet.append(
              {
                'id'    :   prop_id,
                'type'  :   f_type
              }
              )
      return tuple(property_sheet + list(getattr(self, '_local_properties', ())))

CPSDocument._propertyMap = PatchedCPSDocument._propertyMap
CPSDocument.getProperty = Base.getProperty
CPSDocument.setProperty = Base.setProperty
