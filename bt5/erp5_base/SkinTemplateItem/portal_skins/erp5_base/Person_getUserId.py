user_id = context.getUserId()
if user_id is None:
  # BBB: ERP5User-style user ?
  user_id = context.getReference()
return user_id
