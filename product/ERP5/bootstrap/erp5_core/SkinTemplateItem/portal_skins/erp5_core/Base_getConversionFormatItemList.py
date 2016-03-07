'''Returns all possible document conversions from the `base_content_type`.
'''
from Products.ERP5Type.Document import newTempOOoDocument
td = newTempOOoDocument(context, 'testOOo')
td.edit(base_content_type=base_content_type, base_data='not empty')
return  [('', '')] + td.getTargetFormatItemList()
