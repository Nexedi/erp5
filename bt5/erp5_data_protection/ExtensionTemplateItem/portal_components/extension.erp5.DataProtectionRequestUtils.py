# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
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

from Products.ERP5Form.FormBox import FormBox
from six.moves.urllib.parse import urlparse

def Base_updatePropertyMapListWithFieldLabel(self, property_map_list):
  """Try to get the title of field which edit the given inside property_map_list
  - This script loopup portal_type, then list actions of type view
  - Fetch the form by parsing url
  - list fields, and get the field label
  - update the dictionary and return the list of updated dictionaries.
  """
  def getLabelFromForm(form, property_id):
    for field in form.get_fields():
      if isinstance(field, FormBox):
        # Special use case for FormBox
        delegated_form_id = field.get_value('formbox_target_id')
        form_box = getattr(field, delegated_form_id)
        label = getLabelFromForm(form_box, property_id)
        if label:
          return label
      if 'my_%s' % property_id == field.id:
        label = field.get_value('title')
        return label
  portal = self.getPortalObject()
  result_list = []
  action_list_dict = portal.portal_actions.listFilteredActionsFor(self)
  action_list = action_list_dict.get('object_view', ())
  form_id_list = [urlparse(action['url'])[2].split('/')[-1] \
                                             for action in action_list]
  for property_map in property_map_list:
    label = None
    for form_id in form_id_list:
      form = getattr(portal, form_id)
      if form.meta_type != 'ERP5 Form':
        continue
      label = getLabelFromForm(form, property_map['id'])
      if label:
        property_map['label'] = label
        break
    result_list.append(property_map)
  return tuple(result_list)

def Base_purgeWorkflowHistoryCommentList(self):
  """Delete all comment in wokflow history stored on document.
  """
  for workflow_id in self.workflow_history:
     [history.update({'comment': None}) for history in self.workflow_history[workflow_id]]
