import unicodedata

data = unicodedata.normalize('NFKD', context.getTextContent().decode('utf-8')).encode('iso-8859-1', 'ignore')

# Update sending mode "on the fly"
dsn_line_list = data.split('\n')
for line_number, dsn_line in enumerate(dsn_line_list):
  if dsn_line.split(',', 1)[0] == 'S10.G00.00.005':
    dsn_line_list[line_number] = 'S10.G00.00.005,\'%s\'' % sending_mode

data = '\n'.join(dsn_line_list)

filename = context.getTitle()

RESPONSE.setHeader("Content-Type", "text/plain; charset=iso-8859-1")
RESPONSE.setHeader("Content-Length", len(data)) 
RESPONSE.setHeader("Content-Disposition", "attachment;filename='%s.dsn'" % filename)

return data
