##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
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

def ERP5Site_getERP5InstanceState(self, witch_login=None, witch_password=None):
  """
    This script get some information from the instance. This usefull for 
    compare informations and verify the status of the instance.
  """
  result = {}
  preferences = {}
  portal = self.getPortalObject()
  portal_preferences = portal.portal_preferences
  portal_wizard = portal.portal_wizard

  # wizard authentication
  if witch_password is not None and witch_login is not None:
    result['witch_authentication'] = portal_wizard._isCorrectConfigurationKey(witch_login, witch_password)
  else:
    result['witch_authentication'] = -1

  for accessor_name in ('PreferredExpressUserId',
                        'PreferredExpressPassword',
                        'PreferredWitchToolServerUrl',
                        'PreferredWitchToolServerRoot',
                        'PreferredExpressSubscriptionStatus',
                        'PreferredExpressErp5Uid',
                        'PreferredHtmlStyleAccessTab',):
    preferences[accessor_name] = getattr(portal_preferences, 'get%s' % accessor_name)()
  result['preference_dict'] = preferences
  # bt5 list
  result['bt5_list'] = [{'title': x.getTitle(), 
                         'version': x.getVersion(),
                         'revision': x.getRevision()} for x in 
                          portal.portal_templates.getInstalledBusinessTemplateList()]

  return result
