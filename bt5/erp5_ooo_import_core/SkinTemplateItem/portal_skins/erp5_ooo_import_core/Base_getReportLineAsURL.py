url = context.getPortalObject().absolute_url()

url = '%s/%s/view' % (url, brain.object_url)

return url
