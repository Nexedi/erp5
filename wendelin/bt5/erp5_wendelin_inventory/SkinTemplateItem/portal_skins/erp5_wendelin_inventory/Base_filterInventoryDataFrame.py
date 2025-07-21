data = {}
data.update(kw)
data.update(container.REQUEST.form)

return context.Base_getInventoryDataFrame(**data)
