## Script (Python) "update_http_cache"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=my_folder=None
##title=Updates the caching parameters (cache must be called ht)
##
if my_folder is None: my_folder = container

def updateCache(o):
  o.ZCacheable_setManagerId(manager_id='ht')
  #o.setCacheNamespaceKeys(keys=['__ac_name'])

for o in context.objectValues():
  try:
    updateCache(o)
    print 'Good %s' % o.absolute_url()
  except:
    print 'Bad %s' % o.absolute_url()

for f in context.objectValues(spec=['Base18 Folder','Folder','portal_skins']):
  f.update_http_cache(my_folder=f)

print "Done"

return printed
