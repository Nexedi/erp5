from Products.ERP5Type.Message import Message

model_list = [x.getObject() for x in context.checkbook_model_module.searchFolder()]
result_list = [(x.getTitle(),x.getRelativeUrl()) for x in model_list if not x.isInsideCheckbook()]
return result_list
