##############################################################################
#
# Copyright (c) 2002, 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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
from Products.ERP5Form import RelationField
from Products.ERP5Form.RelationField import MAX_SELECT, new_content_prefix
from Globals import get_request
from Products.PythonScripts.Utility import allow_class

import string
from zLOG import LOG
#MAX_SELECT = 50 # Max. number of catalog result
#new_content_prefix = '_newContent_'

def checkSameKeys(a , b):
  """
    Checks if the two lists contain
    the same values
  """
  same = 1
  for ka in a:
    if (not ka in b) and (ka != ''):
      same = 0
  for kb in b:
    if (not kb in a) and (kb != ''):
      same = 0
  return same


class MultiRelationStringFieldWidget(Widget.LinesTextAreaWidget, RelationField.RelationStringFieldWidget):
    """
        RelationStringField widget

        Works like a string field but includes one buttons

        - one search button which updates the field and sets a relation

        - creates object if not there

    """
    property_names = Widget.LinesTextAreaWidget.property_names + \
                     RelationField.RelationStringFieldWidget.property_names

    # delete double in order to keep a usable ZMI...
    #property_names = dict([(i,0) for i in property_names]).keys() # XXX need to keep order !
    _v_dict = {}
    _v_property_name_list = []
    for property_name in property_names:
      if not _v_dict.has_key(property_name):
        _v_property_name_list.append(property_name)
        _v_dict[property_name] = 1
    property_names = _v_property_name_list
      

    def render(self, field, key, value, REQUEST):
        """
          Render text input field.
        """
        here = REQUEST['here']

        relation_field_id = 'relation_%s' % key
        relation_item_id = 'item_%s' % key

        portal_url = getToolByName(here, 'portal_url')
        portal_url_string = portal_url()
        portal_object = portal_url.getPortalObject()

        if type(value) == type(''):
          # Value is a string, reformat it correctly
          value_list = string.split(value, "\r\n")
        else:
          value_list = value

        need_validation = 0
        # Check all relation
        for i in range( len(value_list) ):
          relation_field_id = 'relation_%s_%s' % ( key, i )      
          relation_item_id = 'item_%s_%s' % ( key, i )      
          if REQUEST.has_key(relation_item_id) and value_list[i] != '':
            need_validation = 1
            break
          
        html_string = ''
        if need_validation:
          # Check all relation
          for i in range( len(value_list) ):
            value = value_list[i]
            relation_field_id = 'relation_%s_%s' % ( key, i )      
            relation_item_id = 'item_%s_%s' % ( key, i )      
            

            # If we get a empty string, display nothing !
            if value == '':
              pass

            else:
              
              html_string += Widget.TextWidget.render(self, field, key, value, REQUEST)
              
              if REQUEST.has_key(relation_item_id):
                relation_item_list = REQUEST.get(relation_item_id)
                
                if relation_item_list != []:
                  # Define default tales on the fly
                  tales_expr = field.tales.get('items', None)
                  defined_tales = 0
                  if not tales_expr:
                    defined_tales = 1
                    from Products.Formulator.TALESField import TALESMethod
                    field.tales['items'] = TALESMethod('REQUEST/relation_item_list')


                  REQUEST['relation_item_list'] = relation_item_list 
                  html_string += '&nbsp;%s&nbsp;' % Widget.ListWidget.render(self, 
                                        field, relation_field_id, None, REQUEST)   
                  REQUEST['relation_item_list'] = None          

                  if defined_tales:
                    # Delete default tales on the fly
                    field.tales['items'] = None

                else:
                  html_string += '&nbsp;<input type="image" src="%s/images/exec16.png" value="update..." name="%s/portal_selections/viewSearchRelatedDocumentDialog%s_%s:method">' \
                    %  (portal_url_string, portal_object.getPath(), field.aq_parent._v_relation_field_index, i)

              html_string += '<br/>'

        else:
          # no modification made, we can display only a lines text area widget
          html_string += Widget.LinesTextAreaWidget.render(self, field, key, value_list, REQUEST)

          html_string += '&nbsp;<input type="image" src="%s/images/exec16.png" value="update..." name="%s/portal_selections/viewSearchRelatedDocumentDialog%s:method">' \
            %  (portal_url_string, portal_object.getPath(), field.aq_parent._v_relation_field_index)

          if value_list not in ((), [], None, ['']) and value_list == field.get_value('default'):
            if REQUEST.get('selection_name') is not None:
              html_string += '&nbsp;&nbsp;<a href="%s?field_id=%s&form_id=%s&selection_name=%s&selection_index=%s"><img src="%s/images/jump.png"></a>' \
                % (field.get_value('jump_method'), field.id, field.aq_parent.id, REQUEST.get('selection_name'), REQUEST.get('selection_index'),portal_url_string)
            else:
              html_string += '&nbsp;&nbsp;<a href="%s?field_id=%s&form_id=%s"><img src="%s/images/jump.png"></a>' \
                % (field.get_value('jump_method'), field.id, field.aq_parent.id,portal_url_string)

        field.aq_parent._v_relation_field_index += 1 # Increase index                
        return html_string

    def render_view(self, field, value):
        """
          Render text field.
        """
        REQUEST = get_request()
        here = REQUEST['here']

        portal_url = getToolByName(here, 'portal_url')
        portal_url_string = portal_url()

        # no modification made, we can display only a lines text area widget
        html_string = Widget.LinesTextAreaWidget.render_view(self, field, value)
        if value not in ((), [], None, ''):
          if REQUEST.get('selection_name') is not None:
            html_string += '&nbsp;&nbsp;<a href="%s?field_id=%s&form_id=%s&selection_name=%s&selection_index=%s"><img src="%s/images/jump.png"></a>' \
              % (field.get_value('jump_method'), field.id, field.aq_parent.id, REQUEST.get('selection_name'), REQUEST.get('selection_index'),portal_url_string)
          else:
            html_string += '&nbsp;&nbsp;<a href="%s?field_id=%s&form_id=%s"><img src="%s/images/jump.png"></a>' \
              % (field.get_value('jump_method'), field.id, field.aq_parent.id,portal_url_string)

        return html_string

