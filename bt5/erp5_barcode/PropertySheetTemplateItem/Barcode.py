##############################################################################
#
# Copyright (c) 2002-2008 Nexedi SA and Contributors. All Rights Reserved.
#          Nicolas Delaby <nicolas@nexedi.com>
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

class Barcode:

    _properties = (
    {   'id'                : 'coding_type'
      , 'description'       : 'Type of Barceode Codification'
      , 'type'              : 'string'
      , 'mode'              : 'w'
    },

    {   'id'                : 'column_number'
      , 'description'       : 'Number of Columns'
      , 'type'              : 'int'
      , 'mode'              : 'w'
    },

    {   'id'                : 'row_number'
      , 'description'       : 'Number of Rows'
      , 'type'              : 'int'
      , 'mode'              : 'w'
    },

    {   'id'                : 'horizontal_padding'
      , 'description'       : 'Horizontal Padding'
      , 'type'              : 'int'
      , 'mode'              : 'w'
    },

    {   'id'                : 'vertical_padding'
      , 'description'       : 'Vertical Padding'
      , 'type'              : 'int'
      , 'mode'              : 'w'
    },

    {   'id'                : 'page_top_margin'
      , 'description'       : 'Page Top Margin'
      , 'type'              : 'int'
      , 'mode'              : 'w'
    },
    {   'id'                : 'page_bottom_margin'
      , 'description'       : 'Page Bottom Margin'
      , 'type'              : 'int'
      , 'mode'              : 'w'
    },

    {   'id'                : 'page_left_margin'
      , 'description'       : 'Page Left Margin'
      , 'type'              : 'int'
      , 'mode'              : 'w'
    },

    {   'id'                : 'page_right_margin'
      , 'description'       : 'Page Right Margin'
      , 'type'              : 'int'
      , 'mode'              : 'w'
    },

    {   'id'                : 'page_height'
      , 'description'       : 'Page Height'
      , 'type'              : 'int'
      , 'mode'              : 'w'
    },

    {   'id'                : 'page_width'
      , 'description'       : 'Page Width'
      , 'type'              : 'int'
      , 'mode'              : 'w'
    },

    )

