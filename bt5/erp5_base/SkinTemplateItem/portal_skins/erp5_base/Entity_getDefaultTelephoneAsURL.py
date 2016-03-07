telephone = context.getDefaultTelephoneValue()
if telephone is not None:
  return telephone.asURL()
