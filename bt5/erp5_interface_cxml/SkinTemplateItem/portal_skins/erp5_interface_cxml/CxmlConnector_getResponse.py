from DateTime import DateTime
return """<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE cXML SYSTEM "http://xml.cXML.org/schemas/cXML/1.2.014/cXML.dtd">
<cXML lang="en" payloadID="%s" timestamp ="%s">
  <Response>
    <Status code="%s" text="%s">%s</Status>
  </Response>
</cXML>""" %(context.getPayloadId(), DateTime().ISO8601(), code, text, content)
