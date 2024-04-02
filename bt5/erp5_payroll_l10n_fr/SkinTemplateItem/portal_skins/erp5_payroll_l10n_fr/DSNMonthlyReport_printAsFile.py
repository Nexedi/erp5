from Products.ERP5Type.Utils import str2unicode
import unicodedata

data = unicodedata.normalize('NFKD', str2unicode(context.getTextContent())).encode('iso-8859-1', 'ignore')

# Update sending mode "on the fly"
dsn_line_list = data.split(b'\n')
for line_number, dsn_line in enumerate(dsn_line_list):
  if dsn_line.split(b',', 1)[0] == b'S10.G00.00.005':
    dsn_line_list[line_number] = b'S10.G00.00.005,\'%s\'' % sending_mode.encode()

data = b'\n'.join(dsn_line_list)

filename = context.getTitle()

RESPONSE.setHeader("Content-Type", "text/plain; charset=iso-8859-1")
RESPONSE.setHeader("Content-Length", len(data))
RESPONSE.setHeader("Content-Disposition", "attachment;filename='%s.dsn'" % filename)

return data
