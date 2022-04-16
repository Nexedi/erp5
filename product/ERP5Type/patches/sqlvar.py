##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

try:
  from Shared.DC.ZRDB.sqlvar import StringTypes
except ImportError: # Products.ZSQLMethods < 3.0.8
  import six
  StringTypes = six.string_types + (six.binary_type,)

# dtml-sqlvar patch to convert None to NULL, and deal with DateTime

from Shared.DC.ZRDB.sqlvar import *
from Shared.DC.ZRDB import sqlvar
from DateTime import DateTime

if 1: # For easy diff with original (ZSQLMethods 3.14)
    def render(self, md):
        name = self.__name__
        args = self.args
        t = args['type']
        try:
            expr = self.expr
            if isinstance(expr, StringTypes):
                v = md[expr]
            else:
                v = expr(md)
        except Exception:
            if 'optional' in args and args['optional']:
                return 'null'
            if not isinstance(expr, StringTypes):
                raise
            raise ValueError('Missing input variable, <em>%s</em>' % name)

        if v is None:
            return 'null'

        if t == 'int':
            try:
                if isinstance(v, StringTypes):
                    if v[-1:] == 'L':
                        v = v[:-1]
                    int(v)
                else:
                    v = str(int(v))
            except Exception:
                if not v and 'optional' in args and args['optional']:
                    return 'null'
                err = 'Invalid integer value for <em>%s</em>' % name
                raise ValueError(err)
        elif t == 'float':
            try:
                if isinstance(v, StringTypes):
                    if v[-1:] == 'L':
                        v = v[:-1]
                    float(v)
                else:
                    # ERP5 patch: We use repr that have better precision than str for
                    # floats (on python2 only)
                    v = repr(float(v))
            except Exception:
                if not v and 'optional' in args and args['optional']:
                    return 'null'
                err = 'Invalid floating-point value for <em>%s</em>' % name
                raise ValueError(err)

        elif t.startswith('datetime'):
            # For subsecond precision, use 'datetime(N)' MySQL type,
            # where N is the number of digits after the decimal point.
            n = 0 if t == 'datetime' else int(t[9])
            try:
                v = (v if isinstance(v, DateTime) else DateTime(v)).toZone('UTC')
                return "'%s%s'" % (v.ISO(),
                    ('.%06u' % (v.micros() % 1000000))[:1+n] if n else '')
            except Exception:
                t = 'datetime'

        elif t=='nb' and not v:
            t = 'empty string'

        else:
            if not isinstance(v, (str, StringTypes)):
                v = str(v)
            if not v and t == 'nb':
                if 'optional' in args and args['optional']:
                    return 'null'
                else:
                    err = 'Invalid empty string value for <em>%s</em>' % name
                    raise ValueError(err)

            v = md.getitem('sql_quote__', 0)(v)
            # if v.find("\'") >= 0: v="''".join(v.split("\'"))
            # v="'%s'" % v

        return v

# Patched by yo. datetime is added.
new_valid_types = 'int', 'float', 'string', 'nb', 'datetime'
new_valid_types += tuple(map('datetime(%s)'.__mod__, range(7)))
try:
  # BBB
  from Shared.DC.ZRDB.sqlvar import valid_type
  sqlvar.valid_type = new_valid_types.__contains__
except ImportError:
  sqlvar.valid_types = new_valid_types

SQLVar.render = render
SQLVar.__call__ = render
