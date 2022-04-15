##############################################################################
#
# Copyright (c) 2002, 2006 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from AccessControl.ZopeGuards import guarded_getattr
from ZODB.POSException import ConflictError
from zLOG import LOG, WARNING
from Products.Formulator.DummyField import fields
from Products.Formulator import Widget, Validator
from Products.Formulator.Errors import FormValidationError, ValidationError
from Products.Formulator.Field import ZMIField
from Products.ERP5Type.Message import translateString


class MatrixBoxWidget(Widget.Widget):
    """
    An UI widget which displays a matrix

    Don't forget that you can use tales expressions for every field, so this
    is really usefull if you want to use fonctions
    instead of predefined variables.

    A function is provided to

    - access a cell

    - modify a cell

    """
    property_names = Widget.Widget.property_names +\
                     ['cell_base_id', 'cell_portal_type', 'lines', 'columns',
                      'tabs', 'as_cell_range_script_id', 'getter_method',
                      'editable_attributes', 'global_attributes',
                      'cell_getter_method', 'update_cell_range', 'url_cells' ]

    default = fields.TextAreaField('default',
                                   title='Default',
                                   description=(
        "Default value of the text in the widget."),
                                   default="",
                                   width=20, height=3,
                                   required=0)

    as_cell_range_script_id = fields.StringField('as_cell_range_script_id',
                                 title='Cell range method',
                                 description=(
        "Method returning columns, lines and tabs. The method is passed"
        " matrixbox=True, base_id=base_id as arguments."),
                                 default='',
                                 required=0)
    columns = fields.ListTextAreaField('columns',
                                 title="Columns",
                                 description=(
      "This defines columns of the matrixbox. "
      "This should be a list of couples, "
      "couple[0] is the variation, and couple[1] is the name displayed "
      "to the user.\n"
      "For example (('color/blue', 'Bleu'), ('color/red','Red')).\n"
      " Deprecated, use cell range method instead"),
                                 default=[],
                                 required=0)

    lines = fields.ListTextAreaField('lines',
                                 title="Lines",
                                 description=(
      "This defines lines of the matrixbox. This should be a list of couples, "
      "couple[0] is the variation, and couple[1] is the name displayed "
      "to the user.\n"
      "For example (('size/baby/02','baby/02'),('size/baby/03','baby/03')).\n"
      "Deprecated, use cell range method instead"),
                                 default=[],
                                 required=0)

    tabs = fields.ListTextAreaField('tabs',
                                 title="Tabs",
                                 description=(
      "This defines tabs. You can use it with the same way as Lines "
      "and Columns.\n"
      "This is used only if you have more than 2 kinds of variations.\n"
      "Deprecated, use cell range method instead"),
                                 default=[],
                                 required=0)

    # XXX ListTextAreaField ?
    cell_range = fields.ListTextAreaField('cell_range',
                                           title="Cell Range",
                                           description=(
                "This defines the range of the matrix."),
                                           default=[],
                                           required=0)
    getter_method = fields.StringField('getter_method',
                                 title='Getter method',
                                 description=(
        "You can specify a specific method in order to retrieve the context. "
        "This field can be empty, if so the MatrixBox will use the default "
        "context."),

                                 default='',
                                 required=0)

    cell_getter_method = fields.StringField('cell_getter_method',
                                 title='Cell Getter method',
                                 description=(
        "You can specify a method in order to retrieve cells. This field can "
        "be empty, if so the MatrixBox will use the default method : getCell."
       ),
                                 default='',
                                 required=0)

    new_cell_method = fields.MethodField('new_cell_method',
                                 title='New Cell method',
                                 description=(
        "You can specify a specific method in order to create cells. "
        "This field can be empty, if so the MatrixBox will use the default "
        "method : newCell."),

                                 default='',
                                 required=0)

    editable_attributes = fields.ListTextAreaField('editable_attributes',
                                 title="Editable Properties",
                                 description=(
        "A list of attributes which are set by hidden fields called "
        "matrixbox_attribute_name. This is used "
        "when we want to specify a computed value for each cell"),
                                 default=[],
                                 required=0)

    global_attributes = fields.ListTextAreaField('global_attributes',
                                 title="Global Properties",
                                 description=(
        "An optional list of globals attributes which are set by hidden "
        "fields and which are applied to each cell. "
        "This is used if we want to set the same value for every cell"),
                                 default=[],
                                 required=0)

    cell_base_id = fields.StringField('cell_base_id',
                                 title='Base id for cells',
                                 description=(
        "The Base id for cells : this is the name used to store cells, "
        "we usually use names like : 'movement', 'path', ... "),
                                 default='cell',
                                 required=0)

    cell_portal_type = fields.StringField('cell_portal_type',
                                 title='Portal Type for cells',
                                 description=(
        "The Portal Type for cells : This is the portal type used to "
        "create a new cell."),
                                 default='Mapped Value',
                                 required=0)

    update_cell_range = fields.CheckBoxField('update_cell_range',
                                  title="Update Cell Range",
                                  description=(
        "The cell range should be updated upon edit."),
                                  default=0)

    url_cells = fields.ListTextAreaField('url_cells',
                                 title="URL Cells",
                                 description=(
        "An optional list of cells which can provide a custom URL."
        "If no url cell is used, then no link is displayed."),
                                 default=[],
                                 required=0)

    def render(self, field, key, value, REQUEST, render_format='html', render_prefix=None):
        """
          This is where most things happen. This method renders a list
          of items
        """
        # First grasp the variables we may need
        here = REQUEST['here']
        form = field.aq_parent
        field_title = field.get_value('title')
        cell_base_id = field.get_value('cell_base_id')
        context = here
        getter_method_id = field.get_value('getter_method')
        if getter_method_id not in (None,''):
          context = getattr(here,getter_method_id)()
        if context is None:
          return ''
        as_cell_range_script_id = field.get_value('as_cell_range_script_id')
        extra_dimension_category_list_list = [None]
        if as_cell_range_script_id:
          lines = []
          columns = []
          tabs = []
          dimension_list = guarded_getattr(context,
              as_cell_range_script_id)(matrixbox=True, base_id=cell_base_id)
          len_dimension_list = len(dimension_list)
          if len_dimension_list:
            if len_dimension_list == 1:
              lines, = dimension_list
            elif len_dimension_list == 2:
              lines, columns = dimension_list
            elif len_dimension_list >= 3:
              lines, columns, tabs = dimension_list[:3]
              if len_dimension_list > 3:
                extra_dimension_list = dimension_list[3:]

                extra_dimension_category_label_dict = {}
                extra_dimension_category_index_dict = {}
                for extra_dimension in extra_dimension_list:
                  for index, (category, label) in enumerate(extra_dimension):
                    extra_dimension_category_label_dict[category] = label
                    extra_dimension_category_index_dict[category] = index
                from Products.ERP5Type.Utils import cartesianProduct
                extra_dimension_category_list_list = cartesianProduct(
                    [[category for category, label in extra_dimension] for extra_dimension in extra_dimension_list])
        else:
          lines = field.get_value('lines')
          columns = field.get_value('columns')
          tabs = field.get_value('tabs')
        field_errors = REQUEST.get('field_errors', {})
        cell_getter_method_id = field.get_value('cell_getter_method')
        if cell_getter_method_id not in (None, ''):
          cell_getter_method = getattr(context, cell_getter_method_id)
        else:
          cell_getter_method = context.getCell
        editable_attributes = field.get_value('editable_attributes')
        url_cells = field.get_value('url_cells')
        url_cell_dict = dict(url_cells)

        # This is required when we have no tabs
        if len(tabs) == 0:
          tabs = [(None,None)]
        # This is required when we have no columns
        if len(columns) == 0:
          columns = [(None,None)]

        column_ids = [x[0] for x in columns]
        line_ids = [x[0] for x in lines]
        tab_ids = [x[0] for x in tabs]
        editable_attribute_ids = [x[0] for x in editable_attributes]

        # THIS MUST BE REMOVED - WHY IS THIS BAD ?
        # IT IS BAD BECAUSE TAB_IDS DO NOT DEFINE A RANGE....
        # here.setCellRange(line_ids, column_ids, base_id=cell_base_id)

        # result for the list render
        list_result = []

        url = REQUEST.URL

        list_html = ''

        for extra_dimension_category_list in extra_dimension_category_list_list:
          if extra_dimension_category_list is None:
            extra_dimension_label = ''
            extra_dimension_position = ()
            extra_dimension_index = ''
            extra_dimension_category_list = []
          else:
            extra_dimension_label = ','+','.join([extra_dimension_category_label_dict[category]
                                                  for category in extra_dimension_category_list])
            extra_dimension_position = tuple([extra_dimension_category_index_dict[category]
                                              for category in extra_dimension_category_list])
            extra_dimension_index = '_'+'_'.join(map(str, extra_dimension_position))
          # Create one table per tab
          k = 0
          kwd = dict(base_id=cell_base_id)
          for tab in tabs:
            tab_id = tab[0]
            if (tab_id is not None) and \
               (not isinstance(tab_id, (list, tuple))):
              tab_id = [tab_id]

            if render_format == 'list':
              list_result_tab = [[tab[1]]]

            # Create the header of the table - this should probably become DTML
            first_tab = tab[1] or ''
            header = """\
    <!-- Matrix Content -->
    <div class="matrixbox_label_tab">%s</div>
    <div class="MatrixContent">
     <table>
    """ % (first_tab+extra_dimension_label)

            # Create the footer. This should be replaced by DTML
            # And work as some kind of parameter
            footer = """\
       <tr>
        <td colspan="%i"
            class="Data footer">
        </td>
       </tr>
      </table>
     </div>
    """ % (len(columns) + 1)

            list_header = """\
    <tr class="matrixbox_label_line"><td class=\"Data\"></td>
    """

            for cname in columns:
              first_column = cname[1] or ''
              list_header = list_header + ("<td class=\"Data\">%s</td>\n" %
                                             first_column)
              if render_format == 'list':
                list_result_tab[0].append(cname[1])

            list_header = list_header + "</tr>"

            # Build Lines
            i = 0
            j = 0
            list_body = ''
            for l in lines:

              if not i % 2:
                td_css = 'DataA'
              else:
                td_css = 'DataB'
              list_body = list_body + '\n<tr class=\"%s\"><td class=\"matrixbox_label_column\">%s</td>' % (td_css, str(l[1]))
              j = 0

              if render_format == 'list':
                list_result_lines = [ str(l[1]) ]

              for c in columns:
                has_error = False
                column_id = c[0]
                if (column_id is not None) and \
                   (not isinstance(column_id, (list, tuple))):
                  column_id = [column_id]
                if column_id is None:
                  kw = [l[0]]
                elif tab_id is None:
                  kw = [l[0], c[0]]
                else:
                  kw = [l[0], c[0]] + tab_id + extra_dimension_category_list
                cell = cell_getter_method(*kw, **kwd)
                REQUEST['cell'] = cell
                REQUEST['cell_index'] = kw

                cell_body = ''
                cell_url = None

                for attribute_id in editable_attribute_ids:
                  if attribute_id in url_cell_dict:
                    url_method_id = url_cell_dict[attribute_id]
                    if url_method_id not in (None, ''):
                      url_method = getattr(cell, url_method_id, None)
                      if url_method is not None:
                        try:
                          cell_url = url_method(brain=cell,
                                                cell_index=kw,
                                                cell_position=((i,j,k) + extra_dimension_position))
                        except (ConflictError, RuntimeError):
                          raise
                        except:
                          LOG('MatrixBox', WARNING, 'Could not evaluate the url '
                              'method %r with %r' % (url_method, cell),
                              error=True)
                      else:
                        LOG('MatrixBox', WARNING,
                            'Could not find the url method %s' % (url_method_id,))

                  my_field_id = '%s_%s' % (field.id, attribute_id)
                  if form.has_field(my_field_id):
                    my_field = form.get_field(my_field_id)
                    key = my_field.id + '_cell_%s_%s_%s%s' % (i,j,k,extra_dimension_index)
                    default_value = my_field.get_value(
                      'default', cell=cell, cell_index=kw, cell_position=((i,j,k)+extra_dimension_position))
                    display_value = default_value
                    if field_errors:
                      # Display previous value in case of any error in this form because
                      # we have no cell to get value from
                      display_value = REQUEST.get('field_%s' % key, default_value)

                    if cell is not None:
                      if render_format=='html':
                        cell_html = my_field.render(value=display_value,
                                              REQUEST=REQUEST,
                                              key=key)
                        if cell_url:
                          # don't make a link if widget is editable
                          if not my_field.get_value('editable',
                             cell=cell, cell_index=kw,
                             cell_position=((i,j,k)+extra_dimension_position)):
                            cell_html = "<a href='%s'>%s</a>" % (cell_url,
                                                                 cell_html)
                        if key in field_errors:
                          # Display error message if this cell has an error
                          has_error = True
                          cell_body += '<span class="input">%s</span>%s' % (
                              cell_html, translateString(field_errors[key].error_text))
                        else:
                          cell_body += '<span class="input">%s</span>' % (
                                          cell_html )
                    else:
                      if render_format == 'html':
                        if key in field_errors:
                          # Display error message if this cell has an error
                          has_error = True
                          cell_body += '<span class="input">%s</span>%s' % (
                              my_field.render(value=display_value,
                                              REQUEST=REQUEST,
                                              key=key),
                              translateString(field_errors[key].error_text))
                        else:
                          cell_body += '<span class="input">%s</span>' %\
                                           my_field.render(
                                              value=display_value,
                                              REQUEST=REQUEST,
                                              key=key)

                    if render_format == 'list':
                      # list rendering doesn't make difference when cell exists or not
                      list_result_lines.append({
                        'default': default_value,
                        'value': display_value,
                        'key': key,
                        'type': my_field.meta_type if my_field.meta_type != "ProxyField" else my_field.getRecursiveTemplateField().meta_type,
                        'field_id': my_field.id,
                        'error_text': u"%s" % (translateString(field_errors[key].error_text) if key in field_errors else '')
                      })

                css = td_css
                if has_error:
                  css = 'error'
                list_body = list_body + \
                      ('<td class=\"%s\">%s</td>' % (css, cell_body))
                j += 1

              list_body = list_body + '</tr>'
              i += 1

              if render_format == 'list':
                list_result_tab.append(list_result_lines)

            list_html += header + list_header + \
                    list_body + footer
            k += 1

            if render_format == 'list':
              list_result.append(list_result_tab)

        # XXX Does not leave garbage in REQUEST['cell'], because some other
        # fields also use that key...
        REQUEST.other.pop('cell', None)
        REQUEST.other.pop('cell_index', None)

        if render_format == 'list':
          return list_result

        return list_html

