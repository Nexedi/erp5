# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (c) 2009 Nexedi KK and Contributors. All Rights Reserved.
#                    Yusei TAHARA <yusei@nexedi.com>
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
import six
import functools
import zope.interface
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from erp5.component.interface.IRoundingTool import IRoundingTool
from decimal import (Decimal, ROUND_DOWN, ROUND_UP, ROUND_CEILING, ROUND_FLOOR,
                     ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP)

ROUNDING_OPTION_DICT = {'ROUND_DOWN':ROUND_DOWN,
                        'ROUND_UP':ROUND_UP,
                        'ROUND_CEILING':ROUND_CEILING,
                        'ROUND_FLOOR':ROUND_FLOOR,
                        'ROUND_HALF_DOWN':ROUND_HALF_DOWN,
                        'ROUND_HALF_EVEN':ROUND_HALF_EVEN,
                        'ROUND_HALF_UP':ROUND_HALF_UP}

def round_(value, ndigits=None, decimal_rounding_option='ROUND_HALF_EVEN'):
  if ndigits is None:
    precision = 1
  else:
    assert isinstance(ndigits, int), 'ndigits should be int.'
    precision = 10 ** -ndigits
  if precision >= 1:
    value = Decimal(value)
    value /= precision
    value = value.quantize(precision, rounding=decimal_rounding_option)
    value *= precision
    result = float(value.quantize(precision))
  else:
    result = float(
      Decimal(value).quantize(Decimal(str(precision)),
                                   rounding=decimal_rounding_option))
  return result


round_down = functools.partial(round_, decimal_rounding_option=ROUND_DOWN)
round_up = functools.partial(round_, decimal_rounding_option=ROUND_UP)
round_ceiling = functools.partial(round_, decimal_rounding_option=ROUND_CEILING)
round_floor = functools.partial(round_, decimal_rounding_option=ROUND_FLOOR)
round_half_down = functools.partial(round_, decimal_rounding_option=ROUND_HALF_DOWN)
round_half_even = functools.partial(round_, decimal_rounding_option=ROUND_HALF_EVEN)
round_half_up = functools.partial(round_, decimal_rounding_option=ROUND_HALF_UP)


# prefer native round
if six.PY3:
  round_half_even = round
else:
  round_half_up = round


ModuleSecurityInfo(__name__).declarePublic(
  'round_down',
  'round_up',
  'round_ceiling',
  'round_floor',
  'round_half_down',
  'round_half_even',
  'round_half_up',
)


@zope.interface.implementer(IRoundingTool)
class RoundingTool(BaseTool):
  """Rounding Tool"""
  id = 'portal_roundings'
  title = 'Roundings'
  meta_type = 'ERP5 Rounding Tool'
  portal_type = 'Rounding Tool'

  security = ClassSecurityInfo()

  security.declarePublic('findRoundingModelValueList')
  def findRoundingModelValueList(self, document, property_id=None, context=None):
    """
    Return a list of matched rounding models for `document` which is ordered
    by increasing distance from `context`.
    """
    portal = self.getPortalObject()
    parent_uid_list = [portal.portal_roundings.getUid()]
    kw = {}

    if context is not None:
      current_document = context
      while True:
        if (current_document is None or current_document is portal or
            not current_document.getUid() or
            current_document.getUid() in parent_uid_list):
          break
        else:
          parent_uid_list.append(current_document.getUid())
          current_document = current_document.aq_parent

      context_path = context.getPhysicalPath()
      def sortKeyMethod(document):
        result = 0
        for a, b in zip(context_path, document.getPhysicalPath()):
          if a != b:
            break
          result -= 1
        return result
      kw['sort_key_method'] = sortKeyMethod

    result = portal.portal_domains.searchPredicateList(
      context=document,
      parent_uid=parent_uid_list,
      portal_type='Rounding Model',
      validation_state='validated',
      **kw)

    if property_id is not None:
      for rounding_model in result:
        if property_id in rounding_model.getRoundedPropertyIdList():
          return [rounding_model]
    return result

  security.declarePublic('getRoundingProxy')
  def getRoundingProxy(self, document, context=None):
    """
    Return a rounding proxy object which getter methods returns rounded
    value by following matched rounding model definition.
    """
    target_object = document
    for rounding_model in self.findRoundingModelValueList(document, context=context):
      target_object = rounding_model.getRoundingProxy(target_object)
    return target_object

  security.declarePublic('getDecimalRoundingOptionItemList')
  def getDecimalRoundingOptionItemList(self):
    """
    Return the possible decimal rounding option item list which is provided
    by python standard decimal module.
    """
    return ROUNDING_OPTION_DICT.items()

  security.declarePublic('round')
  round = staticmethod(round_)