from Products.ERP5Type.Document import newTempBase
from Products.ERP5Type.Utils import sortValueList
result = [newTempBase(context, '_', uid="%u.%s" % (i, x['revision']), **x)
          for i, x in enumerate(context.getVcsTool().log(added))]
return sortValueList(result, **kw)
