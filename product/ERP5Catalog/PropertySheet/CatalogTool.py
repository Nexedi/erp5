##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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


class CatalogTool() :
  """
  Properties that define CatalogTool.
  """

  _properties = (
    { 'id'      : 'default_sql_catalog_id',
      'description' : 'The id of the default SQL Catalog',
      'type'    : 'selection',
      'select_variable'    : 'getSQLCatalogIdList',
      'mode'    : 'w',
      'default' : None},

    # Hot Reindexing
    { 'id'      : 'source_sql_catalog_id',
      'description' : 'The id of a source SQL Catalog for hot reindexing',
      'type'    : 'string',
      'mode'    : '',
      'default' : None},
    { 'id'      : 'destination_sql_catalog_id',
      'description' : 'The id of a destination SQL Catalog for hot reindexing',
      'type'    : 'string',
      'mode'    : '',
      'default' : None},
    { 'id'      : 'hot_reindexing_state',
      'description' : 'The state of hot reindexing',
      'type'    : 'string',
      'mode'    : '',
      'default' : None},
    { 'id'      : 'archive_path',
      'description' : 'The path of the archive which is create',
      'type'    : 'string',
      'mode'    : '',
      'default' : None},

    # ERP5 Catalog defaults
    # Might be used later in reindexing
    { 'id'      : 'default_erp5_catalog_id',
      'description' : 'Default ERP5 Catalog Id',
      'type'    : 'selection',
      'select_variable' : 'getERP5CatalogIdList',
      'mode'    : 'w',
      'default' : None},
      )
