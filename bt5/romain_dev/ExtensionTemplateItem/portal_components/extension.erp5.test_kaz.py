def getObjectByOid(self):#XXXYYY
  # ConflictError: database conflict error (oid 0x174c174d, class BTrees.OIBTree.OIBucket, serial this txn started with 0x03f7c3f85883f5bb 2024-04-08 14:48:20.745813, serial currently committed 0x03f7c3f95ce66c66 2024-04-08 14:49:21.773459)

  oid = 0x174c174d
  oid = 0x154aaf61
  oid = 0x174c283a
  oid = 0x174ac365
  oid = 0x11599980
  oid = 0x0f29c33d
  oid = 0x17501c78
  oid = 0x17509394
  oid = 0x050ae6c4
  oid = 0x589a
  oid = 0x1770c10c
  oid = 0x1775c212
  from ZODB.utils import p64
  oid = p64(int(str(oid), 0))
  ob = self._p_jar.get(oid)

  # ob = self._p_jar[oid]
  if 1:
    return ob
