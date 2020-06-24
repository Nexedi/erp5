category_list = context.TradeModelPath_getAccountingDynamicSourceCategoryListWithoutAnalytic(movement)

function = movement.getSourceFunction(base=True) or context.getSourceFunction(
    base=True)
if function:
  category_list.append(function)

funding = movement.getSourceFunding(base=True) or context.getSourceFunding(
    base=True)
if funding:
  category_list.append(funding)

project = movement.getSourceProject(base=True) or context.getSourceProject(
    base=True)
if project:
  category_list.append(project)

return category_list
