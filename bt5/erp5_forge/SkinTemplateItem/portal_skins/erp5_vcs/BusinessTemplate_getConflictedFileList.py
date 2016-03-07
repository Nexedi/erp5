from Products.ERP5Type.Document import newTempBase
from Products.ERP5Type.Utils import sortValueList

result = [newTempBase(context, '_', uid=path)
          for path in context.getVcsTool().getConflictedFileList()]
return sortValueList(result, **kw)
