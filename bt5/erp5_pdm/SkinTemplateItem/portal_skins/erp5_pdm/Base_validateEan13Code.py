if not ean13_code:
  return True

ean13_code = [x for x in ean13_code if x.isalnum()]

if len(ean13_code) != 13:
  return False

key = 0
coeff = 1
for c in ean13_code[:12]:
  key += int(c) * coeff
  coeff = 4 - coeff # coeff value alternates between 1 and 3
key = (10 - key) % 10

if key != int(ean13_code[12]):
  return False

return True
