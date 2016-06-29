portal = context.getPortalObject()

data = context.getTextContent().decode('utf-8').encode('iso-8859-1')
filename = context.getTitle()

RESPONSE.setHeader("Content-Type", "text/plain; charset=iso-8859-1")
RESPONSE.setHeader("Content-Length", len(data)) 
RESPONSE.setHeader("Content-Disposition", "attachment;filename='%s.dsn'" % filename)

return data
