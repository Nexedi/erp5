def getAvailableItemStat(self, **kw):
  result = self.PieceTissu_zGetAvailableItemList(**kw)
  if len(result) > 100:
    return "Trop de pièces"
  remaining_quantity = 0.0
  for m in result:
    o = m.getObject()
    if o is not None:
      remaining_quantity += o.getRemainingQuantity()

  class r:
    pass

  ri = r()
  ri.getRemainingQuantity = remaining_quantity

  return [ri] 
