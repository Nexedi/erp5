##############################################################################
#
# Copyright (c) 2002, 2004, 2006 Nexedi SARL and Contributors. 
#                                All Rights Reserved.
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
from Products.ERP5Type.Utils import convertToUpperCase
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.Utility import allow_class
from Products.ERP5Type.Message import Message
from AccessControl import ClassSecurityInfo
from types import StringType
from zLOG import LOG
from Products.Formulator.DummyField import fields
from Globals import get_request

# Max. number of catalog result
MAX_SELECT = 30
NEW_CONTENT_PREFIX = '_newContent_'
# Key for sub listfield
SUB_FIELD_ID = 'relation'
ITEM_ID = 'item'
NO_VALUE = '??? (No Value)'

class MultiRelationStringFieldWidget(Widget.LinesTextAreaWidget,
                                     Widget.TextWidget, 
                                     Widget.ListWidget):
  """
  RelationStringField widget
  Works like a string field but includes one buttons
  - one search button which updates the field and sets a relation
  - creates object if not there
  """
  local_property_names = ['update_method', 'jump_method', 'allow_jump', 
                          'base_category', 'portal_type', 'allow_creation', 
                          'container_getter_id', 'catalog_index',
                          'relation_setter_id', 'columns', 'sort',
                          'parameter_list','list_method',
                          'first_item', 'items', 'size', 'extra_item',
                          ]

  property_names = Widget.LinesTextAreaWidget.property_names + \
                   Widget.TextWidget.property_names + \
                   local_property_names
    
  # XXX Field to remove...
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

  allow_jump = fields.CheckBoxField('allow_jump',
                             title='Allow Jump',
                             description=(
      "Do we allow to jump to the relation ?"),
                             default=1,
                             required=0)

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

  allow_creation = fields.CheckBoxField('allow_creation',
                             title='Allow Creation',
                             description=(
      "Do we allow to create new objects ?"),
                             default=1,
                             required=0)

  container_getter_id = fields.StringField('container_getter_id',
                             title='Container Getter Method',
                             description=(
      "The method to call to get a container object."),
                             default="",
                             required=0)

  catalog_index = fields.StringField('catalog_index',
                             title='Catalog Index',
                             description=(
      "The method to call to set the relation. Required."),
                             default="",
                             required=1)

  # XXX Is it a good idea to keep such a field ??
  # User can redefine setter method with a script (and so, don't use the API)
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

  sort = fields.ListTextAreaField('sort',
                               title='Default Sort',
                               description=('The default sort keys and order'),
                               default=[],
                               required=0)

  parameter_list = fields.ListTextAreaField('parameter_list',
                               title="Parameter List",
                               description=(
      "A list of paramters used for the portal_catalog."),
                               default=[],
                               required=0)

  list_method = fields.MethodField('list_method',
                               title='List Method',
                               description=('The method to use to list'
                                            'objects'),
                               default='',
                               required=0)

  # delete double in order to keep a usable ZMI...
  # XXX need to keep order !
  #property_names = dict([(i,0) for i in property_names]).keys() 
  _v_dict = {}
  _v_property_name_list = []
  for property_name in property_names:
    if not _v_dict.has_key(property_name):
      _v_property_name_list.append(property_name)
      _v_dict[property_name] = 1
  property_names = _v_property_name_list

  default_widget_rendering_instance = Widget.LinesTextAreaWidgetInstance

  def _generateRenderValueList(self, field, key, value_list, REQUEST):
    result_list = []
    need_validation = 0
    ####################################
    # Check value
    ####################################
    if isinstance(value_list, StringType):
      # Value is a string, reformat it correctly
      value_list = value_list.split("\n")
    else:
      # We get a list
      # rather than displaying nothing, display a marker when the
      # property is not set
      # XXX Translate ?
      value_list = [(x or NO_VALUE) for x in value_list]
    # Check all relation
    for i in range(len(value_list)):
      ###################################
      # Sub field
      ###################################
      relation_field_id = field.generate_subfield_key("%s_%s" % \
                                                      (SUB_FIELD_ID, i),
                                                      key=key)
      relation_item_id = field.generate_subfield_key("%s_%s" % \
                                                     (ITEM_ID, i),
                                                     key=key)
      relation_item_list = REQUEST.get(relation_item_id, None)
      value = value_list[i]
      if (relation_item_list is not None) and \
         (value != ''):
        need_validation = 1
      # If we get a empty string, display nothing !
      if value != '':
        result_list.append((Widget.TextWidgetInstance, relation_field_id, 
                            relation_item_list, value, i))
    if not need_validation:
      ###################################
      # Main field
      ###################################
      result_list = [(Widget.LinesTextAreaWidgetInstance, None, [], 
                      value_list, None)]
    return result_list

  def render(self, field, key, value, REQUEST):
    """
    Render text input field.
    """
    html_string = ''
    relation_field_index = REQUEST.get('_v_relation_field_index', 0)
    render_parameter_list = self._generateRenderValueList(
                                            field, key, value,
                                            REQUEST)
    ####################################
    # Render subfield
    ####################################
    html_string_list = []
    for widget_instance, relation_field_id, relation_item_list, \
                            value_instance, sub_index in render_parameter_list:
      sub_html_string = widget_instance.render(field, key, 
                                               value_instance, REQUEST)
      if relation_item_list is not None:
        if relation_item_list != []:
          ####################################
          # Render listfield
          ####################################

          REQUEST['relation_item_list'] = relation_item_list
          sub_html_string += '&nbsp;%s&nbsp;' % \
                                Widget.ListWidgetInstance.render(
                                field, relation_field_id, None, REQUEST)
          REQUEST['relation_item_list'] = None


        else:
          ####################################
          # Render wheel
          ####################################
          sub_html_string += self.render_wheel(
                    field, value_instance, REQUEST, 
                    relation_index=relation_field_index,
                    sub_index=sub_index)
      html_string_list.append(sub_html_string)  
    ####################################
    # Generate html
    ####################################
    html_string = '<br/>'.join(html_string_list)
    ####################################
    # Render jump
    ####################################
    if (value == field.get_value('default')):
      # XXX Default rendering with value...
      relation_html_string = self.render_relation_link(field, value, 
                                                       REQUEST)
      if relation_html_string != '':
        html_string += '&nbsp;&nbsp;%s' % relation_html_string
    ####################################
    # Update relation field index
    ####################################
    REQUEST.set('_v_relation_field_index', relation_field_index + 1) 
    return html_string

  def render_view(self, field, value):
    """
    Render read only field.

    XXX Improved rendering required
    """
    html_string = self.default_widget_rendering_instance.render_view(
                                                      field, value)
    REQUEST = get_request()
    relation_html_string = self.render_relation_link(field, value, REQUEST)
    if relation_html_string != '':
      html_string += '&nbsp;&nbsp;%s' % relation_html_string
    return html_string

  def render_wheel(self, field, value, REQUEST, relation_index=0,
                   sub_index=None):
    """
    Render wheel used to display a listbox
    """
    here = REQUEST['here']
    portal_url = getToolByName(here, 'portal_url')
    portal_url_string = portal_url()
    portal_object = portal_url.getPortalObject()
    portal_selections_url_string = here.portal_selections.absolute_url_path()
    if sub_index is None:
      sub_index_string = ''
    else:
      sub_index_string = '_%s' % sub_index
    return '&nbsp;<input type="image" ' \
         'src="%s/images/exec16.png" value="update..." ' \
         'name="%s/viewSearchRelatedDocumentDialog%s%s' \
         ':method"/>' % \
           (portal_url_string, portal_selections_url_string,
           relation_index, sub_index_string)

  def render_relation_link(self, field, value, REQUEST):
    """
    Render link to the related object.
    """
    html_string = ''
    here = REQUEST['here']
    portal_url = getToolByName(here, 'portal_url')
    portal_url_string = portal_url()
    portal_object = portal_url.getPortalObject()
    if (value not in ((), [], None, '')) and \
       (field.get_value('allow_jump') == 1):
      # Keep the selection name in the URL
      if REQUEST.get('selection_name') is not None:
        selection_name_html = '&amp;selection_name=%s&amp;selection_index=%s' % \
              (REQUEST.get('selection_name'), REQUEST.get('selection_index'))
      else:
        selection_name_html = ''
      # Generate plan link
      html_string += '<a href="%s/%s?field_id=%s&amp;form_id=%s%s">' \
                       '<img src="%s/images/jump.png" />' \
                     '</a>' % \
                (here.absolute_url(), 
                 field.get_value('jump_method'), 
                 field.id, field.aq_parent.id,
                 selection_name_html,
                 portal_url_string)
    return html_string

