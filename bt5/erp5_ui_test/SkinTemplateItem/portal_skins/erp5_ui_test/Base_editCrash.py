# Always crash with custom response code

if request is None:
  request = container.REQUEST

request.RESPONSE.setStatus(response_code)

if return_none:
  return None

return request.RESPONSE
