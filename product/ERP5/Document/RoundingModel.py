##############################################################################
#
# Copyright (c) 2009 Nexedi KK and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA
# 02110-1301, USA.
#
##############################################################################
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import PropertySheet, Permissions
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5Type.Utils import UpperCase
from decimal import Decimal
from Products.ERP5.Tool.RoundingTool import ROUNDING_OPTION_DICT
import ExtensionClass
from math import log

class RoundingModel(Predicate):
  """
  A Rounding Model class which defines rounding rule.
  """
  meta_type = 'ERP5 Rounding Model'
  portal_type = 'Rounding Model'
  add_permission = Permissions.AddPortalContent

  security = ClassSecurityInfo()

  property_sheets = (PropertySheet.Base,
                     PropertySheet.SimpleItem,
                     PropertySheet.XMLObject,
                     PropertySheet.CategoryCore,
                     PropertySheet.DublinCore,
                     PropertySheet.Predicate,
                     PropertySheet.SortIndex,
                     PropertySheet.Reference,
                     PropertySheet.RoundingModel,
                     )

  security.declareProtected(Permissions.AccessContentsInformation, 'roundValue')
  def roundValue(self, value):
    if not value:
      return value

    rounding_method_id = self.getRoundingMethodId()
    if rounding_method_id is not None:
      rounding_method = getattr(self, rounding_method_id, None)
      if rounding_method is None:
        raise ValueError('Rounding method (%s) was not found.' \
                % (rounding_method_id,))
    else:
      decimal_rounding_option = self.getDecimalRoundingOption()
      if decimal_rounding_option not in ROUNDING_OPTION_DICT:
        raise ValueError('Decimal rounding option must be selected.')

      def rounding_method(value, precision):
        if precision is None:
          precision = 1

        scale = int(log(precision, 10))
        if scale > 0:
          value = Decimal(str(value))
          scale = Decimal(str(int(precision))).quantize(value)
          precision = Decimal('1')
          value /= scale
          value = value.quantize(precision, rounding=decimal_rounding_option)
          value *= scale
          result = float(value.quantize(precision))
        else:
          result = float(
            Decimal(str(value)).quantize(Decimal(str(precision)),
                                         rounding=decimal_rounding_option))
        return result

    return rounding_method(value, self.getPrecision())

  security.declareProtected(Permissions.AccessContentsInformation, 'getRoundingProxy')
  def getRoundingProxy(self, document):
    """
    Return a rounding proxy object which getter methods returns rounded
    value by following the rounding model definition.
    """
    rounding_model = self
    rounded_property_getter_method_name_list = []
    rounded_property_special_property_name_list = []

    if isinstance(document, RoundingProxy):
      temp_document = document._getOriginalDocument()
      original_document = document
    else:
      temp_document = document.asContext()
      original_document = temp_document

    for property_id in rounding_model.getRoundedPropertyIdList():
      getter_name = 'get%s' % UpperCase(property_id)
      getter = getattr(temp_document, getter_name, None)
      setter_name = 'set%s' % UpperCase(property_id)
      setter = getattr(temp_document, setter_name, None)

      if getter is not None and setter is not None:
        # round the property value itself
        setter(self.roundValue(getter()))
      else:
        # cannot round the property value so that the return value of getter
        # will be rounded
        rounded_property_getter_method_name_list.append(getter_name)
        if getter is not None and setter is None:
          rounded_property_special_property_name_list.append(property_id)

    class _RoundingProxy(RoundingProxy):

      def _getOriginalDocument(self):
        if isinstance(original_document, RoundingProxy):
          return original_document._getOriginalDocument()
        else:
          return original_document

      def getRoundingModelPrecision(self, property_id):
        """
        Return precision value of rounding model. This is useful for
        float field.
        """
        if property_id in rounding_model.getRoundedPropertyIdList():
          return rounding_model.getPrecision()
        elif isinstance(original_document, RoundingProxy):
          return original_document.getRoundingModelPrecision(property_id)
        else:
          return None

      def getProperty(self, key, *args, **kw):
        result = original_document.getProperty(key, *args, **kw)
        if key in rounded_property_special_property_name_list:
          return rounding_model.roundValue(result)
        else:
          return result

      # XXX not sure why but getObject may return original_document
      # unless it is overridden here.
      def getObject(self, *args, **kw):
        return self

      def __getattr__(self, name):
        attribute = getattr(original_document, name)
        if getattr(attribute, 'DUMMY_ROUNDING_METHOD_MARK', None) is DUMMY_ROUNDING_METHOD_MARK:
          return attribute
        if name in rounded_property_getter_method_name_list:
          def dummyMethod(*args, **kw):
            return rounding_model.roundValue(attribute(*args, **kw))
          dummyMethod.DUMMY_ROUNDING_METHOD_MARK = DUMMY_ROUNDING_METHOD_MARK
          return dummyMethod
        else:
          return attribute
    return _RoundingProxy()

DUMMY_ROUNDING_METHOD_MARK = object()

# Use the Extension Class only because it is necessary to allow an instance
# of this class to be wrapped in an acquisition wrapper.
class RoundingProxy(ExtensionClass.Base):
  """Super class of _RoundingProxy class defined above. Use this class for
  isinstance method to check if object is a real instance or a rounding proxy
  instance.
  """
