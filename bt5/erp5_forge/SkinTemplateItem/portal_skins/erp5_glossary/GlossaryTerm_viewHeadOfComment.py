LENGTH = 50
comment = context.getProperty('comment') or ''
return comment[:LENGTH]
