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
from Products.ERP5Type.Core.Predicate import Predicate
from Products.ERP5Type.Utils import UpperCase
from decimal import Decimal
from erp5.component.tool.RoundingTool import ROUNDING_OPTION_DICT
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
                     PropertySheet.DecimalOption,
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
        if scale > 0 or (scale==0 and precision>=1):
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
    if not isinstance(document, RoundingProxy):
      document = RoundingProxy(document.asContext())
    document._applyRoundingModel(self)
    return document


# Use the Extension Class only because it is necessary to allow an instance
# of this class to be wrapped in an acquisition wrapper.
class RoundingProxy(ExtensionClass.Base):

  def __init__(self, ob):
    super(RoundingProxy, self).__init__()
    self._ob = ob
    self._rounded_value_set = set()
    self._rounding_model_dict = {}

  def __getattr__(self, name):
    # do not do 'self._ob' to avoid acquisition wrapping
    return getattr(self.__dict__['_ob'], name)

  def _applyRoundingModel(self, rounding_model):
    document = self.__dict__['_ob']
    roundValue = rounding_model.roundValue
    def decorate(original_getter):
      return lambda *args, **kw: roundValue(original_getter(*args, **kw))
    for property_id in rounding_model.getRoundedPropertyIdList():
      assert property_id not in self._rounding_model_dict
      self._rounding_model_dict[property_id] = rounding_model
      getter_name = 'get%s' % UpperCase(property_id)
      getter = getattr(document, getter_name, None)
      setter_name = '_set%s' % UpperCase(property_id)
      setter = getattr(document, setter_name, None)
      if setter is not None:
        # round the property value itself
        setter(roundValue(getter()))
        # tell getProperty not to round it again
        self._rounded_value_set.add(property_id)
      elif getter is not None:
        # cannot round the property value now so do it dynamically
        setattr(self, getter_name, decorate(getter))

  def getRoundingModelPrecision(self, property_id):
    """
    Return precision value of rounding model. This is useful for
    float field.
    """
    rounding_model = self._rounding_model_dict.get(property_id)
    if rounding_model is not None:
      return rounding_model.getPrecision()

  def getProperty(self, key, *args, **kw):
    result = self.__dict__['_ob'].getProperty(key, *args, **kw)
    if key not in self._rounded_value_set:
      rounding_model = self._rounding_model_dict.get(key)
      if rounding_model is not None:
        return rounding_model.roundValue(result)
    return result

  def getObject(self, *args, **kw):
    return self