class MultiRelationEditor:
    """
      A class holding all values required to update a relation
    """
    def __init__(self, field_id, base_category, portal_type, portal_type_item, key, relation_setter_id, relation_editor_list):

      
      self.field_id = field_id
      self.base_category = base_category
      self.portal_type = portal_type
      self.portal_type_item = portal_type_item
      self.key = key
      self.relation_setter_id = relation_setter_id
      self.relation_editor_list = relation_editor_list


    def __call__(self, REQUEST):
      if self.relation_editor_list != None:
        value_list = []


        for i, value, uid, display_text in self.relation_editor_list:
          value_list.append(value) 
          if uid is not None:
            # Decorate the request so that we can display
            # the select item in a popup
            #relation_field_id = 'relation_%s_%s' % ( self.key, i )      
            #relation_item_id = 'item_%s_%s' % ( self.key, i )      
            relation_field_id = 'relation_field_%s_%s' % ( self.field_id, i )      
            relation_item_id = 'item_field_%s_%s' % ( self.field_id, i )      
            
        
            REQUEST.set(relation_item_id, ((display_text, uid),))
            REQUEST.set(relation_field_id, uid)
            
        #REQUEST.set(self.field_id[len('field_'):], value_list) # XXX Dirty
        REQUEST.set(self.field_id, value_list) # XXX Dirty
      else:
        # Make sure no default value appears
        #REQUEST.set(self.field_id[len('field_'):], None)      
        REQUEST.set(self.field_id, None) # XXX Dirty
        
    def view(self):
      return self.__dict__        
        
    def edit(self, o):    
      if self.relation_editor_list != None:
      
        relation_uid_list = []
        relation_object_list = []
        
        for i, value, uid, display_text in self.relation_editor_list:
          if uid is not None:
            if type(uid) is type('a') and uid.startswith(new_content_prefix):
              # Create a new content
              portal_type = uid[len(new_content_prefix):]
              portal_module = None
              for p_item in self.portal_type_item:
                if p_item[0] == portal_type:
                  portal_module = o.getPortalObject().getDefaultModuleId( p_item[0] )
              if portal_module is not None:              
                portal_module_object = getattr(o.getPortalObject(), portal_module)
                kw ={}
                #kw[self.key] = value
                kw[self.key] = string.join( string.split(value,'%'), '' )
                kw['portal_type'] = portal_type
                kw['immediate_reindex'] = 1
                new_object = portal_module_object.newContent(**kw)
                uid = new_object.getUid()
              else:
                raise             
          relation_uid_list.append(int(uid))

          relation_object_list.append( o.portal_catalog.getObject(uid)  )

        #if relation_uid_list != []:

        # Edit relation        
        if self.relation_setter_id:
          relation_setter = getattr(o, self.relation_setter_id)
          relation_setter((), portal_type=self.portal_type)
          relation_setter( relation_uid_list , portal_type=self.portal_type)         
        else:
