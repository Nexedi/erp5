from __future__ import print_function
actions_to_add = [
  {'name' : 'Immobilisation Validity Errors',
   'id':     'immobilisation_validity_errors',
   'action' : 'Immobilisation_viewValidityErrors',
   'condition': 'object/Immobilisation_isInvalid',
   'permission': ('View',),
   'category': 'object_view',
   'visible':1
  },
]


print('Adding Immobilisation Item Actions to Portal Type %s :' % context.getId())
action_list = context.listActions()
for action_to_add in actions_to_add:
  print("- Adding Action '%s (%s)'... " % (action_to_add['id'],action_to_add['name']), end=' ')
  found = 0
  for action in action_list:
    if getattr(action, 'id', None) == action_to_add['id']:
      print('already exists')
      found = 1
  if not found:
    context.addAction(**action_to_add)
    print("OK")

print()
return printed
