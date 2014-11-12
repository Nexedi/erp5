method = getattr(context, 'getSourceValue', None)
if method is None:
  return "http://192.168.1.168/cgi-bin/epos/service.cgi?devid=local_printer&timeout=10000"
source = method()
if source is not None:
  link = getattr(source, "default_printer_url", None)
  if link is not None:
    return link.getUrlString()
return "http://192.168.1.168/cgi-bin/epos/service.cgi?devid=local_printer&timeout=10000"
