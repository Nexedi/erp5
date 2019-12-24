# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
#                    Ivan Tyagov <ivan@nexedi.com>
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


def ERP5Site_dumpWorkflowChainByPortalType(self, REQUEST=None):
  # This method outputs the workflow chain by portal type
  # ---
  # {"Account": ['account_workflow', "edit_workflow"]}
  # ---
  #
  if REQUEST:
    raise RuntimeError("You can not call this script from the url")
  workflow_tool = self.getPortalObject().portal_workflow
  cbt = workflow_tool._chains_by_type
  ti = workflow_tool._listTypeInfo()
  chain_by_type_dict = {}
  for t in ti:
    type_information_id = t.getId()
    title = t.Title()
    if title == type_information_id:
      title = None
    if cbt is not None and cbt.has_key(type_information_id):
      chain = sorted(cbt[type_information_id])
    else:
      chain = ['(Default)']
    chain_by_type_dict.setdefault(type_information_id, []).extend(chain)
  return chain_by_type_dict