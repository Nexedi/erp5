"""
  Check if login exist or not. It's the inverse of avaibility
"""
return not context.ERP5Site_isLocalLoginAvailable(value, REQUEST)
