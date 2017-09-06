result = getattr(context.support_request_module, method_id)(**kw)
REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')

return result
