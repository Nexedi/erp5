##parameters=selection_name, uids


request = context.REQUEST
context.portal_selections.setSelectionToIds(selection_name, uids, REQUEST=request)
url = context.portal_selections.getSelectionListUrlFor(selection_name, REQUEST=request)

request.RESPONSE.redirect(url)