class MultiRelationEditor:
    """
      A class holding all values required to update a relation
    """
    def __init__(self, field_id, base_category, 
                 portal_type_list, 
                 portal_type_item, key, relation_setter_id, 
                 relation_editor_list):
      self.field_id = field_id
      self.base_category = base_category
      self.portal_type_list = portal_type_list
      self.portal_type_item = portal_type_item
      self.key = key
      self.relation_setter_id = relation_setter_id
      self.relation_editor_list = relation_editor_list

    def __call__(self, REQUEST):
      if self.relation_editor_list != None:
        value_list = []

        for value, uid, display_text, relation_key, item_key in \
                               self.relation_editor_list:
          value_list.append(value)
          if uid is not None:
            # Decorate the request so that we can display
            # the select item in a popup
            # XXX To be unified
            relation_field_id = relation_key
            relation_item_id = item_key
            REQUEST.set(relation_item_id, ((display_text, uid),))
        REQUEST.set(self.field_id, value_list) # XXX Dirty
      else:
        # Make sure no default value appears
        REQUEST.set(self.field_id, None) # XXX Dirty

    def view(self):
      return self.__dict__

    def edit(self, o):
      if self.relation_editor_list != None:

        relation_uid_list = []
        relation_object_list = []
        for value, uid, display_text, relation_key, item_key in \
                               self.relation_editor_list:
          if uid is not None:
            if isinstance(uid, StringType) and \
               uid.startswith(NEW_CONTENT_PREFIX):
              # Create a new content
              portal_type = uid[len(NEW_CONTENT_PREFIX):]
              portal_module = None
              for p_item in self.portal_type_item:
                if p_item[0] == portal_type:
                  portal_module = o.getPortalObject().getDefaultModuleId(
                                                            p_item[0])
              if portal_module is not None:
                portal_module_object = getattr(o.getPortalObject(), 
                                               portal_module)
                kw ={}
                kw[self.key] = value.replace('%', '')
                kw['portal_type'] = portal_type
                kw['immediate_reindex'] = 1
                new_object = portal_module_object.newContent(**kw)
                uid = new_object.getUid()
              else:
                raise
              
            relation_uid_list.append(int(uid))
            relation_object_list.append( o.portal_catalog.getObject(uid))

        # Edit relation
        if self.relation_setter_id:
          relation_setter = getattr(o, self.relation_setter_id)
          relation_setter((), portal_type=self.portal_type_list)
          relation_setter(relation_uid_list,                  # relation setter is uid based
                          portal_type=self.portal_type_list)  # maybe not the best solution
                                                              # and inconsistent with bellow
        else:
          # we could call a generic method which create the setter method name
          if len(relation_object_list) == 1:
            set_method_name = '_set%sValue' % \
                         convertToUpperCase(self.base_category)
            getattr(o, set_method_name)(relation_object_list[0],
                                        portal_type=self.portal_type_list)
          else:
            set_method_name = '_set%sValueList' % \
                         convertToUpperCase(self.base_category)
            getattr(o, set_method_name)(relation_object_list,
                                        portal_type=self.portal_type_list)

