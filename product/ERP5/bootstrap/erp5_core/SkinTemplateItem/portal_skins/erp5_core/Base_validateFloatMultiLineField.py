"""Validate that all items in a multi line field are floats.
"""
for item in editor:
  try:
    float(item)
  except (ValueError, TypeError):
    return 0
return 1
