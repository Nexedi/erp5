# -*- coding: utf-8 -*-
#Code based on python-memcached-1.44
import types
try:
  import cPickle as pickle
except ImportError:
  import pickle
try:
  # Only exists in Python 2.4+
  from threading import local
except ImportError:
  # TODO:  add the pure-python local implementation
  class local(object):
    pass
try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO

try:
  import memcache
except ImportError:
  memcache = None
if memcache is not None:
  Client = memcache.Client
  SERVER_MAX_KEY_LENGTH = memcache.SERVER_MAX_KEY_LENGTH
  SERVER_MAX_VALUE_LENGTH = memcache.SERVER_MAX_VALUE_LENGTH

  def Client__init__(self, servers, debug=0, pickleProtocol=0,
               pickler=pickle.Pickler, unpickler=pickle.Unpickler,
               pload=None, pid=None, server_max_key_length=SERVER_MAX_KEY_LENGTH,
               server_max_value_length=SERVER_MAX_VALUE_LENGTH):
    """
    Create a new Client object with the given list of servers.

    @param servers: C{servers} is passed to L{set_servers}.
    @param debug: whether to display error messages when a server can't be
    contacted.
    @param pickleProtocol: number to mandate protocol used by (c)Pickle.
    @param pickler: optional override of default Pickler to allow subclassing.
    @param unpickler: optional override of default Unpickler to allow subclassing.
    @param pload: optional persistent_load function to call on pickle loading.
    Useful for cPickle since subclassing isn't allowed.
    @param pid: optional persistent_id function to call on pickle storing.
    Useful for cPickle since subclassing isn't allowed.
    """
    local.__init__(self)
    self.set_servers(servers)
    self.debug = debug
    self.stats = {}

    # Allow users to modify pickling/unpickling behavior
    self.pickleProtocol = pickleProtocol
    self.pickler = pickler
    self.unpickler = unpickler
    self.persistent_load = pload
    self.persistent_id = pid
    #Patch store these Constant on object itself
    self.server_max_key_length = server_max_key_length
    self.server_max_value_length = server_max_value_length

    #  figure out the pickler style
    file = StringIO()
    try:
        pickler = self.pickler(file, protocol = self.pickleProtocol)
        self.picklerIsKeyword = True
    except TypeError:
        self.picklerIsKeyword = False

  def memcache_check_key(key, key_extra_len=0):
    """Checks sanity of key.  Fails if:
        Key length is > SERVER_MAX_KEY_LENGTH (Raises MemcachedKeyLength).
        Contains control characters  (Raises MemcachedKeyCharacterError).
        Is not a string (Raises MemcachedStringEncodingError)
        Is an unicode string (Raises MemcachedStringEncodingError)
        Is not a string (Raises MemcachedKeyError)
        Is None (Raises MemcachedKeyError)
    """
    if type(key) == types.TupleType: key = key[1]
    if not key:
      raise Client.MemcachedKeyNoneError, ("Key is None")
    if isinstance(key, unicode):
      raise Client.MemcachedStringEncodingError, ("Keys must be str()'s, not "
              "unicode.  Convert your unicode strings using "
              "mystring.encode(charset)!")
    if not isinstance(key, str):
      raise Client.MemcachedKeyTypeError, ("Key must be str()'s")

    if isinstance(key, basestring):
      for char in key:
        #Patch: skip key length check because we have no information
        #about key length in memcache class level.
        if 0 and len(key) + key_extra_len > SERVER_MAX_KEY_LENGTH:
             raise Client.MemcachedKeyLengthError, ("Key length is > %s"
                     % SERVER_MAX_KEY_LENGTH)
        if ord(char) < 32 or ord(char) == 127:
            raise Client.MemcachedKeyCharacterError, "Control characters not allowed"

  def Client__val_to_store_info(self, val, min_compress_len):
    """
       Transform val to a storable representation, returning a tuple of the flags, the length of the new value, and the new value itself.
    """
    flags = 0
    if isinstance(val, str):
      pass
    elif isinstance(val, int):
      flags |= Client._FLAG_INTEGER
      val = "%d" % val
      # force no attempt to compress this silly string.
      min_compress_len = 0
    elif isinstance(val, long):
      flags |= Client._FLAG_LONG
      val = "%d" % val
      # force no attempt to compress this silly string.
      min_compress_len = 0
    else:
      flags |= Client._FLAG_PICKLE
      file = StringIO()
      if self.picklerIsKeyword:
        pickler = self.pickler(file, protocol = self.pickleProtocol)
      else:
        pickler = self.pickler(file, self.pickleProtocol)
      if self.persistent_id:
        pickler.persistent_id = self.persistent_id
      pickler.dump(val)
      val = file.getvalue()

    lv = len(val)
    # We should try to compress if min_compress_len > 0 and we could
    # import zlib and this string is longer than our min threshold.
    if min_compress_len and _supports_compress and lv > min_compress_len:
      comp_val = compress(val)
      # Only retain the result if the compression result is smaller
      # than the original.
      if len(comp_val) < lv:
        flags |= Client._FLAG_COMPRESSED
        val = comp_val

    #Patch: add support for infinite value length
    if self.server_max_value_length == 0:
      return (flags, len(val), val)
    #  silently do not store if value length exceeds maximum
    if len(val) >= self.server_max_value_length: return(0)
    return (flags, len(val), val)

  Client.__init__ = Client__init__
  Client._val_to_store_info = Client__val_to_store_info
  memcache.check_key = memcache_check_key
  del Client__init__, Client__val_to_store_info, memcache_check_key
