## Script (Python) "Invoice_zGetTotalVat"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
price = context.Invoice_zGetTotalNetPrice()

if context.getValueAddedTaxRecoverable():
  vat_ratio = context.getValueAddedTaxRatio()
  if vat_ratio != None:
    price *= vat_ratio
  else:
    price = 0
else:
  price = 0

return price
