SELECT original_message, translated_message, portal_type
FROM translation
WHERE
  <dtml-sqltest language type="string" op="eq"> AND
  <dtml-sqltest message_context type="string" op="eq"> AND
  <dtml-sqltest translated_message type="string" op="eq" multiple="true">