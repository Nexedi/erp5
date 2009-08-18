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

from Products.ERP5Type import Permissions
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Globals import InitializeClass

class BuilderTool(BaseTool):
  """Base class for builder tools

  Builders can be local or global.

  It is safe to have only one instance of builder working at same time.

  Parameters common for methods:

    input_movement_list - optional list of movements to deliver. Corresponding
      script name is simulation_select_method_id (to rename to
      input_movement_select_method_id), defaults to type based method named
      BuilderPortalType_selectDefaultMovement

    business_process_list - optional Business Process list, if defined only
      builders for Business Paths contained in those Business Process will
      be run

    trade_phase_list - optional list of trade phases, if defined only
      Business Paths for this trade phase will be used

    existing_delivery_list - list of deliveries to which builder will *try*
      add new/update existing movements and update delivery. It is not
      guaranteed - if builder configuration (deliver movement groups) are
      not selecting those deliveries they won't be updated, new ones will
      be created. Corresponding script is delivery_select_method_id.
  """

  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBuilderValueList')
  def getBuilderValueList(self, business_process_list=None,
        trade_phase_list=None):
    """Returns sorted builder list with proper condition"""
    if business_process_list is None and trade_phase_list is None:
      builder_value_list = self.contentValues()
    else:
      if business_process_list is None:
        return []
      builder_value_list = []
      method_id_dict = {
        'Order Tool': 'getRelatedOrderBuilderValueList',
        'Delivery Tool': 'getRelatedDeliveryBuilderValueList',
      }
      method_id = getattr(self,method_id_dict[self.getPortalType()])
      for business_process_url in business_process_list:
        business_process = self.unrestrictedTraverse(business_process_url)
        for business_path in business_process.getPathValueList(
            trade_phase=trade_phase_list):
          builder_value_list.extend(getattr(business_path,method_id)())

    # FIXME: what kind of sorting to use?
    return sorted(builder_value_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'build')
  def build(self, input_movement_list=None, existing_delivery_list=None,
      business_process_list=None, trade_phase_list=None):
    """Informs all builders to be build or invoke building

      If parameters are not passed (like input_movement_list,
      existing_delivery_list, ...) it will just inform builder to build.
      Otherwise it will invoke builder with parameters.
    """
    for builder in self.getBuilderValueList(
        business_process_list=business_process_list,
        trade_phase_list=trade_phase_list):
      if input_movement_list is None and existing_delivery_list is None:
        # no parameters are passed to builder - asynchronous way
        if builder.isEnabled() and not builder.isActive():
          # as this is normal invocation, just run it if it is not running yet
          builder.activeSense()
      else:
        # parameter goes to builder, so this builder shall be invoked at once
        # with parameters - at one way
        # stop on first found builder for parameter based invocation
        return builder.build(input_movement_list=input_movement_list,
            existing_delivery_list=existing_delivery_list)

InitializeClass(BuilderTool)