#          if relation_uid_list == []:
#            # XXX we could call a generic method which create the setter method name
#            set_method_name = '_set'+convertToUpperCase(self.base_category)
#            getattr(o, set_method_name)( None )
#          else:
#            # XXX we could call a generic method which create the setter method name
#            set_method_name = '_set'+convertToUpperCase(self.base_category)+'ValueList'
#            getattr(o, set_method_name)( relation_object_list )
          o._setValueUids(self.base_category, (), portal_type=self.portal_type)
          o._setValueUids(self.base_category, relation_uid_list, portal_type=self.portal_type)

      else:
        # Nothing to do
        pass
#        # Delete relation        
#        if self.relation_setter_id:
#          relation_setter = getattr(o, self.relation_setter_id)
#          relation_setter((), portal_type=self.portal_type)
#        else:
#          o._setValueUids(self.base_category, (), portal_type=self.portal_type)      

allow_class(MultiRelationEditor)


class MultiRelationStringFieldValidator(Validator.LinesValidator,  RelationField.RelationStringFieldValidator):   
    """
        Validation includes lookup of relared instances
    """    
    message_names = Validator.LinesValidator.message_names + \
                     RelationField.RelationStringFieldValidator.message_names

    # delete double in order to keep a usable ZMI...
    #message_names = dict([(i,0) for i in message_names]).keys() # XXX need to keep order !
    _v_dict = {}
    _v_message_name_list = []
    for message_name in message_names:
      if not _v_dict.has_key(message_name):
        _v_message_name_list.append(message_name)
        _v_dict[message_name] = 1
    message_names = _v_message_name_list
    
    def validate(self, field, key, REQUEST):
      portal_type = map(lambda x:x[0],field.get_value('portal_type'))
      portal_type_item = field.get_value('portal_type')
      base_category = field.get_value( 'base_category')

      # If the value is different, build a query
      portal_selections = getToolByName(field, 'portal_selections')
      portal_catalog = getToolByName(field, 'portal_catalog')      

      # Get the current value
      value_list = Validator.LinesValidator.validate(self, field, key, REQUEST)

#      if type(value_list) == type(''):
#        value_list = [value_list]
      
      # If the value is the same as the current field value, do nothing
      current_value_list = field.get_value('default')
      if type(current_value_list) == type(''):
        current_value_list = [current_value_list]

      catalog_index = field.get_value('catalog_index')
      relation_setter_id = field.get_value('relation_setter_id')

      relation_field_id = 'relation_%s' % ( key )      
      # we must know if user validate the form or click on the wheel button
      relation_uid_list = REQUEST.get(relation_field_id, None)
      if checkSameKeys( value_list, current_value_list ) and (relation_uid_list is None):
        # XXX Will be interpreted by Base_edit as "do nothing"
        #return MultiRelationEditor(field.id, base_category, portal_type, portal_type_item, catalog_index, relation_setter_id, None)
        return None
      
      else:

        relation_field_id = 'relation_%s' % ( key )      

        # We must be able to erase the relation
        if value_list == ['']:
          display_text = 'Delete the relation'
          return MultiRelationEditor(field.id, base_category, portal_type, portal_type_item, catalog_index, relation_setter_id, [])
