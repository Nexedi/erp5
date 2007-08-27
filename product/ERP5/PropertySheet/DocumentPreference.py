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


class DocumentPreference:
  """
    This property sheet defines the user configurable taxonomy.
  """

  _properties = (
    { 'id'          : 'preferred_ooodoc_server_address',
      'description' : 'address of a server for converting docs (ip or domain)',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : '' },
    { 'id'          : 'preferred_ooodoc_server_port_number',
      'description' : 'port number of a server for converting docs',
      'type'        : 'int',
      'preference'  : 1,
      'mode'        : '' },
    { 'id'          : 'preferred_document_reference_regular_expression',
      'description' : 'a regular expression to find and verify doc references',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : '' },
    { 'id'          : 'preferred_document_file_name_regular_expression',
      'description' : 'a regular expression to parse file names',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : '' },
    { 'id'          : 'preferred_document_reference_method_id',
      'description' : 'function for parsing, finding and verifying doc reference',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : '' },
    { 'id'              : 'preferred_document_ingestion_email_notification',
      'description'     : 'None - always, "always", "problem (only if problem), "never"', # XXX-JPS this is not a description
      'type'            : 'selection',
      'select_variable' : 'getPreferredDocumentIngestionEmailNotificationSelectionList',
      'preference'      : 1,
      'mode'            : '' },
    { 'id'          : 'preferred_document_email_ingestion_address',
      'description' : 'Email ingestion address',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : '' },
    # XXX-JPS. This is not a real property - it is somehow a hack.
    # BG: I was advised by somebody from Nexedi (I think it was Jerome)
    { 'id'              : 'preferred_document_ingestion_email_notification_selection',
      'description'     : 'List of possible values for preferred_document_ingestion_email_notification',
      'type'            : 'tokens',
      'default'         : ['always','problem','never'],
      'mode'            : 'w'},
    )

# vim: shiftwidth=2

