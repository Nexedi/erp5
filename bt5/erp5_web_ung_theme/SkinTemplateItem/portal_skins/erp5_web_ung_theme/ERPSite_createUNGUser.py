import json

form = context.REQUEST.form
portal = context.getPortalObject()

if len(portal.portal_catalog(portal_type="Person",
                             reference=form.get("login_name"))):
  return json.dumps(None)

person = portal.person_module.newContent(portal_type="Person")
person.edit(first_name=form.get("firstname"),
            last_name=form.get("lastname"),
            email_text=form.get("email"),
            password=form.get("password"),
            reference=form.get("login_name"))

assignment = person.newContent(portal_type='Assignment')
assignment.setFunction("ung_user")
assignment.open()

person.validate()

return json.dumps(True)
