#############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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


class CustomerRelationPreference:
  """
    This property sheet defines the user configurable taxonomy.
  """

  _properties = (
    { 'id'          : 'preferred_event_resource',
      'description' : 'Preferred resources to count the different kinds of Events',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'mode'        : '' },
    { 'id'          : 'preferred_campaign_resource',
      'description' : 'Preferred resources to count the different kinds of Events',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'mode'        : '' },
    { 'id'          : 'preferred_sale_opportunity_resource',
      'description' : 'Preferred resources to count the different kinds of Events',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'mode'        : '' },
    { 'id'          : 'preferred_meeting_resource',
      'description' : 'Preferred resources to count the different kinds of Events',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'mode'        : '' },
    { 'id'          : 'preferred_support_request_resource',
      'description' : 'Preferred resources to count the different kinds of Events',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'mode'        : '' },
    { 'id'          : 'preferred_event_assessment_form_id',
      'description' : 'Preferred forms to use in the assessing of ticket events.',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'mode'        : '' },
    { 'id'          : 'preferred_event_sender_email',
      'description' : 'Preferred email for replies sent through the CRM system.',
      'type'        : 'lines',
      'preference'  : 1,
      'default'     : [],
      'mode'        : '' },
    )
