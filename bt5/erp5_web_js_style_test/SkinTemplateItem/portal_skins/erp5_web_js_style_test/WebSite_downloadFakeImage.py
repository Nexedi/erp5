response = REQUEST.RESPONSE

response.setHeader('Content-Type', 'image/svg+xml')

if (format == 'jpg') and (display == 'small') and (quality == '90'):
  emoji = '👍'
else:
  emoji = '👎'

return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90%">' + emoji + '</text></svg>'
