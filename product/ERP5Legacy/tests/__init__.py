# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################


def Legacy_getBusinessTemplateList(cls):
  getBusinessTemplateList = cls.getBusinessTemplateList
  def Legacy_getBusinessTemplateList(self):
    bt_list = []
    IGNORE_BUSINESS_TEMPLATE_LIST = ['erp5_simulation_test',
                    'erp5_configurator_standard_solver',
                    'erp5_configurator_standard_trade_template',
                    'erp5_configurator_standard_accounting_template',
                    'erp5_configurator_standard_invoicing_template']

    for bt in getBusinessTemplateList(self):
      if bt not in IGNORE_BUSINESS_TEMPLATE_LIST and bt not in bt_list:
        bt_list.append(bt)
        if bt == 'erp5_simulation':
          bt_list.append(bt +  '_legacy')
        elif bt in ('erp5_accounting', 'erp5_invoicing', 'erp5_mrp',
                    'erp5_project', 'erp5_trade'):
          bt_list.append(bt +  '_simulation_legacy')
    return tuple(bt_list)
  cls.getBusinessTemplateList = Legacy_getBusinessTemplateList

from Products.ERP5.tests import utils
utils.newSimulationExpectedFailure = lambda test: test
