## Script (Python) "AccountingTransactionModule_getDestinationSectionUrl"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=brain=None, selection=None, **kwd
##title=
##
from ZTUtils import make_query

index = selection.getIndex()
name = selection.getName()
object = brain.getObject()

url = object.getDestinationSectionValue().absolute_url()
method = 'Entity_viewAccountingTransactionList'
kw = { 
       'reset' : '1', 
     }

return url + '/' + method + '?' + make_query(kw)
