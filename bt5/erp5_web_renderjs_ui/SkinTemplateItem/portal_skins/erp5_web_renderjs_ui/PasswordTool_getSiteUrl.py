base_url = context.REQUEST.get("url") or context.absolute_url()
return "%s/WebSite_viewResetPassword" % base_url
