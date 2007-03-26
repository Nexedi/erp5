##############################################################################
#
## Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#
## WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# # consequences resulting from its eventual inadequacies and bugs
# # End users who are looking for a ready-to-use solution with commercial
# # garantees and support are strongly adviced to contract a Free Software
# # Service Company
# #
# # This program is Free Software; you can redistribute it and/or
# # modify it under the terms of the GNU General Public License
# # as published by the Free Software Foundation; either version 2
# # of the License, or (at your option) any later version.
# #
# # This program is distributed in the hope that it will be useful,
# # but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # GNU General Public License for more details.
# #
# # You should have received a copy of the GNU General Public License
# # along with this program; if not, write to the Free Software
# # Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# #
# ##############################################################################

class Document:
  """
    This propert sheet defines the default taxonomy for Document management in ERP5.
  """

  _properties = (
    { 'id'              : 'base_data',
      'description'     : 'An object (string, stream, etc.) which contains raw data'
                          'to store the converted content of the document in its base format',
      'type'            : 'object',
      'default'         : '',
      'read_permission' : 'Manage properties',
      'mode'            : 'w' },
    { 'id'              : 'base_content_type',
      'description'     : 'A string which represents the mime type of the base data',
      'type'            : 'string',
      'read_permission' : 'Manage properties',
      'mode'            : 'w' },
  )

  _categories = ('similar', 'predecessor', 'successor', 'contributor', 'classification',
                 # Source project is set by default since project is equivalent to workspace
                 'source_project',
                 # Source is defined in DMS documentation
                 'source',
                 # XXX-JPS where are these defined in documentation. Why ?
                 'destination',
                 # XXX-JPS all the following properties should be configured on portal type
                 # and removed from here
                 'publication_section', 'function', 'group', 'site')


