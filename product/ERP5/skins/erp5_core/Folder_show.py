## Script (Python) "Folder_show"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=selection_name
##title=
##
request = context.REQUEST
context.portal_selections.setSelectionToAll(selection_name, REQUEST=request)
url = context.portal_selections.getSelectionListUrlFor(selection_name, REQUEST=request)

request.RESPONSE.redirect(url)
