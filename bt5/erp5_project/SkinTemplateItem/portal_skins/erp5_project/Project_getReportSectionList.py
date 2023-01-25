from Products.ERP5Form.Report import ReportSection

result = []

params = {}

for project_line in [x.getObject() for x in context.searchFolder(sort_id='int_index')]:

  result.append(
                 ReportSection(path=project_line.getPhysicalPath(),
                               form_id='ProjectLine_viewReport',
                               selection_name='project_line_selection',
                               selection_params=params,
                               #listbox_display_mode='ReportTreeMode',

                               )
               )


return result
