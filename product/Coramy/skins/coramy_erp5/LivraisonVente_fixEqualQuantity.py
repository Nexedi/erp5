## Script (Python) "LivraisonVente_fixEqualQuantity"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
blist = list(context.LivraisonVente_searchEqualQuantity())
context.portal_simulation.commitTransaction()

for b in blist:
  o = b.getObject()
  if o is not None:
    if o.getQuantity() != o.getRelatedQuantity():
      if o.getRelatedQuantity() is None:
        print "Not Fixeable %s %s %s" % (o.getRelativeUrl(), o.getQuantity(), o.getRelatedQuantity())
      else:
        print "Fixed %s %s %s" % (o.getRelativeUrl(), o.getQuantity(), o.getRelatedQuantity())
        o.edit(quantity = o.getRelatedQuantity())
  

return printed
