## Script (Python) "AccountModule_getCurrencyUrl"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=brain=None, selection=None
##title=
##
from ZTUtils import make_query

params = selection.getParams()
object = context.restrictedTraverse(params['accounting_transaction_line_currency'])
url = object.absolute_url()
method = 'view'
kw = { 
       'reset' : '1', 
     }

return url + '/' + method + '?' + make_query(kw)
