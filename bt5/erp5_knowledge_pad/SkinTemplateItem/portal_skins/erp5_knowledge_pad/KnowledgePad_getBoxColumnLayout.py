if real_context is None:
  real_context = context
layout = []
added_box_ids = []
all_box_ids = []
boxes = context.contentValues(portal_type = 'Knowledge Box',
                              checked_permission = 'View')
isAnon = context.portal_membership.isAnonymousUser()
validation_state_map = {1: ('public',),
                        0: ('visible', 'invisible', 'public',)}
boxes = filter(lambda x: x.getValidationState() in validation_state_map[isAnon] and x.test(real_context), boxes)
for box in boxes:
  all_box_ids.append(box.getId())

user_layout = getattr(context, 'user_layout', None)
# read layout from pad
if user_layout is not None:
  sections = user_layout.split('##')
  for section in sections:
    section_layout = []
    boxes = filter(lambda x: x.strip()!='', section.split('|'))
    for box in boxes:
      box_id = box.replace('box_','').replace('_main','')
      ## must exists
      if box_id in all_box_ids:
        section_layout.append(box_id)
        added_box_ids.append(box_id)
    layout.append(section_layout)
else:
  return [all_box_ids]

# add new boxes to first column
for box_id in all_box_ids:
  if not box_id in added_box_ids:
    layout[0].append(box_id)
return layout
