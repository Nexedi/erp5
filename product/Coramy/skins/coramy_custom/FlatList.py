## Script (Python) "FlatList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id, list_start
##title=
##
request = container.REQUEST
request.set('list_start', int(list_start))

return getattr(context,form_id)(request)
