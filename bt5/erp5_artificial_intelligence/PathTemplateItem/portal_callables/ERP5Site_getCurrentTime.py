# portal_callable ERP5Site_getCurrentTime (in portal_callables, params: none)
now = DateTime()
return {"iso": now.ISO8601(), "date": now.Date(), "time": now.TimeMinutes(), "timezone": now.timezone()}
