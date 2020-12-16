##############################################################################
#
# Copyright (c) 2014 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly advised to contract a Free Software
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

from DateTime import DateTime
from erp5.component.module.DateUtils import addToDate
import re

def render_date_range(date_range):
  m = re.match(r'(\d+)([dwmy])', date_range)
  if m is not None:
    period_dict = {
      'd':'day',
      'w':'week',
      'm':'month',
      'y':'year',
    }
    num, period = m.groups()
    period = period_dict[period.lower()]
    return addToDate(DateTime(), **{period:-int(num)})

def recurseUpdateSyntaxNode(self, node):
  if node.isLeaf():
    pass
  elif node.isColumn():
    if node.column_name == 'mine':
      node.column_name = 'owner'
      node.node.value = self.portal_membership.getAuthenticatedMember().getId()
    elif node.column_name == 'state' and node.node.value != 'all':
      node.column_name = 'simulation_state'
    elif node.column_name == 'type' and node.node.value != 'all':
      node.column_name = 'portal_type'
    elif node.column_name == 'file':
      node.column_name = 'source_reference'
    elif node.column_name == 'filetype':
      node.column_name = 'source_reference'
      node.node.value = '%%.%s' % node.node.value
    elif node.column_name == 'created':
      node.column_name = 'creation_date'
      node.node.value = render_date_range(node.node.value)
      node.node.comparison_operator = '>='
    elif node.column_name == 'creation_from':
      node.column_name = 'creation_date'
      node.node.comparison_operator = '>='
    elif node.column_name == 'creation_to':
      node.column_name = 'creation_date'
      node.node.comparison_operator = '<='
    elif node.column_name == 'modification_from':
      node.column_name = 'modification_date'
      node.node.comparison_operator = '>='
    elif node.column_name == 'modification_to':
      node.column_name = 'modification_date'
      node.node.comparison_operator = '<='
  else:
    for subnode in node.getNodeList():
      recurseUpdateSyntaxNode(self, subnode)

def getAdvancedSearchSyntaxTreeNode(self, search_text, column):
  sql_catalog = self.getPortalObject().portal_catalog.getSQLCatalog()
  node = sql_catalog.parseSearchText(search_text=search_text, column=column, is_valid=lambda x:True)
  if node is not None:
    recurseUpdateSyntaxNode(self, node)
  return node
