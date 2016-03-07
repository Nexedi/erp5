'''this script overide the existing form login_form 
and redirect to the customize login page'''

request = context.REQUEST
portal = context.getPortalObject()
N_ = portal.Base_translateString

module_url = portal.web_site_module.ecitizen.absolute_url()
form_id = 'view'

msg = ""
if request.get('came_from', None) is not None:
   msg = "%s. %s" % (N_("You don't have enough permissions to access this page"), N_("You can log in with another user name"))
return context.Base_redirect('%s/%s' % (module_url, form_id), keep_items = {'portal_status_message' : msg})
