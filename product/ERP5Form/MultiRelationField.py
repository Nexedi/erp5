##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.Formulator import Widget, Validator
from Products.Formulator.Field import ZMIField
from Products.Formulator.DummyField import fields
from Products.ERP5Type.Utils import convertToUpperCase

class MultiRelationStringFieldWidget(Widget.LinesTextAreaWidget):
    """
        RelationStringField widget

        Works like a string field but includes one buttons

        - one search button which updates the field and sets a relation

        - creates object if not there

    """
    property_names = Widget.LinesTextAreaWidget.property_names + \
      ['update_method', 'jump_method', 'base_category', 'portal_type', 'catalog_index',
       'default_module']

    update_method = fields.StringField('update_method',
                               title='Update Method',
                               description=(
        "The method to call to set the relation. Required."),
                               default="base_update_relation",
                               required=1)

    jump_method = fields.StringField('jump_method',
                               title='Jump Method',
                               description=(
        "The method to call to jump to the relation. Required."),
                               default="base_jump_relation",
                               required=1)

    base_category = fields.StringField('base_category',
                               title='Base Category',
                               description=(
        "The method to call to set the relation. Required."),
                               default="",
                               required=1)

    portal_type = fields.ListTextAreaField('portal_type',
                               title='Portal Type',
                               description=(
        "The method to call to set the relation. Required."),
                               default="",
                               required=1)

    catalog_index = fields.StringField('catalog_index',
                               title='Catalog Index',
                               description=(
        "The method to call to set the relation. Required."),
                               default="",
                               required=1)

    default_module = fields.StringField('default_module',
                               title='Default Module',
                               description=(
        "The module which should be invoked to create new objects."),
                               default="",
                               required=1)

    def render(self, field, key, value, REQUEST):
        """Render text input field.
        """
        html_string = Widget.LinesTextAreaWidget.render(self, field, key, value, REQUEST)
        portal_url_string = getToolByName(here, 'portal_url')()
        # We add a button which has a path reference to a base category...
        html_string += '&nbsp;&nbsp;<input type="image" src="%s/images/exec16.png" value="update..." name="%s:method">' \
            % (portal_url_string,field.get_value('update_method'))
        if value not in ((), [], None, ''):
          if REQUEST.get('selection_name') is not None:
            html_string += '&nbsp;&nbsp;<a href="%s?field_id=%s&form_id=%s&selection_name=%s&selection_index=%s"><img src="%s/images/jump.png"></a>' \
              % (field.get_value('jump_method'), field.id, field.aq_parent.id, REQUEST.get('selection_name'), REQUEST.get('selection_index'),portal_url_string)
          else:
            html_string += '&nbsp;&nbsp;<a href="%s?field_id=%s&form_id=%s"><img src="%s/images/jump.png"></a>' \
              % (field.get_value('jump_method'), field.id, field.aq_parent.id,portal_url_string)
        return html_string

MultiRelationStringFieldWidgetInstance = MultiRelationStringFieldWidget()
MultiRelationStringFieldValidatorInstance = Validator.LinesValidator()

class MultiRelationStringField(ZMIField):
    meta_type = "MultiRelationStringField"

    widget = MultiRelationStringFieldWidgetInstance
    validator = MultiRelationStringFieldValidatorInstance



