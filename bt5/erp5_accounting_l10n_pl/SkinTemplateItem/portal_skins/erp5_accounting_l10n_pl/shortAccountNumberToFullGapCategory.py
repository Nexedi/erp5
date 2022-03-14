from builtins import range
gap_root = kw.get('gap_root', context.getPortalObject().portal_preferences.getPreferredAccountingTransactionGap())

parts=[]
for i in range(len(accountNumber)+1):
  parts.append(accountNumber[:i])
  context.log(parts)
return gap_root+'/'.join(parts)
