##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.Constraint import Constraint

class ResourceMeasuresConsistency(Constraint):
  """Check that measures defined on a resource are not meaningless.

  Choosing quantity units for a resource without defining measures is
  tolerated, for compatibility, although conversion between units won't be
  possible.
  """

  _message_id_list = ['message_measure_no_quantity_unit',
                      'message_measure_no_quantity',
                      'message_duplicate_metric_type',
                      'message_duplicate_default_measure',
                      'message_missing_metric_type']

  _message_measure = "Measure for metric_type '${metric_type}' "
  message_measure_no_quantity_unit = \
    _message_measure + "doesn't have a valid quantity_unit"
  message_measure_no_quantity = \
    _message_measure + "doesn't have a valid quantity value"
  message_duplicate_metric_type = \
    "Several measures have the same metric_type '${metric_type}'"
  message_duplicate_default_measure = \
    "Several measures are associated to the same unit '${quantity_unit}'"
  message_missing_metric_type = \
    "Implicit measure for the management unit can't be created" \
    " because 'metric_type/${metric_type}' category doesn't exist."

  def checkConsistency(self, obj, fixit=0):
    """Implement here the consistency checker
    """
    error_list = []
    portal = obj.getPortalObject()

    if obj.getPortalType() not in portal.getPortalResourceTypeList():
      return error_list

    error = lambda msg, **kw: error_list.append(
      self._generateError(obj, self._getMessage(msg), mapping=kw))

    getCategoryValue = portal.portal_categories.getCategoryValue
    display = lambda *args, **kw: \
      getCategoryValue(*args, **kw).getCompactLogicalPath()

    top = lambda relative_url: relative_url.split('/', 1)[0]

    quantity_map = {}
    metric_type_set = set()

    for measure in obj.getMeasureList():
      metric_type = measure.getMetricType()
      if metric_type:
        quantity = top(metric_type)
        default_or_generic = quantity_map.setdefault(quantity, [0, 0])
        if measure.getDefaultMetricType():
          default_or_generic[0] += 1
        if quantity == metric_type:
          default_or_generic[1] += 1

        if not measure.getConvertedQuantityUnit():
          error('message_measure_no_quantity_unit',
                metric_type=display(metric_type, 'metric_type'))
        elif not measure.asCatalogRowList():
          error('message_measure_no_quantity',
                metric_type=display(metric_type, 'metric_type'))
        if metric_type in metric_type_set:
          error('message_duplicate_metric_type',
                metric_type=display(metric_type, 'metric_type'))
        else:
          metric_type_set.add(metric_type)
      #else:
      # pass # we don't care about undefined measures

    for i, quantity_unit in enumerate(obj.getQuantityUnitList()):
      quantity = top(quantity_unit)
      default, generic = quantity_map.get(quantity, (0, 0))
      if (default or generic) > 1:
        error('message_duplicate_default_measure',
              quantity_unit=display(quantity_unit, 'quantity_unit'))
      elif not (default or generic):
        if i:
          pass # tolerate quantity units without any measure associated to them
        else: # management unit: check we can create an implicit measure
          if getCategoryValue(quantity, 'metric_type') is None:
            error('message_missing_metric_type', metric_type=quantity)

    return error_list