allow_class(MultiRelationEditor)

class MultiRelationStringFieldValidator(Validator.LinesValidator):
  """
      Validation includes lookup of relared instances
  """
  message_names = Validator.LinesValidator.message_names +\
                  ['relation_result_too_long', 'relation_result_ambiguous', 
                   'relation_result_empty',]

  # XXX Do we need to translate here ?
  relation_result_too_long = "Too many documents were found."
  relation_result_ambiguous = "Select appropriate document in the list."
  relation_result_empty = "No such document was found."

  # Relation field variable
  editor = MultiRelationEditor
  default_validator_instance = Validator.LinesValidatorInstance

  def _generateItemUidList(self, field, key, relation_uid_list, REQUEST=None):
    """
    Generate tuple...
    """
    result_list = []
    for i in range(len(relation_uid_list)):
      # Generate a Item id for each value.
      relation_item_id = field.generate_subfield_key("%s_%s" % \
                                                     (ITEM_ID, i),
                                                     key=key)
      relation_uid = relation_uid_list[i]
      result_list.append((relation_item_id, relation_uid, None))
    return result_list

  def _generateFieldValueList(self, field, key, 
                              value_list, current_value_list):
    """
    Generate list of value, item_key
    """
    item_value_list = []
    if isinstance(current_value_list, StringType):
      current_value_list = [current_value_list]
    # Check value list
    if value_list != current_value_list: # Changes in the order or in the number of occurences
                                         # must be taken into account
      for i in range(len(value_list)):
        value = value_list[i]
        relation_field_id = field.generate_subfield_key("%s_%s" % \
                                                        (SUB_FIELD_ID, i),
                                                        key=key)
        relation_item_id = field.generate_subfield_key("%s_%s" % \
                                                       (ITEM_ID, i),
                                                       key=key)
        item_value_list.append((relation_field_id, value, relation_item_id))
      # Make possible to delete the content of the field.
      if item_value_list == []:
        relation_field_id = field.generate_subfield_key("%s" % \
                                                      SUB_FIELD_ID, key=key)
        relation_item_key = field.generate_subfield_key(ITEM_ID, key=key)
        item_value_list.append((relation_field_id, '', relation_item_key))
    return item_value_list

  def validate(self, field, key, REQUEST):
    """
    Validate the field.
    """
    raising_error_needed = 0
    relation_editor_list = None
    # Get some tool
    catalog_index = field.get_value('catalog_index')
    portal_type_list = [x[0] for x in field.get_value('portal_type')]
    portal_catalog = getToolByName(field, 'portal_catalog')

    ####################################
    # Check list input
    ####################################
    relation_field_id = field.generate_subfield_key("%s" % \
                                                    SUB_FIELD_ID, key=key)
    relation_uid_list = REQUEST.get(relation_field_id, None)

    ####################################
    # User clicked on the wheel
    ####################################
    need_to_revalidate = 1
    if relation_uid_list not in (None, ''):
      need_to_revalidate = 0
      relation_editor_list = []
      for relation_item_id, relation_uid, value in \
                  self._generateItemUidList(field, key, relation_uid_list,
                                            REQUEST=REQUEST):
        found = 0
        try:
          related_object = portal_catalog.getObject(relation_uid)
          display_text = str(related_object.getProperty(catalog_index))
          found = 1
        except ValueError:
          # Catch the error raised when the uid is a string
          if relation_uid.startswith(NEW_CONTENT_PREFIX):
            ##############################
            # New content was selected, but the 
            # form is not validated
            ##############################
            portal_type = relation_uid[len(NEW_CONTENT_PREFIX):]
            translated_portal_type = Message(domain='erp5_ui',
                                             message=portal_type)
            # XXX Replace New by Add
            message = Message(
                    domain='erp5_ui', message='New ${portal_type}',
                    mapping={'portal_type': translated_portal_type})
            display_text = message
          else:
            display_text = 'Object has been deleted'

        ################################
        # Modify if user modified his value
        ################################
        # XXX Does not work when user select a value in a ListField
