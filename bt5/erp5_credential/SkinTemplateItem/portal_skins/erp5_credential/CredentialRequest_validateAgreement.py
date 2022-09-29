""" Use as validator method for a checkbox.
Return True if checked.
Parameters:
value -- State of checking (default:None,boolean)
REQUEST -- Standard request variable"""
if value:
  return True
return False
