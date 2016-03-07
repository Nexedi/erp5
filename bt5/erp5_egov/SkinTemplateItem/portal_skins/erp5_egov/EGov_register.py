request=context.REQUEST


# check captcha
if not context.isCaptchaTextCorrect(captcha_text):
  message = "text entered at the right of the picture is wrong"
  translated_message = context.Base_translateString(message)
  return request['RESPONSE'].redirect(
             "%s/view?portal_status_message=%s" %
             (context.absolute_url(), translated_message))

web_site_url = context.getWebSiteValue().absolute_url()

portal_type = request.get('portal_type','')

if portal_type == '': 
  return request['RESPONSE'].redirect(web_site_url) 

 
# create a new anonymous procedure
module = context.getDefaultModule(portal_type=portal_type)
form = module.newContent(portal_type=portal_type)

module_id = module.getId()
new_object_id = form.getId()

redirect_url = "%s/%s/%s" % (web_site_url, module_id, new_object_id)

# set a login on the new form
form.setReference(new_object_id)

# set a password
password = context.Person_generatePassword()
form.setPassword(password)

# the ownership is the form itself
form.manage_addLocalRoles(new_object_id, ['Owner','Agent'])


# login with this new form
# set in the request wich module is used for this annonymous application
# this is use in PAS
redirect_url = '%s/logged_in?__ac_name=%s&__ac_password=%s&anonymous_module=%s' % (redirect_url, new_object_id, password, module.getId())

result = request['RESPONSE'].redirect(redirect_url) 
return result
