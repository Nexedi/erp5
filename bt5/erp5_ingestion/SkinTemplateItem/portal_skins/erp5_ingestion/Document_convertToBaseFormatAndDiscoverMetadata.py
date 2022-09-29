"""
  This is a convenient method to call both convertToBaseFormat and
  discoverMetadata in good order in the same transaction.
  This method guarantees order of calling methods.
"""

if context.isSupportBaseDataConversion():
  context.convertToBaseFormat()

return context.discoverMetadata(filename=filename,
                                user_login=user_login,
                                input_parameter_dict=input_parameter_dict)
