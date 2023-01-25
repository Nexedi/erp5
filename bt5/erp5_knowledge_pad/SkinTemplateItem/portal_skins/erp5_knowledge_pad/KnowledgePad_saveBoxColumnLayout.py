"""
  Save desired user box layout to current knowledge pad.
  This script is called by drag and drop framework when user
  drags and/or drops a knowledge box to a column.
"""
if not context.portal_membership.isAnonymousUser():
  box_url = None
  new_user_layout = []
  for item in user_layout.split('##'):
    if item != '':
      l = []
      sub_items=item.split('|')
      # get box relative url
      splitted_box_url = sub_items[0].split('_')
      box_url='knowledge_pad_module/%s/%s' %(splitted_box_url[-2], splitted_box_url[-1])
      # remove box_relative_url from layout string
      for sub_item in sub_items:
        knowledge_box = sub_item.split('_')[-1]
        l.append(knowledge_box)
      # join boxes
      new_user_layout.append('|'.join(l))
    else:
      new_user_layout.append(item)
  # parent is part of layout element
  knowledge_pad = context.restrictedTraverse(box_url).getParentValue()
  # join columns
  new_user_layout = '##'.join(new_user_layout)
  #  update only if necessary
  if getattr(knowledge_pad, 'user_layout', None)!=new_user_layout:
    knowledge_pad.edit(user_layout=new_user_layout)
