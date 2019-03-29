reference = bank_account.getReference()
if not same_type(reference, ''):
  raise TypeError('Reference is not a string: %s.getReference() == %s' % (repr(bank_account), repr(reference)))
return 'bank_account_%s' % (reference, )
