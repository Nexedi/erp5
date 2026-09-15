"""Answer the strong model of this Artificial Task, or None.

This script holds no model identifier. The property
`strong_model` of the Artificial Task holds the value. The value is data, and
the value is not code.

An empty value is one valid state. An empty value stops every escalation.
"""
# The accessor exists only after the install of the property sheet. One
# instance with no property must answer None, and must not raise.
method = getattr(context, 'getStrongModel', None)
if method is None:
  return None
value = method()
if value:
  return value
return None
