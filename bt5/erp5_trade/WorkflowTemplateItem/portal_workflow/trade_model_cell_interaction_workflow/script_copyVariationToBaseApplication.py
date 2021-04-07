var = state_change['object'].getVariationCategoryList()

state_change['object'].log("var = %s" %(var,))
state_change['object'].setBaseApplicationList(var)
