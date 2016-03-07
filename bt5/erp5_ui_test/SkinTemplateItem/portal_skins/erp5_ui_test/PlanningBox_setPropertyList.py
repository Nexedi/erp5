"""
Used in selenium test in order to change the properties of Planning box
"""

d = dict(
  field_title = 'Foo_viewPlanningBox',
  field_description = '',
  field_css_class = '',
  field_default = '',
  field_alternate_name = '',
  field_hidden = '',
  field_js_enabled = 'checked',
  field_vertical_view = vertical_view,
  field_report_axis_groups = '10' ,
  field_size_border_width_left = '10' ,
  field_size_planning_width = '800'   ,
  field_size_y_axis_space = '10'   ,
  field_size_y_axis_width = '200'   ,
  field_use_date_zoom = 'checked'   ,
  field_size_header_height =  '20'  ,
  field_size_planning_height = '800'  ,
  field_size_x_axis_space = '10'   ,
  field_size_x_axis_height = '50'   ,
  field_y_axis_position = ''   ,
  field_x_axis_position = ''   ,
  field_report_root_list = """parent | parent
foo_domain | foo_domain"""   ,
  field_selection_name = 'planning_0'   ,
  field_portal_types = """Foo Line""",
  field_sort = 'id'   ,
  field_list_method = 'searchFolder'   ,
  field_second_layer_list_method = ''   ,
  field_title_line = 'getTitle'   ,
  field_x_start_bloc = 'start_date'   ,
  field_x_stop_bloc = 'stop_date'   ,
  field_y_size_block = height_method   ,
  field_stat_method = '' ,
  field_split_method = '' ,
  field_color_script = '' ,
  field_round_script = '' ,
  field_lane_root_list="""base_day_domain | Day
base_week_domain | Week
base_month_domain | Month
base_year_domain | Year
""",
  field_info_center = 'getTitle'   ,
  field_info_topleft = 'getTitle'   ,
  field_info_topright = 'getTitle'   ,
  field_info_botleft = 'getTitle'   ,
  field_info_botright = 'getTitle'   ,
  field_info_tooltip = 'getTitle'  ,
  field_enabled = 'checked',
  field_editable = 'checked',
  field_page_template = '',
  field_external_validator = '',
  field_required = '',
  field_whitespace_preserve = '',
)

d.update(context.REQUEST)
d.update(kw)
#context.log('PlanningBox_setPropertyList', 'kw = %r, d = %r' % (kw, d,))
r = context.form.validate(d)
context.manage_edit_xmlrpc(r)

return 'Set Successfully.'
