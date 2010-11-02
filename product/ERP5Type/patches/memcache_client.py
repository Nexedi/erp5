# -*- coding: utf-8 -*-
# Code based on python-memcached-1.45
try:
    from memcache import _Host, Client, _Error
except ImportError:
    pass
else:
    _Host._SOCKET_TIMEOUT = 10 # wait more than 3s is safe
    # always return string
    # https://bugs.launchpad.net/python-memcached/+bug/509712
    def readline(self):
        buf = self.buffer
        recv = self.socket.recv
        while True:
            index = buf.find('\r\n')
            if index >= 0:
                break
            data = recv(4096)
            if not data:
                self.mark_dead('Connection closed while reading from %s'
                        % repr(self))
                self.buffer = ''
                # (patch)
                # return None
                return ''
            buf += data
        self.buffer = buf[index+2:]
        return buf[:index]
    _Host.readline = readline

    # Client._get() should raises an Exception instead of returning
    # None, in case of connection errors or missing values.
    class MemcachedConnectionError(Exception):
        pass
    Client.MemcachedConnectionError = MemcachedConnectionError

    import socket
    def _get(self, cmd, key):
        self.check_key(key)
        server, key = self._get_server(key)
        if not server:
            # (patch)
            # return None
            raise MemcachedConnectionError
        self._statlog(cmd)

        try:
            server.send_cmd("%s %s" % (cmd, key))
            rkey = flags = rlen = cas_id = None
            if cmd == 'gets':
                rkey, flags, rlen, cas_id, = self._expect_cas_value(server)
                if rkey:
                    self.cas_ids[rkey] = cas_id
            else:
                rkey, flags, rlen, = self._expectvalue(server)

            if not rkey:
                # (patch)
                # return None
                raise KeyError
            value = self._recv_value(server, flags, rlen)
            server.expect("END")
        except (_Error, socket.error), msg:
            if isinstance(msg, tuple): msg = msg[1]
            server.mark_dead(msg)
            # (patch)
            # return None
            raise MemcachedConnectionError
        return value

    Client._get = _get
