# -*- coding: utf-8 -*-
# Code based on python-memcached-1.53
try:
    from memcache import _Host, Client, _Error
except ImportError:
    pass
else:
    _Host._SOCKET_TIMEOUT = 10 # wait more than 3s is safe

    try:
        from memcache import _ConnectionDeadError
    except ImportError:
        # BBB
        class _ConnectionDeadError(Exception):
            pass
    Client.MemcachedConnectionError = _ConnectionDeadError

    import socket
    def _get(self, cmd, key):
        if getattr(self, 'do_check_key', True):
            self.check_key(key)
        server, key = self._get_server(key)
        if not server:
            # (patch)
            # return None
            raise _ConnectionDeadError

        def _unsafe_get():
            self._statlog(cmd)

            try:
                server.send_cmd("%s %s" % (cmd, key))
                rkey = flags = rlen = cas_id = None

                if cmd == 'gets':
                    try:
                        rkey, flags, rlen, cas_id, = self._expect_cas_value(server,
                                raise_exception=True)
                    except TypeError:
                        # BBB
                        rkey, flags, rlen, cas_id, = self._expect_cas_value(server)
                    if rkey and self.cache_cas:
                        self.cas_ids[rkey] = cas_id
                else:
                    try:
                        rkey, flags, rlen, = self._expectvalue(server,
                                raise_exception=True)
                    except TypeError:
                        # BBB
                        rkey, flags, rlen, = self._expectvalue(server)
                if not rkey:
                    # (patch)
                    # return None
                    raise KeyError
                try:
                    value = self._recv_value(server, flags, rlen)
                finally:
                    try:
                        server.expect("END", raise_exception=True)
                    except TypeError:
                        # BBB
                        server.expect("END")
            except (_Error, socket.error) as msg:
                if isinstance(msg, tuple): msg = msg[1]
                server.mark_dead(msg)
                # (patch)
                # return None
                raise _ConnectionDeadError

            return value

        try:
            return _unsafe_get()
        except _ConnectionDeadError:
            # retry once
            try:
                if server.connect():
                    return _unsafe_get()
                # (patch)
                # return None
                raise _ConnectionDeadError
            except (_ConnectionDeadError, socket.error) as msg:
                server.mark_dead(msg)
            # (patch)
            # return None
            raise _ConnectionDeadError

    Client._get = _get
