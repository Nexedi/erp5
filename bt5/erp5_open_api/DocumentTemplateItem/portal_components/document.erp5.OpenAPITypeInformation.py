##############################################################################
#
# Copyright (c) 2023 Nexedi SA and Contributors. All Rights Reserved.
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

import json
import io
import warnings

from Persistence.mapping import PersistentMapping
import six
from ZTUtils import make_query

from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5Type.XMLMatrix import XMLMatrix
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet


class OpenAPITypeInformationCell:
  __allow_access_to_unprotected_subobjects__ = True

  def __init__(self, context, key, method_id):
    self.context = context
    self.key = key
    self.method_id = method_id

  def edit(self, method_id=None, *args, **kw):
    print('edit', self.context, self.key, method_id, args, kw)
    self.context.setMethodIdForOperation(self.key[0], self.key[1], method_id)

  def getProperty(self, prop):
    if prop == 'method_id':
      return self.method_id

  def getMethodId(self):
    return 'ohoh'


class OpenAPITypeInformationMethodMapping:
  __allow_access_to_unprotected_subobjects__ = True

  def __init__(
      self, context, request_path, http_method, operation_id, method_id,
      method):
    self.context = context
    self.request_path = request_path
    self.http_method = http_method
    self.operation_id = operation_id
    self.method_id = method_id
    self.method = method
    self.uid = 'new_'

  def getUid(self):
    return self.uid

  def getObject(self):
    return self

  def getPhysicalPath(self):
    if self.method is not None:
      return self.method.getPhysicalPath()
    return self.context.getPhysicalPath()

  def getListItemUrl(self, cname_id, selection_index, selection_name):
    if self.method is None:
      return None
    return '{}/view?{}'.format(
      self.method.absolute_url(),
      make_query(
        selection_index=selection_index, selection_name=selection_name))


class OpenAPITypeInformation(ERP5TypeInformation, XMLMatrix):
  """
  """
  portal_type = 'Open API Type'
  meta_type = 'ERP5 Open API Type'

  # Default Properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.Data,
    PropertySheet.TextDocument,
  )

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def __init__(self, *args, **kw):
    super(OpenAPITypeInformation, self).__init__(*args, **kw)
    self._method_id_mapping = PersistentMapping()

  def getSchema(self):
    stream = io.BytesIO(self.getTextContent() or b'{}')
    try:
      import yaml # pylint:disable=import-error
    except ImportError:
      warnings.warn(ImportWarning, "yaml not available, only json is supported")
      return json.load(stream)
    return yaml.load(stream, yaml.SafeLoader)

  def asCellRange(self, base_id='method_mapping', matrixbox=True):
    """returns the cell range for matrixbox
    """
    def iter_operations():
      schema = self.getSchema()
      for path, path_item in six.iteritems(schema.get('paths', {})):
        for http_method, operation in six.iteritems(path_item):
          yield path, http_method, operation.get('operationId')

    def format_operation(path, http_method, operation_id):
      formatted = '{http_method} {path}'.format(
        http_method=http_method.upper(), path=path)
      if operation_id:
        formatted += ' ({operation_id})'.format(operation_id=operation_id)
      return formatted

    operation_list = list(iter_operations())
    if matrixbox:
      return [[(m, format_operation(*m)) for m in operation_list]]
    return [[operation_list]]

  def getCellRange(self, base_id='method_mapping'):
    """returns the cell range
    """
    return self.asCellRange(base_id=base_id, matrixbox=False)

  def newCell(self, *coords, **kw):
    method_id = self.getMethodIdForOperation(coords[0][0], coords[0][1], None)
    return OpenAPITypeInformationCell(self, coords[0], method_id)

  getCell = newCell

  def hasInRange(self, *coords, **kw):
    return kw['base_id'] == 'method_mapping'

  def setMethodIdForOperation(self, path, http_method, method_id):
    self._method_id_mapping[path, http_method] = method_id

  def getMethodIdForOperation(self, path, http_method, operation_id, context=None):
    # TODO simplify this
    mapped_method_id = self._method_id_mapping.get((path, http_method), None)
    if mapped_method_id:
      return mapped_method_id

    if operation_id:
      if context is None:
        context = self.getPortalObject().newContent(
          portal_type=self.getId(), temp_object=True)
      method = context._getTypeBasedMethod(operation_id)
      print(operation_id, 'tbm method', method)
      if hasattr(method, 'getId'):
        return method.getId()

  def getMethodMappingValueList(self, *args, **kw):
    method_mapping_value_list = []
    context = self.getPortalObject().newContent(
      portal_type=self.getId(), temp_object=True)

    schema = self.getSchema()
    for path, path_item in six.iteritems(schema.get('paths', {})):
      for http_method, operation in six.iteritems(path_item):
        __traceback_info__ = path, http_method, operation
        if http_method in (
            "description",
            "servers",
            "summary",
        ):
          continue
        if http_method == '$ref':
          raise NotImplementedError()
        if http_method == "parameters":
          # WARNING #"parameters",
          continue

        operation_id = operation.get('operationId')
        method_id = None
        if operation_id:
          method = context._getTypeBasedMethod(operation_id)
          if hasattr(method, 'getId'):
            method_id = method.getId()

        method_mapping_value_list.append(
          OpenAPITypeInformationMethodMapping(
            self,
            path,
            http_method.upper(),
            operation.get('operationId'),
            method_id,
            method,
          ))

    return method_mapping_value_list
