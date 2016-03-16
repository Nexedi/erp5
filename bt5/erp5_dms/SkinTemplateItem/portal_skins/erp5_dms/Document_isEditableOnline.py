return not getattr(context, 'isSupportBaseDataConversion', lambda:False)()
