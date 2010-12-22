##############################################################################
#
# Copyright (c) 2006-2007 Nexedi SARL and Contributors. All Rights Reserved.
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

class ExternalDocument:
  """
  Properties of documents which have been downloaded from a URL. Most
  properties are used by the crawling API to frequently update content
  if necessary.
  """
  _properties = (
        {   'id'          : 'crawling_cache_duration',
            'description' : 'Defines the number of day a document should be kept in'
                            'public cache after it has disappeared from the Web.',
            'default'     : 10,
            'type'        : 'int',
            'mode'        : 'w'},
        {   'id'          : 'crawling_depth',
            'description' : 'Defines the maximum number of links which can be followed in the'
                            'crawling process. If set to 0 (default), no crawling happens.',
            'type'        : 'int',
            'default'     : 0,
            'mode'        : 'w'},
        {   'id'          : 'crawling_scope',
            'description' : 'Defines whether the crawling process should be local to a single'
                            'domain or IP host. If so, crawling will not try to access'
                            'links outside the initial host.',
            'type'        : 'string',
            'mode'        : 'w'},
        )
