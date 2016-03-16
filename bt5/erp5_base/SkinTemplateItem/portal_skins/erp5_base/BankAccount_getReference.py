reference = ''
if context.getBankCountryCode():
  reference = ' '.join((context.getBankCountryCode(),
                   context.getBankCode() or '',
                   context.getBranch() or '',
                   context.getBankAccountNumber() or '',
                   context.getBankAccountKey() or ''))
else:
  reference = ' '.join((context.getBankCode() or '',
                   context.getBranch() or '',
                   context.getBankAccountNumber() or '',
                   context.getBankAccountKey() or ''))

if not reference.strip():
  return default or context.getTitleOrId()

return reference