MatrixBoxWidgetInstance = MatrixBoxWidget()

class MatrixBoxValidator(Validator.Validator):
    property_names = Validator.Validator.property_names

    def validate(self, field, key, REQUEST):
        form = field.aq_parent
        # We need to know where we get the getter from
        # This is coppied from ERP5 Form
        here = getattr(form, 'aq_parent', REQUEST)
        cell_base_id = field.get_value('cell_base_id')
        as_cell_range_script_id = field.get_value('as_cell_range_script_id')
        context = here
        getter_method_id = field.get_value('getter_method')
        if getter_method_id not in (None,''):
          context = getattr(here,getter_method_id)()
          if context is None:
            return {}
        extra_dimension_category_list_list = [None]
        if as_cell_range_script_id:
          lines = []
          columns = []
          tabs = []
          dimension_list = guarded_getattr(context,
              as_cell_range_script_id)(matrixbox=True, base_id=cell_base_id)
          len_dimension_list = len(dimension_list)
          if len_dimension_list:
            if len_dimension_list == 1:
              lines, = dimension_list
            elif len_dimension_list == 2:
              lines, columns = dimension_list
            elif len_dimension_list >= 3:
              lines, columns, tabs = dimension_list[:3]
              if len_dimension_list > 3:
                extra_dimension_list = dimension_list[3:]

                extra_dimension_category_label_dict = {}
                extra_dimension_category_index_dict = {}
                for extra_dimension in extra_dimension_list:
                  for index, (category, label) in enumerate(extra_dimension):
                    extra_dimension_category_label_dict[category] = label
                    extra_dimension_category_index_dict[category] = index
                from Products.ERP5Type.Utils import cartesianProduct
                extra_dimension_category_list_list = cartesianProduct(
                    [[category for category, label in extra_dimension] for extra_dimension in extra_dimension_list])
        else:
          lines = field.get_value('lines')
          columns = field.get_value('columns')
          tabs = field.get_value('tabs')

        editable_attributes = field.get_value('editable_attributes')
        error_list = []
        cell_getter_method_id = field.get_value('cell_getter_method')
        if cell_getter_method_id not in (None, ''):
          cell_getter_method = getattr(context, cell_getter_method_id)
        else:
          cell_getter_method = context.getCell

        # This is required when we have no tabs
        if len(tabs) == 0: tabs = [(None,None)]
        # This is required when we have no columns
        if len(columns) == 0: columns = [(None,None)]

        # XXX Copy/Paste from render...
        column_ids = [x[0] for x in columns]
        line_ids = [x[0] for x in lines]
        tab_ids = [x[0] for x in tabs]
        editable_attribute_ids = [x[0] for x in editable_attributes]

        result = {}
        for extra_dimension_category_list in extra_dimension_category_list_list:
          if extra_dimension_category_list is None:
            extra_dimension_label = ''
            extra_dimension_position = ()
            extra_dimension_index = ''
            extra_dimension_category_list = []
          else:
            extra_dimension_label = ','+','.join([extra_dimension_category_label_dict[category]
                                                  for category in extra_dimension_category_list])
            extra_dimension_position = tuple([extra_dimension_category_index_dict[category]
                                              for category in extra_dimension_category_list])
            extra_dimension_index = '_'+'_'.join(map(str, extra_dimension_position))
          k = 0
          # Create one table per tab
          kwd = dict(base_id=cell_base_id)
          for tab_id in tab_ids:
            if (tab_id is not None) and \
               (not isinstance(tab_id, (list, tuple))):
              tab_id = [tab_id]

            i = 0
            j = 0
            for l in line_ids:
              j = 0
              for c in column_ids:
                if c is None:
                  kw = [l]
                elif tab_id is None:
                  kw = [l, c]
                else:
                  kw = [l, c] + tab_id + extra_dimension_category_list
                kw = tuple(kw)
                cell = cell_getter_method(*kw, **kwd)

                for attribute_id in editable_attribute_ids:

                  my_field_id = '%s_%s' % (field.id, attribute_id)
                  if form.has_field(my_field_id):
                    my_field = form.get_field(my_field_id)
                    if my_field.get_value('editable'):
                      key = 'field_' + my_field.id + '_cell_%s_%s_%s%s' % (i,j,k,extra_dimension_index)
                      attribute_value = my_field.get_value('default',
                          cell=cell, cell_index=kw, cell_position = ((i,j,k)+extra_dimension_position))
                      value = None
                      try :
                        # We call directly Validator's validate method to pass our own key
                        # because Field.validate always computes the key from field properties
                        value = my_field.validator.validate(my_field, key, REQUEST)
                        # Unfortunately the call to external validator is implemented within
                        # field's `validate` method. Since we call the validator's validate
                        # directly, we need to copy&paste call to external validator from Field's validate here
                        external_validator = my_field.get_value('external_validator')
                        if external_validator and not external_validator(value, REQUEST):
                            my_field.validator.raise_error('external_validator_failed', my_field)
                      except ValidationError as err :
                        err.field_id = my_field.id + '_cell_%s_%s_%s%s' % (i,j,k,extra_dimension_index)
                        error_list.append(err)

                      if (attribute_value != value or \
                          attribute_value not in ('',None,(),[])) \
                          and not my_field.get_value('hidden'):
                        # Only validate modified values from visible fields
                        result.setdefault(kw, {})[attribute_id] = value
                      elif kw in result:
                        result[kw][attribute_id] = value
                j += 1
              i += 1
            k += 1
        if len(error_list):
          raise FormValidationError(error_list, {})
        return result

MatrixBoxValidatorInstance = MatrixBoxValidator()

class MatrixBox(ZMIField):
    meta_type = "MatrixBox"

    widget = MatrixBoxWidgetInstance
    validator = MatrixBoxValidatorInstance

    security = ClassSecurityInfo()

    security.declareProtected('Access contents information', 'get_value')
    def get_value(self, id, **kw):
      if id == 'default':
        render_format = kw.get('render_format')
        if render_format == 'list':
          request = kw.get('REQUEST')
          if request is None:
            request = get_request()
          field = kw.get('field', self) # for proxy field
          return self.widget.render(field, self.generate_field_key(), None,
                                    request,
                                    render_format=render_format,
                                    render_prefix=kw.get('render_prefix'))
      else:
        return ZMIField.get_value(self, id, **kw)

# Psyco
from Products.ERP5Type.PsycoWrapper import psyco
psyco.bind(MatrixBoxWidget.render)
psyco.bind(MatrixBoxValidator.validate)
