# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Łukasz Nowak <luke@nexedi.com>
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
from AccessControl import ModuleSecurityInfo

TARGET_LEVEL_DELIVERY = 'DELIVERY'
TARGET_LEVEL_MOVEMENT = 'MOVEMENT'

ModuleSecurityInfo('Products.ERP5.PropertySheet.TradeModelLine').declarePublic(
  'TARGET_LEVEL_DELIVERY', 'TARGET_LEVEL_MOVEMENT')


class TradeModelLine:
  """
    Properties for trade model lines
  """
  _properties = (
    { 'id'          : 'create_line',
      'description' : 'A flag indicating if the corresponding line will'
                      ' be created',
      'type'        : 'boolean',
      'mode'        : 'w',
      'default'     : True,
    },
    { 'id'          : 'calculation_script_id',
      'description' : 'If a script is defined on trade model Line, this '
                      'script will be used for calculation',
      'type'        : 'string',
      'mode'        : 'w',
    },
    { 'id'          : 'target_level',
      'description' : 'Target level defines how trade model line is applied to '
                      'what(a set of movement or a movement). If target level '
                      'is `delivery`, then this is applied only at delivery '
                      'level(for example, VAT to total price of order). And if '
                      'target level is `movement`, then this is applied to one '
                      'movement and result will not be summed up(for example, '
                      'VAT to each order line). If target level is neither '
                      'delivery nor movement, this is applied to anything '
                      'without restriction.',
      'type'        : 'selection',
      'select_variable' : 'getTargetLevelSelectionList',
      'mode'        : 'w',
      'default'     : None,
    },
    { 'id'          : 'target_level_selection',
      'description' : 'List of possible values for target_level property',
      'type'        : 'tokens',
      'mode'        : '',
      'default'     : [TARGET_LEVEL_DELIVERY, TARGET_LEVEL_MOVEMENT],
    },
  )

  _categories = (
        'base_application', 'base_contribution', 'trade_phase',
      )