#         if (found == 1) and \
#            (value != display_text):
#           relation_editor_list = None
#           need_to_revalidate = 1
#           REQUEST.set(relation_field_id, None)
#           break
        if value is None:
          value = display_text
        # Storing display_text as value is needed in this case
        relation_editor_list.append((value, 
                                     relation_uid, display_text,
                                     None, relation_item_id))
#                                      str(relation_uid), display_text,
    ####################################
    # User validate the form
    ####################################
    if need_to_revalidate == 1:
#     else:
      ####################################
      # Check the default field
      ####################################
      value_list = self.default_validator_instance.validate(field, 
                                                       key, REQUEST)
      # If the value is the same as the current field value, do nothing
      current_value_list = field.get_value('default')
      field_value_list = self._generateFieldValueList(field, key, value_list,
                                                    current_value_list)
      if len(field_value_list) != 0:
        ####################################
        # Values were changed
        ####################################
        relation_editor_list = []
        for relation_field_id, value, relation_item_id in field_value_list:
          if value == '':
            ####################################
            # User want to delete this line
            ####################################
            # Clean request if necessary
            if REQUEST.has_key(relation_field_id):
              for subdict_name in ['form', 'other']:
                subdict = getattr(REQUEST, subdict_name)
                if subdict.has_key(relation_field_id):
                  subdict.pop(relation_field_id)
            display_text = 'Delete the relation'
            relation_editor_list.append((value, None, 
                                     display_text, None, None))
            # XXX RelationField implementation
