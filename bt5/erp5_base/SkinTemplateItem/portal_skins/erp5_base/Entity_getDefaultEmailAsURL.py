email = context.getDefaultEmailValue()
if email is not None:
  return email.asURL()
