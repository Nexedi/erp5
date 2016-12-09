kwargs = state_change['kwargs']
person = state_change['object']

if not person.hasUserId():
  person.edit(user_id=kwargs['reference'])
person.newContent(
  portal_type='ERP5 Login',
  password=kwargs['password'],
  reference=kwargs['reference']).validate()
