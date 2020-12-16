import random
translateString = context.Base_translateString
person =  context.ERP5Site_getAuthenticatedMemberPersonValue()


if person is None:
  msg = translateString("You can only request points after login.")
  return context.getWebSiteValue().Base_redirect("login_form",
            keep_items={"portal_status_message": msg,
                        "come_from": context.getWebSectionValue().absolute_url()})


if not len(person.contentValues(portal_type="Loyalty Account")):
  new_id = context.portal_ids.generateNewLengthId(
                     id_group="Loyalty_Account",
                     default=1)
  reference = "LA-%s-%s" % (new_id, random.randint(100000,1000000))
  person.newContent(portal_type="Loyalty Account",
                    title="Default",
                    reference=reference)
  msg = translateString("your Loyalty program is now enable")
  return context.Base_redirect("", keep_items={"portal_status_message": msg})
