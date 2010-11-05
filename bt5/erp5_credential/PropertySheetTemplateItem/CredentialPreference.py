#############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
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


class CredentialPreference:
  """
    This property sheet defines configurable preference for credential managment.
  """

  _properties = (
    { 'id'          : 'preferred_credential_request_automatic_approval',
      'description' : 'Automaticaly accept credential request',
      'type'        : 'boolean',
      'preference'  : 1,
      'default'     : False,
      'write_permission': 'Manage properties',
      'mode'        : '' },
    { 'id'          : 'preferred_credential_recovery_automatic_approval',
      'description' : 'Automaticaly accept credential recovery',
      'type'        : 'boolean',
      'preference'  : 1,
      'default'     : False,
      'write_permission': 'Manage properties',
      'mode'        : '' },
    { 'id'          : 'preferred_person_credential_update_automatic_approval',
      'description' : 'Automaticaly accept credential update of a person',
      'type'        : 'boolean',
      'preference'  : 1,
      'default'     : False,
      'write_permission': 'Manage properties',
      'mode'        : '' },
    { 'id'          : 'preferred_organisation_credential_update_automatic_approval',
      'description' : 'Automaticaly accept credential update of an organisation',
      'type'        : 'boolean',
      'preference'  : 1,
      'default'     : False,
      'write_permission': 'Manage properties',
      'mode'        : '' },
    { 'id'          : 'preferred_credential_assignment_duration',
      'description' : 'Validation duration  for assignments created from a credential (Days)',
      'type'        : 'int',
      'preference'  : 1,
      'default'     : 3650,
      'write_permission': 'Manage properties',
      'mode'        : '' },
    { 'id'          : 'preferred_login_and_password_notifier',
      'description' : 'Which notifier use to send password and login.("Mail Message", "SMS",...)',
      'type'        : 'text',
      'preference'  : 1,
      'default'     : 'Mail Message',
      'write_permission': 'Manage properties',
      'mode'        : '' },
    )
