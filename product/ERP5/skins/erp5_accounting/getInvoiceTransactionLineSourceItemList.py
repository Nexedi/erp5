## Script (Python) "getInvoiceTransactionLineSourceItemList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
if context.id == 'l0':
  if context.portal_type == 'Purchase Invoice Transaction Line':
    compte2 = '409'
    compte = '40'
  elif context.portal_type == 'Sale Invoice Transaction Line':
    compte = '41'
    compte2 = '410'
  return context.portal_categories.pcg['4'][compte][compte2].getCategoryMemberTitleItemList()
elif context.id == 'l1':
  if context.portal_type == 'Purchase Invoice Transaction Line':
    compte = '6'
  elif context.portal_type == 'Sale Invoice Transaction Line':
    compte = '7'
  return context.portal_categories.pcg[compte].getCategoryMemberTitleItemList()
elif context.id == 'l2':
  return context.portal_categories.pcg['4']['44'].getCategoryMemberTitleItemList()
else:
  return context.portal_categories.pcg.getCategoryMemberTitleItemList()

return ()
