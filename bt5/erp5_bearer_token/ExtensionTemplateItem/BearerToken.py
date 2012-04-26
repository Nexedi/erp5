import hmac

def getHMAC(self, key, body):
  digest = hmac.new(key, body)
  return digest.hexdigest()
