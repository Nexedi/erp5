import six
import ipaddress
from Products.ERP5Type.Message import translateString
from Products.Formulator.Errors import ValidationError

for addr in editor:
  addr = addr.strip()
  if not addr:
    continue
  if addr[0] == '#':
    continue
  if six.PY2:
    addr = addr.decode('utf-8')
  try:
    ipaddress.ip_network(addr)
  except ValueError as error:
    raise ValidationError(
      'external_validator_failed',
      context,
      error_text=translateString(
        "Invalid IP Network ${error}",
        mapping={
          "addr": addr,
          "error": error
        }
      )
    )

return True
