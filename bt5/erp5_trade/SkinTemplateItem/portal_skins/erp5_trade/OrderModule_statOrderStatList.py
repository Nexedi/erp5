request = container.REQUEST
RESPONSE =  request.RESPONSE

stat_line = request.get('stat_line', None)

return stat_line
