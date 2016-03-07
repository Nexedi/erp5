from Products.PythonScripts.standard import html_quote

if brain.object_state.startswith('Modified'):
  target_object = brain.getObject()
  parent_absolute_path = target_object.aq_parent.absolute_url()
  if hasattr(brain, 'bt1'): # diff two selected business templates
    return html_quote(parent_absolute_path+'/BusinessTemplate_viewObjectsDiff?object_id='+brain.object_id+'&object_class='+brain.object_class+'&bt1='+brain.bt1+'&bt2='+brain.bt2)
  # diff against installed version
  return html_quote(parent_absolute_path+'/BusinessTemplate_viewObjectsDiff?object_id='+brain.object_id+'&object_class='+brain.object_class)
