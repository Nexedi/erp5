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
from Products.CMFCore.utils import getToolByName
from Globals import get_request
from Products.PythonScripts.Utility import allow_class

from zLOG import LOG
MAX_SELECT = 50 # Max. number of catalog result
new_content_prefix = '_newContent_'


class RelationStringFieldWidget(Widget.TextWidget, Widget.ListWidget):
    """
        RelationStringField widget

        Works like a string field but includes one buttons

        - one search button which updates the field and sets a relation

        - creates object if not there

    """
    property_names = Widget.TextWidget.property_names + \
      ['update_method', 'jump_method', 'base_category', 'portal_type', 'catalog_index',
       'default_module', 'relation_setter_id', 'columns',
       'first_item', 'items', 'size', 'extra_item']

    update_method = fields.StringField('update_method',
                               title='Update Method',
                               description=(
        "The method to call to set the relation. Required."),
                               default="Base_validateRelation",
                               required=1)

    jump_method = fields.StringField('jump_method',
                               title='Jump Method',
                               description=(
        "The method to call to jump to the relation. Required."),
                               default="Base_jumpToRelatedDocument",
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

    relation_setter_id = fields.StringField('relation_setter_id',
                               title='Relation Update Method',
                               description=(
        "The method to invoke in order to update the relation"),
                               default="",
                               required=0)

    size = fields.IntegerField('size',
                               title='Size',
                               description=(
        "The display size in rows of the field. If set to 1, the "
        "widget will be displayed as a drop down box by many browsers, "
        "if set to something higher, a list will be shown. Required."),
                               default=1,
                               required=1)                               
                               
    columns = fields.ListTextAreaField('columns',
                                 title="Columns",
                                 description=(
        "A list of attributes names to display."),
                                 default=[],
                                 required=0)

    def render(self, field, key, value, REQUEST):
        """Render text input field.
        """
        relation_field_id = 'relation_%s' % key
        relation_item_id = 'item_%s' % key
        here = REQUEST['here']
        portal_url = getToolByName(here, 'portal_url')
        portal_url_string = portal_url()
        portal_object = portal_url.getPortalObject()
        html_string = Widget.TextWidget.render(self, field, key, value, REQUEST)
        if REQUEST.has_key(relation_item_id):
          # Define default tales on the fly
          tales_expr = field.tales.get('items', None)
          if not tales_expr:
            from Products.Formulator.TALESField import TALESMethod
            field.tales['items'] = TALESMethod('REQUEST/relation_item_list')
          REQUEST['relation_item_list'] = REQUEST.get(relation_item_id)
          html_string += '&nbsp;%s&nbsp;' % Widget.ListWidget.render(self, 
                                field, relation_field_id, None, REQUEST)   
          REQUEST['relation_item_list'] = None          
        # We used to add a button which has a path reference to a base category...
        # but it really created too many problems
        # now we do it in another way
        # we compare what has been changed in the relation update script
        html_string += '&nbsp;<input type="image" src="%s/images/exec16.png" value="update..." name="%s/portal_selections/viewSearchRelatedDocumentDialog%s:method">' \
          %  (portal_url_string, portal_object.getPath(), field.aq_parent._v_relation_field_index)

        field.aq_parent._v_relation_field_index += 1 # Increase index                

        if value not in ('', None) and not REQUEST.has_key(relation_item_id) and value == field.get_value('default'):
          if REQUEST.get('selection_name') is not None:
            html_string += '&nbsp;&nbsp;<a href="%s/%s?field_id=%s&form_id=%s&selection_name=%s&selection_index=%s"><img src="%s/images/jump.png"></a>' \
              % (here.absolute_url(), field.get_value('jump_method'), field.id, field.aq_parent.id, REQUEST.get('selection_name'), REQUEST.get('selection_index'),portal_url_string)
          else:
            html_string += '&nbsp;&nbsp;<a href="%s/%s?field_id=%s&form_id=%s"><img src="%s/images/jump.png"></a>' \
              % (here.absolute_url(), field.get_value('jump_method'), field.id, field.aq_parent.id,portal_url_string)        
        return html_string

    def render_view(self, field, value):
        """Render text input field.
        """
        REQUEST = get_request()
        here = REQUEST['here']
        html_string = Widget.TextWidget.render_view(self, field, value)
        portal_url_string = getToolByName(here, 'portal_url')()
        if value not in ('', None):
          html_string = '<a href="%s/%s?field_id=%s&form_id=%s">%s</a>' \
            % (here.absolute_url(), field.get_value('jump_method'), field.id, field.aq_parent.id, html_string)
          html_string += '&nbsp;&nbsp;<a href="%s/%s?field_id=%s&form_id=%s"><img src="%s/images/jump.png"></a>' \
            % (here.absolute_url(), field.get_value('jump_method'), field.id, field.aq_parent.id, portal_url_string)
        return html_string

class RelationEditor:
    """
      A class holding all values required to update a relation
    """

    def __init__(self, field_id, base_category, portal_type, uid, portal_type_item, 
                       key, value, relation_setter_id, display_text):
      self.field_id = field_id
      self.uid = uid
      self.base_category = base_category
      self.portal_type = portal_type
      self.portal_type_item = portal_type_item
      self.key = key
      self.value = value
      self.relation_setter_id = relation_setter_id
      self.display_text = display_text
      
    def __call__(self, REQUEST):
      if self.uid is not None:      
        # Decorate the request so that we can display
        # the select item in a popup
        relation_field_id = 'relation_%s' % self.field_id      
        relation_item_id = 'item_%s' % self.field_id
        REQUEST.set(relation_item_id, ((self.display_text, self.uid),))
        REQUEST.set(relation_field_id, self.uid)
        REQUEST.set(self.field_id[len('field_'):], self.value) # XXX Dirty
      else:
        # Make sure no default value appears
        REQUEST.set(self.field_id[len('field_'):], None)      
      
    def view(self):
      return self.__dict__        
        
    def edit(self, o):    
      if self.uid is not None:
        if type(self.uid) is type('a') and self.uid.startswith(new_content_prefix):
          # Create a new content
          portal_type = self.uid[len(new_content_prefix):]
          portal_module = None
          for p_item in self.portal_type_item:
            if p_item[0] == portal_type:
              #portal_module = p_item[1]
              portal_module = o.getPortalObject().getDefaultModuleId( p_item[0] )
          if portal_module is not None:              
            portal_module_object = getattr(o.getPortalObject(), portal_module)
            kw ={}
            kw[self.key] = self.value
            kw['portal_type'] = portal_type
            new_object = portal_module_object.newContent(**kw)
            self.uid = new_object.getUid()
          else:
            raise             

        # Edit relation        
        if self.relation_setter_id:
          relation_setter = getattr(o, self.relation_setter_id)
          relation_setter((), portal_type=self.portal_type)
          relation_setter((int(self.uid),), portal_type=self.portal_type)         
        else:
          o._setValueUids(self.base_category, (), portal_type=self.portal_type)      
          o._setValueUids(self.base_category, (int(self.uid),), portal_type=self.portal_type)      

      else:
        if self.value == '':
          # Delete relation        
          if self.relation_setter_id:
            relation_setter = getattr(o, self.relation_setter_id)
            relation_setter((), portal_type=self.portal_type)
          else:
            o._setValueUids(self.base_category, (), portal_type=self.portal_type)      


allow_class(RelationEditor)

class RelationStringFieldValidator(Validator.StringValidator):   
    """
        Validation includes lookup of relared instances
    """    
    
    message_names = Validator.StringValidator.message_names +\
                    ['relation_result_too_long', 'relation_result_ambiguous', 'relation_result_empty',]

    relation_result_too_long = "Too many documents were found."
    relation_result_ambiguous = "Select appropriate document in the list."
    relation_result_empty = "No such document was found."
                          
    def validate(self, field, key, REQUEST):
      relation_field_id = 'relation_%s' % key      
      relation_item_id = 'item_%s' % key
      portal_type = map(lambda x:x[0],field.get_value('portal_type'))
      portal_type_item = field.get_value('portal_type')
      base_category = field.get_value( 'base_category')
      # If the value is different, build a query
      portal_selections = getToolByName(field, 'portal_selections')
      portal_catalog = getToolByName(field, 'portal_catalog')      
      # Get the current value
      value = Validator.StringValidator.validate(self, field, key, REQUEST)
      # If the value is the same as the current field value, do nothing
      current_value = field.get_value('default')
      # If a relation has been defined in a popup menu, use it
      relation_uid = REQUEST.get(relation_field_id, None)
      catalog_index = field.get_value('catalog_index')
      relation_setter_id = field.get_value('relation_setter_id')
      if value == current_value:
        return RelationEditor(key, base_category, portal_type, None, 
                              portal_type_item, catalog_index, value, relation_setter_id, None)
                              # Will be interpreted by Base_edit as "do nothing"
      if relation_uid not in (None, ''):
        # A value has been defined by the user
        if type(relation_uid) in (type([]), type(())): relation_uid = relation_uid[0]
        related_object = portal_catalog.getObject(relation_uid)
        if related_object is not None:
          display_text = str(related_object.getProperty(catalog_index))
        else:
          display_text = 'Object has been deleted'        
        return RelationEditor(key, base_category, portal_type, relation_uid, 
                              portal_type_item, catalog_index, value, relation_setter_id, display_text)

      # We must be able to erase the relation
      if value == '':
        display_text = 'Delete the relation'
        return RelationEditor(key, base_category, portal_type, None, 
                              portal_type_item, catalog_index, value, relation_setter_id, display_text)
                              # Will be interpreted by Base_edit as "delete relation" (with no uid and value = '')

        
      kw ={}
      kw[catalog_index] = value
      kw['portal_type'] = portal_type
      # Get the query results
      relation_list = portal_catalog(**kw)
      relation_uid_list = map(lambda x: x.uid, relation_list)
      # Prepare a menu
      menu_item_list = [('', '')]
      for p in portal_type:
        menu_item_list += [('New %s' % p, '%s%s' % (new_content_prefix,p))]      
      # If the length is 1, return uid
      if len(relation_list) == 1:
        relation_uid = relation_uid_list[0]
        related_object = portal_catalog.getObject(relation_uid)
        if related_object is not None:
          display_text = str(related_object.getProperty(catalog_index))
        else:
          display_text = 'Object has been deleted'        
          
        return RelationEditor(key, base_category, portal_type, relation_uid, 
                              portal_type_item, catalog_index, value, relation_setter_id, display_text)
      # If the length is 0, raise an error
      elif len(relation_list) == 0:
        REQUEST.set(relation_item_id, menu_item_list)
        self.raise_error('relation_result_empty', field)
      # If the length is short, raise an error
      elif len(relation_list) < MAX_SELECT:        
        menu_item_list += [('-', '')]        
        menu_item_list += map(lambda x: (x.getObject().getProperty(catalog_index), x.uid), 
                                                                        relation_list)
        REQUEST.set(relation_item_id, menu_item_list)
        self.raise_error('relation_result_ambiguous', field)
      else:
        # If the length is long, raise an error
        
        # If this error is raise, we don t want to create a new object...
        #REQUEST.set(relation_item_id, menu_item_list)
        self.raise_error('relation_result_too_long', field)    
        
RelationStringFieldWidgetInstance = RelationStringFieldWidget()
RelationStringFieldValidatorInstance = RelationStringFieldValidator()

class RelationStringField(ZMIField):
    meta_type = "RelationStringField"
    is_relation_field = 1

    widget = RelationStringFieldWidgetInstance
    validator = RelationStringFieldValidatorInstance



