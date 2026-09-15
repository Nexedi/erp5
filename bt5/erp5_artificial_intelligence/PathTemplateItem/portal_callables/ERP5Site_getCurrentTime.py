now = DateTime()
return {"iso": now.ISO8601(), "date": now.Date(), "time": now.TimeMinutes(), "timezone": now.timezone()}
