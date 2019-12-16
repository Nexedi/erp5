alpha = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
new_password = ''.join([random.choice(alpha) for _ in range(10)])

person_module = context.getPortalObject().person_module
user_id = "user_a_test"
person = getattr(person_module, user_id, None)
if person:
  if person.getReference() != user_id:
    person.setReference(user_id)
else:
  person = person_module.newContent(portal_type="Person",
                                    reference=user_id,
                                    id=user_id,
                                    default_email_text="userA@example.invalid")
  assignment = person.newContent(portal_type='Assignment')
  assignment.open()
  login = person.newContent(
    portal_type='ERP5 Login',
    reference=user_id,
    password=new_password,
  )
  login.validate()

# Make sure always a new password
person.setPassword(new_password)
return "OK"
