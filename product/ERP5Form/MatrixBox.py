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
from Products.Formulator.DummyField import fields
from Products.Formulator import Widget, Validator
from Products.Formulator.Errors import FormValidationError, ValidationError
from Products.Formulator.Field import ZMIField
from Products.ERP5Type.Message import Message

def N_(message, **kw):
  return Message('erp5_ui', message, **kw)

class MatrixBoxWidget(Widget.Widget):
    """
    An UI widget which displays a matrix

    A MatrixBoxWidget should be called 'matrixbox', if you don't do so, then
    you may have some errors, 
    or some strange problems, you have been Warned !!!!

    Don't forget that you can use tales expressions for every field, so this
    is really usefull if you want to use fonctions 
    instead of predefined variables.

    A function is provided to

    - access a cell

    - modify a cell

    """
    property_names = Widget.Widget.property_names +\
                     ['cell_base_id', 'cell_portal_type',
                      'lines', 'columns', 'tabs', 'getter_method' ,
                      'editable_attributes' , 'global_attributes',
                      'update_cell_range'
                       ]

    default = fields.TextAreaField('default',
                                   title='Default',
                                   description=(
        "Default value of the text in the widget."),
                                   default="",
                                   width=20, height=3,
                                   required=0)

    columns = fields.ListTextAreaField('columns',
                                 title="Columns",
                                 description=(
      """This defines columnes of the matrixbox. 
      This should be a list of couples, 
      couple[0] is the variation, and couple[1] is the name displayed 
      to the user.
      For example (('color/bleu','bleu'),('color/red','red')),
      Deprecated"""),
                                 default=[],
                                 required=0)

    lines = fields.ListTextAreaField('lines',
                                 title="Lines",
                                 description=(
      """This defines lines of the matrixbox. This should be a list of couples,
      couple[0] is the variation, and couple[1] is the name displayed 
      to the user.
      For example (('size/baby/02','baby/02'),('size/baby/03','baby/03')), 
      Deprecated"""),
                                 default=[],
                                 required=0)

    tabs = fields.ListTextAreaField('tabs',
                                 title="Tabs",
                                 description=(
      """This defines tabs. You can use it with the same way as Lines 
      and Columns,
      This is used only if you have more than 2 kinds of variations. 
      Deprecated"""),
                                 default=[],
                                 required=0)

    # XXX ListTextAreaField ?
    cell_range = fields.ListTextAreaField('cell_range',
                                           title="Cell Range",
                                           description=(
                """
                This defines the range of the matrix.
                """),
                                           default=[],
                                           required=0)
    getter_method = fields.StringField('getter_method',
                                 title='Getter method',
                                 description=("""
        You can specify a specific method in order to retrieve the context.
        This field can be empty, if so the MatrixBox will use the default 
        context."""),

                                 default='',
                                 required=0)

    new_cell_method = fields.MethodField('new_cell_method',
                                 title='New Cell method',
                                 description=("""
        You can specify a specific method in order to create cells.
        This field can be empty, if so the MatrixBox will use the default 
        method :
        newCell."""),

                                 default='',
                                 required=0)

    editable_attributes = fields.ListTextAreaField('editable_attributes',
                                 title="Editable Properties",
                                 description=(
        """A list of attributes which are set by hidden fields called 
        matrixbox_attribute_name. This is used
        when we want to specify a value calculated for each cell"""),
                                 default=[],
                                 required=0)

    global_attributes = fields.ListTextAreaField('global_attributes',
                                 title="Global Properties",
                                 description=(
        """An optional list of globals attributes which are set by hidden 
        fields and which are applied to each cell. 
        This is used if we want to set the same value for every cell"""),
                                 default=[],
                                 required=0)

    cell_base_id = fields.StringField('cell_base_id',
                                 title='Base id for cells',
                                 description=("""
        The Base id for cells : this is the name used to store cells, 
        we usually,
        use names like : 'mouvement','path', ...."""),
                                 default='cell',
                                 required=0)

    cell_portal_type = fields.StringField('cell_portal_type',
                                 title='Portal Type for cells',
                                 description=("""
        The Portal Type for cells : This is the portal type used to 
        construct a new cell."""),
                                 default='Mapped Value',
                                 required=0)

    update_cell_range = fields.CheckBoxField('update_cell_range',
                                  title="Update Cell Range",
                                  description=(
        "The cell range should be updated upon edit."),
                                  default=0)

    def render(self, field, key, value, REQUEST, render_format='html'):
        """
          This is where most things happen. This method renders a list
          of items
        """
        # First grasp the variables we may need
        here = REQUEST['here']
        form = field.aq_parent
        field_title = field.get_value('title')
        cell_base_id = field.get_value('cell_base_id')
        lines = field.get_value('lines')
        columns = field.get_value('columns')
        tabs = field.get_value('tabs')
        field_errors = REQUEST.get('field_errors', {})
        context = here
        getter_method_id = field.get_value('getter_method')
        if getter_method_id not in (None,''):
          context = getattr(here,getter_method_id)()
        if context is None:
          return ''
        cell_getter_method = context.getCell
        editable_attributes = field.get_value('editable_attributes')

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
        k = 0

        # Create one table per tab
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
  %s<br>
  <div class="ListContent">
   <table cellpadding="0" cellspacing="0" border="0">
  """ % first_tab

          # Create the footer. This should be replaced by DTML
          # And work as some kind of parameter
          footer = """\
        </div>
       </td>
      </div>
     </tr>
     <tr>
      <td colspan="%s" width="100" align="center" valign="middle"
          class="Data">
      </td>
     </tr>
    </table>
   </div>
  """ % len(columns)

          list_header = """\
  <tr><td class=\"Data\"></td>
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
            list_body = list_body + '\n<tr class=\"%s\"><td class=\"%s\">%s</td>' % (td_css, td_css, str(l[1]))
            j = 0
            
            if render_format == 'list':
              list_result_lines = [ str(l[1]) ]

            for c in columns:
              has_error = 0
              column_id = c[0]
              if (column_id is not None) and \
                 (not isinstance(column_id, (list, tuple))):
                column_id = [column_id]
              if column_id is None:
                kw = [l[0]]
              elif tab_id is None:
                kw = [l[0], c[0]]
              else:
                kw = [l[0], c[0]] + tab_id
              kwd = {}
              kwd['base_id'] = cell_base_id
              cell = cell_getter_method(*kw, **kwd)

              cell_body = ''

              for attribute_id in editable_attribute_ids:
                my_field_id = '%s_%s' % (field.id, attribute_id)
                if form.has_field(my_field_id):
                  my_field = form.get_field(my_field_id)
                  key = my_field.id + '_cell_%s_%s_%s' % (i,j,k)
                  if cell != None:
                    attribute_value = my_field.get_value('default',
                           cell=cell, cell_index=kw, cell_position = (i,j,k))
                  
                    if render_format=='html':
                      REQUEST['cell'] = cell
                      display_value = attribute_value

                      if field_errors.has_key(key):
                        # Display previous value (in case of error)
                        display_value = REQUEST.get('field_%s' % key,
                                                  attribute_value)
                        has_error = 1
                        cell_body += "%s<br/>%s" % (
                            my_field.render(value=display_value,
                                            REQUEST=REQUEST,
                                            key=key),
                            N_(field_errors[key].error_text))
                      else:
                        cell_body += str(my_field.render(
                                            value=attribute_value,
                                            REQUEST=REQUEST,
                                            key=key))

                    elif render_format == 'list':
                      if not my_field.get_value('hidden'):
                        list_result_lines.append(attribute_value)

                  else:
                    if my_field.get_value('hidden'):
                      attribute_value = my_field.get_value('default',
                            cell_index=kw, cell_position=(i,j,k))
                    else :
                      attribute_value = my_field.get_orig_value('default')
                    if render_format == 'html':
                      REQUEST['cell'] = None
                      cell_body += str(my_field.render(value=attribute_value,
                                      REQUEST=REQUEST, key=key))
                    elif render_format == 'list':
                      list_result_lines.append(None)

              css = td_css
              if has_error :
                css = td_css + 'Error'
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
        lines = field.get_value('lines')
        columns = field.get_value('columns')
        tabs = field.get_value('tabs')
        editable_attributes = field.get_value('editable_attributes')
        getter_method_id = field.get_value('getter_method')
        error_list = []
        context = here
        if getter_method_id not in (None,''):
          context = getattr(here,getter_method_id)()
          if context is None: return {}
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

        k = 0
        result = {}
        # Create one table per tab
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
                kw = [l, c] + tab_id
              kw = tuple(kw)
              kwd = {}
              kwd['base_id'] = cell_base_id
              cell = cell_getter_method(*kw, **kwd)

              for attribute_id in editable_attribute_ids:

                my_field_id = '%s_%s' % (field.id, attribute_id)
                if form.has_field(my_field_id):
                  my_field = form.get_field(my_field_id)
                  if my_field.get_value('editable'):
                    key = 'field_' + my_field.id + '_cell_%s_%s_%s' % (i,j,k)
                    attribute_value = my_field.get_value('default',
                        cell=cell, cell_index=kw, cell_position = (i,j,k))
                    try :
                      value = my_field.validator.validate(
                                      my_field, key, REQUEST)
                    except ValidationError, err :
                      err.field_id = my_field.id + '_cell_%s_%s_%s' % (i,j,k)
                      error_list.append(err)

                    if (attribute_value != value or \
                        attribute_value not in ('',None,(),[])) \
                        and not my_field.get_value('hidden'):
                      # Only validate modified values from visible fields
                      result.setdefault(kw, {})
                      result[kw][attribute_id] = value
                    else:
                      if result.has_key(kw):
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
      if id=='default' and kw.get('render_format') in ('list', ):
        return self.widget.render(self, self.generate_field_key(), None, 
                                  kw.get('REQUEST'), 
                                  render_format=kw.get('render_format'))
      else:
        return ZMIField.get_value(self, id, **kw)

# Psyco
from Products.ERP5Type.PsycoWrapper import psyco
psyco.bind(MatrixBoxWidget.render)
psyco.bind(MatrixBoxValidator.validate)

# Register get_value
from Products.ERP5Form.ProxyField import registerOriginalGetValueClassAndArgument
registerOriginalGetValueClassAndArgument(MatrixBox, 'default')
