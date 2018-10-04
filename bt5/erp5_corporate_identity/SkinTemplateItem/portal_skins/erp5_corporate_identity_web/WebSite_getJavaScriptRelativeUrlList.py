"""
================================================================================
Return extendable default list of JavaScript files to load
================================================================================
"""
if scope is not None:
  if scope == "global":
    return [
      "ci_web_js/ci_web.js"
    ]
return []
