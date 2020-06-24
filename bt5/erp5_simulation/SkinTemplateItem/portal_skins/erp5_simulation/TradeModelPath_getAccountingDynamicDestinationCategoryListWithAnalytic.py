category_list = context.TradeModelPath_getAccountingDynamicDestinationCategoryListWithoutAnalytic(movement)

function = movement.getDestinationFunction(
    base=True) or context.getDestinationFunction(base=True)
if function:
  category_list.append(function)

funding = movement.getDestinationFunding(
    base=True) or context.getDestinationFunding(base=True)
if funding:
  category_list.append(funding)

project = movement.getDestinationProject(
    base=True) or context.getDestinationProject(base=True)
if project:
  category_list.append(project)

return category_list
