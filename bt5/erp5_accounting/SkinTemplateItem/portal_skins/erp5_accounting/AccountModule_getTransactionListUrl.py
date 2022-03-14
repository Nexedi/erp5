from builtins import str
from ZTUtils import make_query
from Products.PythonScripts.standard import html_quote

index = context.portal_selections.getSelectionIndexFor(selection_name)
account = brain.getObject()

# this is for domain_tree mode
if account.getPortalType() == "Category":
  return "#"

kw = { 'selection_index': str(index),
       'selection_name' : selection_name,
       'reset' : '1',
     }

return html_quote('%s/Account_viewAccountingTransactionList?%s' % (
  account.absolute_url(), make_query(kw)))