#         # We must be able to erase the relation
#         display_text = 'Delete the relation'
#         # Will be interpreted by Base_edit as "delete relation" 
#         # (with no uid and value = '')
#         relation_editor_list = [(value, None, 
#                                      display_text, None, None)]
          else:
            relation_uid = REQUEST.get(relation_field_id, None)
#             need_to_revalidate = 1
            if relation_uid not in (None, ''):
#               need_to_revalidate = 0
#               found = 0
              ####################################
              # User selected in a popup menu
              ####################################
              if isinstance(relation_uid, (list, tuple)):
                relation_uid = relation_uid[0]
              try:
                related_object = portal_catalog.getObject(relation_uid)
              except ValueError:
                # Catch the exception raised when the uid is a string
                related_object = None
              if related_object is not None:
                display_text = str(related_object.getProperty(catalog_index))
#                 found = 1
              else:
                ##############################
                # New content was selected, but the 
                # form is not validated
                ##############################
                if relation_uid.startswith(NEW_CONTENT_PREFIX):
                  ##############################
                  # New content was selected, but the 
                  # form is not validated
                  ##############################
                  portal_type = relation_uid[len(NEW_CONTENT_PREFIX):]
                  translated_portal_type = Message(domain='erp5_ui',
                                                   message=portal_type)
                  message = Message(
                          domain='erp5_ui', message='New ${portal_type}',
                          mapping={'portal_type': translated_portal_type})
                  display_text = message
                else:
                  display_text = 'Object has been deleted'
#               ################################
#               # Modify if user modified his value
#               ################################
#               if (found == 1) and \
#                  (value != display_text):
#                 REQUEST.set(relation_field_id, None)
#                 need_to_revalidate = 1
#               else:
#                 # Check
#                 REQUEST.set(relation_item_id, ((display_text, relation_uid),))
#                 relation_editor_list.append((value, str(relation_uid), 
#                                             display_text, relation_field_id,
#                                             relation_item_id))
              REQUEST.set(relation_item_id, ((display_text, relation_uid),))
              relation_editor_list.append((value, str(relation_uid), 
                                          display_text, relation_field_id,
                                          relation_item_id))
