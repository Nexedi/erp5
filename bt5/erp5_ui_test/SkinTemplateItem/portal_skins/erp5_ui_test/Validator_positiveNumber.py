if value:
  try:
    return float(value) > 0
  except ValueError:
    # conversion error - not a number
    return True
return True
