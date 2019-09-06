# you can pass oid like "?oid=0x123456"

if oid.startswith('0x'):
  oid = ('\x00'*8 + oid[2:].decode('hex'))[-8:]

ob = context.getObjectByOid(oid)
print repr(ob)[:10*1024]
return printed
