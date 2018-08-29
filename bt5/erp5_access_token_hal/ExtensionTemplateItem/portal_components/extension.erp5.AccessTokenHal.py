import os
import hashlib

def generateSecretKey(self, length=128):
  return hashlib.sha1(os.urandom(length)).hexdigest()