#             if need_to_revalidate == 1:
            else:
              ####################################
              # User validate the form for this line
              ####################################
              kw ={}
              kw[catalog_index] = value
              kw['portal_type'] = portal_type_list
              kw['sort_on'] = catalog_index
              parameter_list = field.get_value('parameter_list')
              if len(parameter_list) > 0:
                for k,v in parameter_list:
                  kw[k] = v
              # Get the query results
              relation_list = portal_catalog(**kw)
              relation_uid_list = [x.uid for x in relation_list]
              menu_item_list = []
              if len(relation_list) >= MAX_SELECT:
                # If the length is long, raise an error
                # This parameter means we need listbox help
                # XXX XXX XXX Do we need to delete it ?
                REQUEST.set(relation_item_id, [])
                raising_error_needed = 1
                raising_error_value = 'relation_result_too_long'
              elif len(relation_list) == 1:
                # If the length is 1, return uid
                relation_uid = relation_uid_list[0]
                related_object = relation_list[0].getObject()
                if related_object is not None:
                  display_text = str(related_object.getProperty(catalog_index))
                  # Modify the value, in order to let the user 
                  # modify it later...
                  value = display_text
                else:
                  display_text = 'Object has been deleted'
                # XXX XXX XXX
                REQUEST.set(relation_item_id, ((display_text, 
                                                relation_uid),))
                relation_editor_list.append((value, relation_uid, 
                                             display_text, None,
                                             relation_item_id))
#                 relation_editor_list.append((0, value, relation_uid, 
#                                              display_text, None, None))
              elif len(relation_list) == 0:
                # Add blank line
                menu_item_list.append(('', ''))
                # If the length is 0, raise an error
                if field.get_value('allow_creation') == 1 :
                  # XXX
                  for portal_type in portal_type_list:
                    translated_portal_type = Message(domain='erp5_ui',
                                                     message=portal_type)
                    message = Message(
                            domain='erp5_ui', message='New ${portal_type}',
                            mapping={'portal_type': translated_portal_type})
                    menu_item_list.append((message, 
                                           '%s%s' % (NEW_CONTENT_PREFIX, 
                                                     portal_type)))
                REQUEST.set(relation_item_id, menu_item_list)
                raising_error_needed = 1
                raising_error_value = 'relation_result_empty'
              else:
                # If the length is short, raise an error
                # len(relation_list) < MAX_SELECT:
                menu_item_list.extend([(
                                  x.getObject().getProperty(catalog_index),
                                  x.uid) for x in relation_list])
                # Add blank line
                menu_item_list.append(('', ''))
                REQUEST.set(relation_item_id, menu_item_list)
                raising_error_needed = 1
                raising_error_value = 'relation_result_ambiguous'

    ##################################### 
    # Validate MultiRelation field
    ##################################### 
    if raising_error_needed:
      # Raise error
      self.raise_error(raising_error_value, field)
      return value_list
    else:
      # Can return editor
      base_category = field.get_value('base_category')
      portal_type_item = field.get_value('portal_type')
      relation_setter_id = field.get_value('relation_setter_id')
      return self.editor(field.id, 
                         base_category,
                         portal_type_list, 
                         portal_type_item, catalog_index, 
                         relation_setter_id, relation_editor_list)

MultiRelationStringFieldWidgetInstance = MultiRelationStringFieldWidget()
MultiRelationStringFieldValidatorInstance = MultiRelationStringFieldValidator()

class MultiRelationStringField(ZMIField):
  meta_type = "MultiRelationStringField"
  security = ClassSecurityInfo()

  widget = MultiRelationStringFieldWidgetInstance
  validator = MultiRelationStringFieldValidatorInstance

  security.declareProtected('Access contents information', 'get_orig_value')
  def get_orig_value(self, id):
    """
    Get value for id; don't do any override calculation.
    """
    if id in ('is_relation_field', 'is_multi_relation_field'):
      result = 1
    else:
      result = ZMIField.get_orig_value(self, id)
    return result

  security.declareProtected('Access contents information', 'get_value')
  def get_value(self, id, REQUEST=None, **kw):
    """Get value for id.

    Optionally pass keyword arguments that get passed to TALES
    expression.
    """
    if (id == 'items') and (REQUEST is not None):
      # relation_item_list is not editable for the RelationField
      result = REQUEST.get('relation_item_list', None)
    else:
      result = ZMIField.get_value(self, id, REQUEST=REQUEST, **kw)
    return result

# Register get_value
from Products.ERP5Form.ProxyField import registerOriginalGetValueClassAndArgument
registerOriginalGetValueClassAndArgument(MultiRelationStringField, 'items')
