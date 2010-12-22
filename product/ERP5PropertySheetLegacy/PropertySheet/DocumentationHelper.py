##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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

class DocumentationHelper:
    """
        DocumentationHelper attributes definition.
    """

    _properties = (
        {   'id'          : 'type',
            'description' : 'Text representation of the documented item\'s '\
                            'type.',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'content',
            'description' : 'Text representation (as in repr()) of the '\
                            'documented item\'s content',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'security',
            'description' : 'Security defined on the documented item.',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'argument',
            'description' : 'List of arguments. See doc(inspect.getargspec).',
            'type'        : 'lines',
            'mode'        : 'w' },
        {   'id'          : 'inheritance',
            'description' : 'Inheritance list.',
            'type'        : 'lines',
            'mode'        : 'w' },
        {   'id'          : 'source_path',
            'description' : 'String representation of the path of the place '\
                            'where the documented item is defined.',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'source_code',
            'description' : 'Source code of the documented item.',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'static_method',
            'description' : 'List of DocHelper objects documenting item\'s '\
                            'methods.',
            'type'        : 'lines',
            'mode'        : 'w' },
        {   'id'          : 'static_property',
            'description' : 'List of DocHelper objects documenting item\'s '\
                            'properties.',
            'type'        : 'lines',
            'mode'        : 'w' },
        {   'id'          : 'dynamic_accessor',
            'description' : 'List of DocHelper objects documenting item\'s '\
                            'accessors.',
            'type'        : 'lines',
            'mode'        : 'w' },
        {   'id'          : 'dynamic_method',
            'description' : 'List of DocHelper objects documenting item\'s '\
                            'dynamic methods, except accessors.',
            'type'        : 'lines',
            'mode'        : 'w' },
        {   'id'          : 'dynamic_property',
            'description' : 'List of DocHelper objects documenting item\'s '\
                            'dynamic properties.',
            'type'        : 'lines',
            'mode'        : 'w' },
        {   'id'          : 'dynamic_category',
            'description' : 'List of DocHelper objects documenting item\'s '\
                            'dynamic categories.',
            'type'        : 'lines',
            'mode'        : 'w' },
    )

    _categories = ()
