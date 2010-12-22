# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Jean-Paul Smets <jp@nexedi.com>
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

class Data:
  """
     This property sheet defines the way to store data (file, images, etc.)
     in the form of an object of any type
  """

  _properties = (
    { 'id'          : 'data',
      'description' : 'An object (string, stream, etc.) which contains raw data',
      'type'        : 'data',
      'default'     : '',
      'mode'        : 'w' },
    { 'id'          : 'content_type',
      'description' : 'A string which represents the mime type of the data',
      'type'        : 'string',
      'default'     : 'application/unknown',
      'mode'        : 'w' },
    # Syntax of filename property is published by
    # Dublin Core DCMI Administrative Metadata.
    # final version dated of 28 October 2003 can be found at url:
    # http://dublincore.org/usage/meetings/2009/10/seoul/acore.pdf
    { 'id'          : 'filename',
      'description' : 'Name of provided file from where data come from',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'size',
      'description' : 'Size in bytes of the data',
      'type'        : 'int',
      'default'     : 0,
      'mode'        : 'w' },
   )
