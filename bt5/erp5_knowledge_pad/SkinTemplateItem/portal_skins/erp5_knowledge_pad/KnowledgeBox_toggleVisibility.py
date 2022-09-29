"""
  This script is called by drag and drop javascript framework
  when user click on 'Minimize' button.
"""
# format to Zope relative URL ('knowledge_pad_module_3_4' -> 'knowledge_pad_module/3/4')
splitted_box_relative_url = box_relative_url.split('_')
box = context.restrictedTraverse('knowledge_pad_module/%s/%s' %(splitted_box_relative_url[-2],
                                                               splitted_box_relative_url[-1]))
state = box.getValidationState()
if state == 'visible':
  box.invisible()
elif state == 'invisible':
  box.visible()
