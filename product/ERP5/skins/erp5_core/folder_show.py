##parameters=selection_name


request = context.REQUEST
context.portal_selections.setSelectionToAll(selection_name, REQUEST=request)
url = context.portal_selections.getSelectionListUrlFor(selection_name, REQUEST=request)

request.RESPONSE.redirect(url)
