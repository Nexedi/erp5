##############################################################################
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

class WebSection:
    """
        WebSite properties for all ERP5 objects
    """

    _properties = (
        {   'id'          : 'container_layout',
            'description' : 'ID of a page template or form which defines the rendering layout for the container',
            'type'        : 'string',
            'default'     : None,
            'acquisition_base_category'     : ('parent',),
            'acquisition_portal_type'       : ('Web Section', 'Web Site'),
            'acquisition_copy_value'        : 0,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getContainerLayout',
            'acquisition_depends'           : None,
            'mode'        : '' },
        {   'id'          : 'content_layout',
            'description' : 'ID of a page template or form which defines the rendering layout for contents',
            'type'        : 'string',
            'default'     : None,
            'acquisition_base_category'     : ('parent',),
            'acquisition_portal_type'       : ('Web Section', 'Web Site'),
            'acquisition_copy_value'        : 0,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getContentLayout',
            'acquisition_depends'           : None,
            'mode'        : '' },
        {   'id'          : 'webmaster',
            'description' : 'ID of a user which has complete access to all documents in the site.',
            'type'        : 'string',
            'default'     : None,
            'acquisition_base_category'     : ('parent',),
            'acquisition_portal_type'       : ('Web Section', 'Web Site'),
            'acquisition_copy_value'        : 0,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getWebmaster',
            'acquisition_depends'           : None,
            'mode'        : '' },
        {   'id'          : 'visible',
            'description' : 'Defines visibility of current section.',
            'type'        : 'boolean',
            'mode'        : 'rw' },
        {   'id'          : 'custom_render_method_id',
            'description' : 'ID of a page template, script, form or any callable object'
                            'which overrides the default rendering of the section',
            'type'        : 'string',
            'default'     : None,
            'mode'        : 'rw' },
    )

    _categories = ('aggregate', )

