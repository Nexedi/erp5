## Script (Python) "SaleInvoice_updateTransaction"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# Create invoice lines
global total_price 
global total_vat 
global total_discount 
total_price = 0.0
total_vat = 0.0
total_discount = 0.0
invoice = context

def updateTotal(l):
  global total_price 
  global total_vat 
  global total_discount 
  if l.getPrice() in ('', None):
    return 'Price is not defined for %s %s' % (l.getResource(), l.getVariationText())
  elif l.getQuantity():
    price = l.getPrice() * l.getQuantity()
    total_price += price
    if l.getValueAddedTaxRatio() and l.getValueAddedTaxRecoverable():
      total_vat += price * l.getValueAddedTaxRatio()
  return None  

for l in context.contentValues(filter={'portal_type':"Invoice Line"}):
  if l.hasCellContent():
    for c in l.contentValues(filter={'portal_type':"Invoice Cell"}):
      error_message = updateTotal(c)
      if error_message is not None:
        return error_message 
  else:
    error_message = updateTotal(l)
    if error_message is not None:
      return error_message 

# Generate accounting lines
# Income Line
if not invoice.hasObject('income'):
  income = invoice.newContent(portal_type="Sale Invoice Transaction Line", id='income')                          
else:
  income = context.income 
income.edit(source='account/vente', destination='account/achat',
                           source_credit=total_price)
# Payable Line
if not invoice.hasObject('payable'):
  payable = invoice.newContent(portal_type="Sale Invoice Transaction Line", id='payable')                          
else:
  payable = context.payable 
payable.edit(source='account/creance_client', destination='dette_fournisseur',
                           source_debit=total_price + total_vat)

# VAT Line
if not invoice.hasObject('vat'):
  vat = invoice.newContent(portal_type="Sale Invoice Transaction Line", id='vat')                          
else:
  vat = context.vat
vat.edit(source='account/tva_collectee_196', destination='account/tva_recuperable_196',
                           source_credit=total_vat)
