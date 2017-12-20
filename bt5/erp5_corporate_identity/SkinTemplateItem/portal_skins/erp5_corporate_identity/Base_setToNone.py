"""
================================================================================
Clean parameters which can be "" or "0" if passed through http
================================================================================
"""
# parameters:
# ------------------------------------------------------------------------------
# parameter                    Parameter to lookup
if param == "" or param == None or param == 0 or param == str(0):
  return None
else:
  return param
