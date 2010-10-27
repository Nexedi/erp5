# -*- coding: utf-8 -*-
# Code based on python-memcached-1.45
try:
    import memcache
except ImportError:
    pass
else:
    memcache._Host._SOCKET_TIMEOUT = 10 # wait more than 3s is safe
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
                return '' #None
            buf += data
        self.buffer = buf[index+2:]
        return buf[:index]
    memcache._Host.readline = readline
