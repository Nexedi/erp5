def getQuickCostingStat(self, **kw):
  result = self.Transformation_quickCostingListBuilder(stat_mode=1,**kw)
  total = 0
  for m in result:
   total += m.transformed_total_price

  class r:
    pass

  ri = r()
  ri.transformed_total_price = total

  return [ri] 
