"""
  Delete Box from Pad.
  This script is called by drag and drop javascript framework
  when user click on 'Close' button.
"""
splitted_box_url = box_relative_url.split('_')
box_relative_url = 'knowledge_pad_module/%s/%s'  %(splitted_box_url[-2], splitted_box_url[-1])
box = context.restrictedTraverse(box_relative_url)
box.delete()
