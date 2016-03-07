from ZTUtils import make_query
from Products.PythonScripts.standard import html_quote

index = context.portal_selections.getSelectionIndexFor(selection_name)
object = brain.getObject()

# this is for domain_tree mode
if object.getPortalType() == "Category" : 
 return "#"

method = 'Account_viewAccountingTransactionList'
kw = { 'selection_index': str(index),
       'selection_name' : selection_name, 
       'reset' : '1', 
     }

return html_quote('%s/%s?%s' % (object.absolute_url(), method, make_query(kw)))
