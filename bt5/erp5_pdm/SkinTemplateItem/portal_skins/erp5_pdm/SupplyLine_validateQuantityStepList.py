"""Validate that all quantity steps are floats.
"""
for item in editor:
  try:
    float(item)
  except (ValueError, TypeError):
    return 0
return 1
