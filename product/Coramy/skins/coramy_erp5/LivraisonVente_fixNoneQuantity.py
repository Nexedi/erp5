## Script (Python) "LivraisonVente_fixNoneQuantity"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
blist = list(context.LivraisonVente_searchNoneQuantity())
context.portal_simulation.commitTransaction()

for b in blist:
  o = b.getObject()
  if o is not None:
    if o.getQuantity() == o.getRelatedQuantity():
      #print "Fixed equal %s %s %s" % (o.getRelativeUrl(), o.getQuantity(), o.getRelatedQuantity())
      #o.edit(quantity = o.getQuantity(), force_update = 1)
      pass
    else:
      if o.getRelatedQuantity() is None:
        print "Not Fixeable %s %s %s" % (o.getRelativeUrl(), o.getQuantity(), o.getRelatedQuantity())
      else:
        print "Fixed different %s %s %s" % (o.getRelativeUrl(), o.getQuantity(), o.getRelatedQuantity())
        o.edit(quantity = o.getRelatedQuantity())
    o.commitTransaction()
  
return printed
