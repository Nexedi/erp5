request=context.REQUEST
portal = context.getPortalObject()

# get module url
absolute_url = portal.web_site_module.ecitizen.absolute_url()

redirect_url = absolute_url

result = request['RESPONSE'].redirect(redirect_url) 
return result
