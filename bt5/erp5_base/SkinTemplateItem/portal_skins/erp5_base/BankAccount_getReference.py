if context.getIban():
  return context.getIban()

reference = ' '.join(
    part for part in (
        context.getBankCountryCode(),
        context.getBankCode(),
        context.getBranch(),
        context.getBankAccountNumber(),
        context.getBankAccountKey(),)
    if part
)

if not reference.strip():
  return default or context.getTitleOrId()

return reference
