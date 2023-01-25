"""Use information given in the method mailPasswordResetRequest of Password Tool
to build a substitution mapping dict.
Parameters:
  instance_name -- Current erp5 portal title
  reset_password_link -- Url to reset the password
  expiration_date -- Expiration Datetime of the link
"""
return {'reset_password_link':reset_password_link,
        'expiration_date': context.Base_FormatDate(date=expiration_date,
                                                   hour_minute = True,
                                                   seconds = False)}