#          return RelationEditor(key, base_category, portal_type, None, 
#                                portal_type_item, catalog_index, value, relation_setter_id, display_text)
                                # Will be interpreted by Base_edit as "delete relation" (with no uid and value = '')

        if REQUEST.has_key( relation_field_id ):
          # we must know if user validate the form or click on the wheel button
          relation_uid_list = REQUEST.get(relation_field_id, None)
          if relation_uid_list != None:
            relation_editor_list = []
            for i in range( len(relation_uid_list) ):

              relation_item_id = 'item_%s_%s' % ( key, i )      
              relation_uid = relation_uid_list[i]
              
              related_object = portal_catalog.getObject(relation_uid)
              if related_object is not None:
                display_text = str(related_object.getProperty(catalog_index))
              else:
                display_text = 'Object has been deleted'        
              # Check 
              REQUEST.set(relation_item_id, ( (display_text, relation_uid),  ))
              relation_editor_list.append( (i, '', str(relation_uid), display_text) )

            return MultiRelationEditor(field.id, base_category, portal_type, portal_type_item, catalog_index, relation_setter_id, relation_editor_list)
          
      
        else:
          # User validate the form

          relation_editor_list = []
          raising_error_needed = 0
          raising_error_value = ''
          
          # Check all relation
          for i in range( len(value_list) ):
            relation_field_id = 'relation_%s_%s' % ( key, i )      
            relation_item_id = 'item_%s_%s' % ( key, i )      
            
            relation_uid = REQUEST.get(relation_field_id, None)

            value = value_list[i]

            
            # If we get a empty string, delete this line
            if value == '':
              # Clean request if necessary
              if REQUEST.has_key( relation_field_id):
                REQUEST.pop(relation_field_id)

            else:
              # Got a true value

              if relation_uid not in (None, ''):
                # A value has been defined by the user in  popup menu
                if type(relation_uid) in (type([]), type(())): relation_uid = relation_uid[0]
                related_object = portal_catalog.getObject(relation_uid)
                if related_object is not None:
                  display_text = str(related_object.getProperty(catalog_index))
                else:
                  display_text = 'Object has been deleted'        
                # Check 
                REQUEST.set(relation_item_id, ( (display_text, relation_uid),  ))
                relation_editor_list.append( (i, value, str(relation_uid), display_text) )

              else:

                kw ={}
                kw[catalog_index] = value
                kw['portal_type'] = portal_type
                # Get the query results
                relation_list = portal_catalog(**kw)
                relation_uid_list = map(lambda x: x.uid, relation_list)

                # Prepare a menu
                menu_item_list = [('', '')]
                new_object_menu_item_list = []
                for p in portal_type:
                  new_object_menu_item_list += [('New %s' % p, '%s%s' % (new_content_prefix,p))]      

                if len(relation_list) >= MAX_SELECT:        
                  # If the length is long, raise an error
                  # This parameter means we need listbox help
                  REQUEST.set(relation_item_id, [])
                  raising_error_needed = 1
                  raising_error_value = 'relation_result_too_long'

                elif len(relation_list) == 1:
                  # If the length is 1, return uid
                  relation_uid = relation_uid_list[0]
                  related_object = portal_catalog.getObject(relation_uid)
                  if related_object is not None:
                    display_text = str(related_object.getProperty(catalog_index))
                  else:
                    display_text = 'Object has been deleted'        
                    
                  REQUEST.set(relation_item_id, ( (display_text, relation_uid),  ))
                  relation_editor_list.append( (0, value, relation_uid, display_text) )
                  
                elif len(relation_list) == 0:
                  # If the length is 0, raise an error
                  menu_item_list += new_object_menu_item_list 
                  REQUEST.set(relation_item_id, menu_item_list)
                  raising_error_needed = 1
                  raising_error_value = 'relation_result_empty'

                else:
                  # If the length is short, raise an error
                  # len(relation_list) < MAX_SELECT:
                  
                  #menu_item_list += [('-', '')]        
                  menu_item_list += map(lambda x: (x.getObject().getProperty(catalog_index), x.uid), 
                                                                                  relation_list)
                  REQUEST.set(relation_item_id, menu_item_list)
                  raising_error_needed = 1
                  raising_error_value = 'relation_result_ambiguous'
                
          # validate MultiRelation field
          if raising_error_needed:
            # Raise error
            self.raise_error(raising_error_value, field)
            return value_list
          else:
            # Can return editor
            return MultiRelationEditor(field.id, base_category, portal_type, portal_type_item, catalog_index, relation_setter_id, relation_editor_list)



MultiRelationStringFieldWidgetInstance = MultiRelationStringFieldWidget()
MultiRelationStringFieldValidatorInstance = MultiRelationStringFieldValidator()

class MultiRelationStringField(ZMIField):
    meta_type = "MultiRelationStringField"
    is_relation_field = 1

    widget = MultiRelationStringFieldWidgetInstance
    validator = MultiRelationStringFieldValidatorInstance



