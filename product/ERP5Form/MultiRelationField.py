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
from Products.PythonScripts.Utility import allow_class
from Products.ERP5Type.Message import translateString
from AccessControl import ClassSecurityInfo
from Products.Formulator.DummyField import fields
from Products.ERP5Type.Globals import get_request
from cgi import escape
import json

# Max. number of catalog result
MAX_SELECT = 30
NEW_CONTENT_PREFIX = '_newContent_'
# Key for sub listfield
SUB_FIELD_ID = 'relation'
ITEM_ID = 'item'
NO_VALUE = '??? (No Value)'
NBSP = '&nbsp;'

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
                          'container_getter_id', 'context_getter_id',
                          'catalog_index',
                          'relation_setter_id', 'relation_form_id', 'columns',
                          'sort', 'parameter_list','list_method',
                          'first_item', 'items', 'proxy_listbox_ids',
                          'size', 'extra_item',
                          ]

  property_names = (lambda name_list, name_set=set():
    # delete double (but preserve order) in order to keep a usable ZMI...
    [x for x in name_list if not (x in name_set or name_set.add(x))])(
      Widget.LinesTextAreaWidget.property_names +
      Widget.TextWidget.property_names +
      local_property_names)

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
                             required=0)

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

  context_getter_id = fields.StringField('context_getter_id',
                             title='Context Getter Method',
                             description=(
      "The method to call to get the context."),
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

  relation_form_id = fields.StringField('relation_form_id',
                             title='Relation Form',
                             description=(
      "Form to display relation choices"),
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

  proxy_listbox_ids = fields.ListTextAreaField('proxy_listbox_ids',
                               title='Proxy Listbox IDs',
                               description=('A list of listbox that can be used as proxy'),
                               default='',
                               required=0)

  default_widget_rendering_instance = Widget.LinesTextAreaWidgetInstance

  def _getContextValue(self, field, REQUEST):
    """Return result of evaluated method
    defined by context_getter_id or here.
    """
    context_getter_id = field.get_value('context_getter_id')
    here = REQUEST['here']
    if context_getter_id:
      return getattr(here, context_getter_id)()
    return here

  def _generateRenderValueList(self, field, key, value_list, REQUEST):
    if isinstance(value_list, basestring):
      # Value is a string, reformat it correctly
      value_list = value_list.split("\n")
    else:
      # We get a list
      # rather than displaying nothing, display a marker when the
      # property is not set
      # XXX Translate ?
      value_list = [(x or NO_VALUE) for x in value_list]
    generate_subfield_key = field.generate_subfield_key
    need_validation = False
    result_list = []
    for index, value in enumerate(value_list):
      relation_item_list = REQUEST.get(
        generate_subfield_key(
          "%s_%s" % (ITEM_ID, index),
          key=key,
        ),
        None,
      )
      # If we get a empty string, display nothing !
      if value:
        need_validation |= relation_item_list is not None
        result_list.append(
          (
            Widget.TextWidgetInstance,
            generate_subfield_key(
              "%s_%s" % (SUB_FIELD_ID, index),
              key=key,
            ),
            relation_item_list,
            value,
            index,
          ),
        )
    if need_validation:
      return result_list
    return [
      (Widget.LinesTextAreaWidgetInstance, None, [], value_list, None)
    ]

  def render(self, field, key, value, REQUEST, render_prefix=None):
    """
    Render text input field.
    """
    portal = self._getContextValue(field, REQUEST).getPortalObject()
    autocomplete_enabled = getattr(
      portal.portal_skins,
      'erp5_autocompletion_ui',
      None,
    ) is not None
    relation_field_index = REQUEST.get('_v_relation_field_index', 0)
    html_string_list = []
    for (
          widget_instance,
          relation_field_id,
          relation_item_list,
          value_instance,
          sub_index
        ) in self._generateRenderValueList(
          field, key, value, REQUEST,
        ):
      sub_html_string = widget_instance.render(
        field, key, value_instance, REQUEST,
      )
      if autocomplete_enabled:
        sub_html_string += self.render_autocomplete(field, key)
      if relation_item_list is not None:
        if not autocomplete_enabled:
          sub_html_string += self.render_wheel(
            field,
            value_instance,
            REQUEST,
            relation_index=relation_field_index,
            sub_index=sub_index,
          )
        if relation_item_list:
          REQUEST['relation_item_list'] = relation_item_list
          sub_html_string += NBSP + Widget.ListWidgetInstance.render(
            field, relation_field_id, None, REQUEST,
          ) + NBSP
          REQUEST['relation_item_list'] = None
      html_string_list.append(sub_html_string)
    html_string = '<br/>'.join(html_string_list)
    if (value == field.get_value('default')):
      # XXX Default rendering with value...
      relation_html_string = self.render_relation_link(field, value, REQUEST)
      if relation_html_string:
        html_string += NBSP + NBSP + relation_html_string
    REQUEST.set('_v_relation_field_index', relation_field_index + 1)
    return html_string

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """
    Render read only field.
    """
    if (value not in ((), [], None, '')) and field.get_value('allow_jump'):
      if not isinstance(value, (list, tuple)):
        value = value,
      html_string = '<br />'.join(
        '<a class="relationfieldlink" href="%s">%s</a>' % (
          escape(jump_reference.absolute_url()),
          escape(display_value),
        )
        for jump_reference, display_value in zip(
          getattr(
            self._getContextValue(field, REQUEST),
            'get%sValueList' % ''.join(
              part.capitalize()
              for part in field.get_value('base_category').split('_')
            )
          )(
            portal_type=[x[0] for x in field.get_value('portal_type')],
            filter=dict(field.get_value('parameter_list')),
          ),
          value,
        )
      )
    else:
      html_string = self.default_widget_rendering_instance.render_view(
        field,
        value,
        REQUEST=REQUEST,
      )
      if REQUEST is None:
        REQUEST = get_request()
      relation_html_string = self.render_relation_link(field, value, REQUEST)
      if relation_html_string:
        html_string += NBSP + NBSP + relation_html_string
    extra = field.get_value('extra')
    if extra not in (None, ''):
      html_string = "<div %s>%s</div>" % (extra, html_string)
    css_class = field.get_value('css_class')
    if css_class not in ('', None):
      html_string = '<span class="%s">%s</span>' % (
        escape(css_class),
        html_string,
      )
    return html_string

  def render_autocomplete(self, field, key):
    """
    Use jquery-ui autocompletion for all relation fields by default, requiring
    only erp5_autocompletion_ui bt5 to be installed
    """
    # XXX: Allow to specify more parameters to jquery-ui autocomplete widget?
    return """
<script type="text/javascript">
$(document).ready(function() {
  $("input[name='%s']").ERP5Autocomplete({search_portal_type: %s,
                                          search_catalog_key: "%s"});
});
</script>""" % (
      escape(key),
      escape(json.dumps([x[0] for x in field.get_value('portal_type')])),
      escape(field.get_value('catalog_index')),
    )

  def render_wheel(self, field, value, REQUEST, relation_index=0,
                   sub_index=None, render_prefix=None):
    """
    Render wheel used to display a listbox
    """
    here = self._getContextValue(field, REQUEST)
    portal_url = here.getPortalObject().portal_url
    if sub_index is None:
      sub_index_string = ''
    else:
      sub_index_string = '_%s' % sub_index
    return '&nbsp;<input type="image" ' \
      'src="%s/images/exec16.png" alt="update..." ' \
      'name="%s/viewSearchRelatedDocumentDialog%s%s' \
      ':method"/>' % (
      escape(portal_url()),
      escape(portal_url.getRelativeContentURL(here.portal_selections)),
      escape(str(relation_index)),
      escape(sub_index_string),
    )

  def render_relation_link(self, field, value, REQUEST, render_prefix=None):
    """
    Render link to the related object.
    """
    if value not in ((), [], None, '') and field.get_value('allow_jump'):
      # If we this relation field is used as a listbox/matrixbox editable
      # field, then the context of this cell is set in REQUEST. XXX this is not
      # 100% reliable way, maybe we need something to know that the field is
      # beeing rendered as an editable field.
      cell = REQUEST.get('cell')
      here = (
        cell
        if cell is not None else
        self._getContextValue(field, REQUEST)
      )
      # Keep the selection name in the URL
      selection_name = REQUEST.get('selection_name')
      if selection_name is not None:
        selection_name_html = '&amp;selection_name=%s&amp;selection_index=%s' % (
          escape(selection_name),
          escape(str(REQUEST.get('selection_index', 0))),
        )
      else:
        selection_name_html = ''
      ignore_layout = REQUEST.get('ignore_layout')
      if ignore_layout is not None:
        selection_name_html += '&amp;ignore_layout:int=%s' % int(ignore_layout)
      # Generate plan link
      return '<a href="%s/%s?field_id=%s&amp;form_id=%s%s">' \
        '<img src="%s/images/jump.png" alt="jump" />' \
      '</a>' % (
        escape(here.absolute_url()),
        escape(field.get_value('jump_method')),
        escape(field.id),
        escape(field.aq_parent.id),
        escape(selection_name_html),
        escape(here.getPortalObject().portal_url()),
      )
    return ''

class MultiRelationEditor:
    """
      A class holding all values required to update a relation
    """
    def __init__(self, field_id, base_category,
                 portal_type_list,
                 portal_type_item, key, relation_setter_id,
                 relation_editor_list,
                 context_getter_id):
      self.field_id = field_id
      self.base_category = base_category
      self.portal_type_list = portal_type_list
      self.portal_type_item = portal_type_item
      self.key = key
      self.relation_setter_id = relation_setter_id
      self.relation_editor_list = relation_editor_list
      self.context_getter_id = context_getter_id

    def __call__(self, REQUEST):
      if self.relation_editor_list != None:
        value_list = []

        for value, uid, display_text, relation_key, item_key in \
                               self.relation_editor_list:
          value_list.append(display_text)
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

    def edit(self, o):
      if self.relation_editor_list is None:
        return
      if self.context_getter_id:
        o = getattr(o, self.context_getter_id)()
      portal = o.getPortalObject()
      getDefaultModuleValue = portal.getDefaultModuleValue
      getObject = portal.portal_catalog.getObject
      portal_type_set = {x[0] for x in self.portal_type_item}
      relation_object_list = []
      append = relation_object_list.append
      for (
            value, uid, display_text, relation_key, item_key
          ) in self.relation_editor_list:
        if isinstance(uid, basestring) and uid.startswith(NEW_CONTENT_PREFIX):
          portal_type = uid[len(NEW_CONTENT_PREFIX):]
          if portal_type in portal_type_set:
            append(
              getDefaultModuleValue(
                portal_type,
                only_visible=True,
              ).newContent(
                portal_type=portal_type,
                **{
                  self.key: value.replace('%', ''),
                }
              )
            )
        elif uid is not None:
          append(getObject(uid))

      set_method_name = self.relation_setter_id
      set_method_kw = {}
      if not set_method_name:
        # XXX: we could call a generic method which create the setter method name
        set_method_name = 'set%sValueList' % \
          convertToUpperCase(self.base_category)
        set_method_kw['checked_permission'] = 'View'
      getattr(o, set_method_name)(
        relation_object_list,
        portal_type=self.portal_type_list,
        **set_method_kw
      )

allow_class(MultiRelationEditor)

class MultiRelationStringFieldValidator(Validator.LinesValidator):
  """
      Validation includes lookup of relared instances
  """
  message_names = Validator.LinesValidator.message_names +\
                  ['relation_result_too_long', 'relation_result_ambiguous',
                   'relation_result_empty',]

  relation_result_too_long = "Too many documents were found."
  relation_result_ambiguous = "Select appropriate document in the list."
  relation_result_empty = "No such document was found."

  # Relation field variable
  editor = MultiRelationEditor
  default_validator_instance = Validator.LinesValidatorInstance

  # For relation fields, we want to preserve whitespaces by default
  # so that we can search for "  things   "
  whitespace_preserve = fields.CheckBoxField('whitespace_preserve',
                                            title="Preserve whitespace",
                                            description=(
    "Checked if the field preserves whitespace. This means even "
    "just whitespace input is considered to be data."),
                                            default=1)

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
    if isinstance(current_value_list, basestring):
      current_value_list = [current_value_list]
    # Changes in the order or in the number of occurences
    # must be taken into account
    if value_list == current_value_list:
      return []
    if value_list:
      return [
        (
          field.generate_subfield_key(
            "%s_%s" % (SUB_FIELD_ID, index),
            key=key,
          ),
          value,
          field.generate_subfield_key(
            "%s_%s" % (ITEM_ID, index),
            key=key,
          ),
        )
        for index, value in enumerate(value_list)
      ]
    return [
      (
        field.generate_subfield_key(SUB_FIELD_ID, key=key),
        '',
        field.generate_subfield_key(ITEM_ID, key=key),
      )
    ]

  def validate(self, field, key, REQUEST):
    """
    Validate the field.
    """
    raising_error_value = None
    relation_editor_list = []
    catalog_index = field.get_value('catalog_index')
    portal_type_list = [x[0] for x in field.get_value('portal_type')]
    portal = field.getPortalObject()
    portal_catalog = portal.portal_catalog
    relation_uid_list = REQUEST.get(
      field.generate_subfield_key(SUB_FIELD_ID, key=key),
    )
    if relation_uid_list in (None, ''):
      field_value_list = self._generateFieldValueList(
        field,
        key,
        self.default_validator_instance.validate(field, key, REQUEST),
        field.get_value('default'),
      )
      if not field_value_list:
        relation_editor_list = None
      for relation_field_id, value, relation_item_id in field_value_list:
        if value == '':
          for subdict_name in ['form', 'other']:
            getattr(REQUEST, subdict_name).pop(relation_field_id, None)
          relation_editor_list.append(
            (value, None, 'Delete the relation', None, None),
          )
          continue
        relation_uid = REQUEST.get(relation_field_id)
        menu_item_list = []
        if relation_uid in (None, ''):
          kw = dict(field.get_value('parameter_list'))
          kw[catalog_index] = value
          relation_list = portal_catalog(
            portal_type=portal_type_list,
            sort_on=catalog_index,
            **kw
          )
          relation_uid_list = [x.uid for x in relation_list]
          if len(relation_list) >= MAX_SELECT:
            raising_error_value = 'relation_result_too_long'
          elif len(relation_list) == 1:
            relation_uid = relation_uid_list[0]
            related_object = relation_list[0].getObject()
            if related_object is None:
              display_text = 'Object has been deleted'
            else:
              value = display_text = str(
                related_object.getProperty(catalog_index),
              )
            menu_item_list.append((display_text, relation_uid))
            relation_editor_list.append(
              (value, relation_uid, display_text, None, relation_item_id),
            )
          elif relation_list:
            menu_item_list.extend(
              (x.getObject().getProperty(catalog_index), x.uid)
              for x in relation_list
            )
            menu_item_list.append(('', ''))
            raising_error_value = 'relation_result_ambiguous'
          else:
            menu_item_list.append(('', ''))
            if field.get_value('allow_creation'):
              getDefaultModuleValue = portal.getDefaultModuleValue
              for portal_type in portal_type_list:
                try:
                  getDefaultModuleValue(
                    portal_type, default=None, only_visible=True,
                  )
                except ValueError:
                  pass
                else:
                  menu_item_list.append(
                    (
                      translateString(
                        'Add ${portal_type}',
                        mapping={
                          'portal_type': translateString(portal_type),
                        },
                      ),
                      '%s%s' % (NEW_CONTENT_PREFIX, portal_type),
                    )
                  )
            raising_error_value = 'relation_result_empty'
        else:
          if isinstance(relation_uid, (list, tuple)):
            relation_uid = relation_uid[0]
          display_text = 'Object has been deleted'
          if isinstance(relation_uid, basestring) and relation_uid.startswith(
                NEW_CONTENT_PREFIX,
              ):
            display_text = translateString('New ${portal_type}', mapping={
              'portal_type': translateString(
                relation_uid[len(NEW_CONTENT_PREFIX):],
              ),
            })
          elif relation_uid is not None:
            related_object = portal_catalog.getObject(relation_uid)
            if related_object is not None:
              display_text = str(related_object.getProperty(catalog_index))
              if catalog_index == 'title_or_reference':
                display_text = related_object.getTitle()
          menu_item_list.append((display_text, relation_uid))
          relation_editor_list.append(
            (
              value,
              str(relation_uid),
              display_text,
              relation_field_id,
              relation_item_id,
            ),
          )
        REQUEST.set(relation_item_id, menu_item_list)
    else:
      for relation_item_id, relation_uid, value in self._generateItemUidList(
            field, key, relation_uid_list, REQUEST=REQUEST,
          ):
        try:
          related_object = portal_catalog.getObject(relation_uid)
          display_text = str(related_object.getProperty(catalog_index))
          if catalog_index == 'title_or_reference':
            display_text = related_object.getTitle()
        except ValueError:
          if relation_uid.startswith(NEW_CONTENT_PREFIX):
            portal_type = relation_uid[len(NEW_CONTENT_PREFIX):]
            display_text = translateString(
              'New ${portal_type}',
              mapping={
                'portal_type': translateString(portal_type),
              },
            )
          else:
            display_text = 'Object has been deleted'
        if value is None:
          value = display_text
        relation_editor_list.append(
          (value, relation_uid, display_text, None, relation_item_id)
        )

    if raising_error_value:
      self.raise_error(raising_error_value, field)
    return self.editor(
      field.id,
      field.get_value('base_category'),
      portal_type_list,
      field.get_value('portal_type'),
      catalog_index,
      field.get_value('relation_setter_id'),
      relation_editor_list,
      field.get_value('context_getter_id'),
    )

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