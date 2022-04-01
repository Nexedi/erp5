ZMI_OBJECT_CLASS_LIST = ["Skin"]
ERP5_OBJECT_CLASS_LIST = ["Path", "Category", "PortalType", "Module"]
PORTAL_TYPE_OBJECT_LIST = ["PortalTypePropertySheet", "PortalTypeBaseCategory", 
                           "PortalTypeBaseCategory", "PortalTypeAllowedContentType"]
WORKFLOW_OBJECT_CLASS_LIST = ['PortalTypeWorkflowChain']

color_dict = { 'Modified' : '#FDE406', 
               'New' : '#B5FFB5', 
               'Removed' : '#FFA4A4' }
link = 0
request = context.REQUEST
print('<div style="background-color:white;padding:4px">')
for diff_object in context.BusinessTemplate_getDiffObjectList():
  color = color_dict.get(diff_object.object_state, '#FDE406')
  print('<div style="background-color:%s;padding:4px">' % color)
  # XXX This header could be more improved to have icons and more options, like
  # See XML, full diff, unified diff, link to svn (if available).
  print('&nbsp; [<b>%s</b>] [<b>%s</b>] &nbsp;' % (diff_object.object_state,
                                                   diff_object.object_class))

  if diff_object.object_class in ERP5_OBJECT_CLASS_LIST:
    print('<a href="%s">' % (diff_object.object_id))
    link = 1
  elif diff_object.object_class in PORTAL_TYPE_OBJECT_LIST:
    print('<a href="portal_types/%s">' % (diff_object.object_id))
    link = 1
  elif diff_object.object_class in ZMI_OBJECT_CLASS_LIST:
    print('<a href="%s/manage_main">' % (diff_object.object_id))
    link = 1
  elif diff_object.object_class in WORKFLOW_OBJECT_CLASS_LIST:
    print('<a href="portal_workflow/manage_main">')
    link = 1
  print('%s' % (diff_object.object_id))
  if link == 1: 
    print('</a>')
  print('</div>')
  if diff_object.object_state.startswith('Modified'):
    request.set('bt1', diff_object.bt1)
    request.set('bt2', diff_object.bt2)
    request.set('object_id', diff_object.object_id)
    request.set('object_class', diff_object.object_class)
    print(context.portal_templates.diffObjectAsHTML(request))
  print('<hr>')
print('</div>')
return printed
