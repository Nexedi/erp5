##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

class ResourceMeasuresConsistencyConstraint:
    """
    Define an Resource Measures Consistency Constraint for ZODB
    Property Sheets
    """
    _properties = (
        {   'id': 'message_measure_no_quantity_unit',
            'type': 'string',
            'description' : "Error message when the measure doesn't have a "\
                            "valid quantity_unit",
            'default': "Measure for metric_type '${metric_type}' doesn't "\
                       "have a valid quantity_unit" },
        {   'id': 'message_measure_no_quantity',
            'type': 'string',
            'description' : "Error message when the measure doesn't have a "\
                            "valid quantity value",
            'default': "Measure for metric_type '${metric_type}' doesn't "\
                       "have a valid quantity value" },
        {   'id': 'message_duplicate_metric_type',
            'type': 'string',
            'description' : 'Error message when several measures have the '\
                            'same metric_type',
            'default': "Several measures have the same metric_type "\
                       "'${metric_type}'" },
        {   'id': 'message_duplicate_default_measure',
            'type': 'string',
            'description' : 'Error message when several measures are '\
                            'associated to the same unit',
            'default': "Several measures are associated to the same unit "\
                       "'${quantity_unit}'" },
        {   'id': 'message_missing_metric_type',
            'type': 'string',
            'description' : "Error message when the metric category doesn't "\
                            "exist",
            'default': "Implicit measure for the management unit can't be "\
                       "created because 'metric_type/${metric_type}' "\
                       "category doesn't exist" },
        )
