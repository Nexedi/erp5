import json

form = context.REQUEST.form
portal = context.getPortalObject()

login = form.get("login_name")
if context.acl_users.searchUsers(login=login, exact_match=True):
  return json.dumps(None)

person = portal.person_module.newContent(portal_type="Person")
person.edit(first_name=form.get("firstname"),
            last_name=form.get("lastname"),
            email_text=form.get("email"),
            password=form.get("password"),
            reference=login,
)

assignment = person.newContent(portal_type='Assignment')
assignment.setFunction("ung_user")
assignment.open()

person.validate()

return json.dumps(True)
