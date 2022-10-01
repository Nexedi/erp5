actions_to_add = [
  {'name' : 'Immobilisation Periods',
   'id':     'immobilisation_periods',
   'action' : 'Item_viewImmobilisationPeriods',
   'condition': '',
   'permission': ('View',),
   'category': 'object_view',
   'visible':1
  },
  {'name' : 'Jump to Related Amortisation Transactions',
   'id':     'jump_amortisation_transaction',
   'action' : 'Item_jumpToAmortisationTransaction',
   'condition': '',
   'permission': ('View',),
   'category': 'object_jump',
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
