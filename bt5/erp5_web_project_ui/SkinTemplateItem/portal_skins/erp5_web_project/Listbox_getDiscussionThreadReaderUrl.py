context.log("brain:")
context.log(kw['brain'].getObject())
context.log(kw['brain'].getObject().getRelativeUrl())
discussion_thread = kw['brain'].getObject()

key = discussion_thread.getRelativeUrl()
portal_absolute_url = context.getPortalObject().absolute_url()
return '%s/%s' % (portal_absolute_url, key)


form_id = 'My_viewForm'
redirect_url = '%s/%s' % (discussion_thread.absolute_url(), form_id)
return redirect_url
