## Script (Python) "Account_search"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kwd
##title=
##
for cname in kwd.keys():
  if kwd[cname] == '' or kwd[cname] is None:
    del kwd[cname]

kwd['select_expression'] = "'EUR' AS accounting_transaction_line_currency"
return context.portal_catalog(**kwd)
