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

# dtml-sqlvar patch to convert None to NULL, and deal with DateTime

from Shared.DC.ZRDB.sqlvar import SQLVar
from Shared.DC.ZRDB import sqlvar
from string import atoi,atof
from DateTime import DateTime

def SQLVar_render(self, md):
    args=self.args
    t=args['type']
    try:
        expr=self.expr
        if type(expr) is str: v=md[expr]
        else: v=expr(md)
    except Exception:
        if args.get('optional'):
            return 'null'
        if type(expr) is not str:
            raise
        raise ValueError('Missing input variable, <em>%s</em>' % self.__name__)

    if v is None and args.get('optional'):
        return 'null'

    if t=='int':
        try:
            if type(v) is str:
                if v[-1:]=='L':
                    v=v[:-1]
                atoi(v)
                return v
            return str(int(v))
        except Exception:
            t = 'integer'
    elif t=='float':
        try:
            if type(v) is str:
                if v[-1:]=='L':
                    v=v[:-1]
                atof(v)
                return v
            # ERP5 patch, we use repr that have better precision than str for
            # floats
            return repr(float(v))
        except Exception:
            t = 'floating-point'
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
        v = md.getitem('sql_quote__',0)(
            v if isinstance(v, basestring) else str(v))
        #if find(v,"\'") >= 0: v=join(split(v,"\'"),"''")
        #v="'%s'" % v
        return v

    if args.get('optional'):
        return 'null'
    raise ValueError('Invalid %s value for <em>%s</em>: %r'
                     % (t, self.__name__, v))

# Patched by yo. datetime is added.
new_valid_types = 'int', 'float', 'string', 'nb', 'datetime'
new_valid_types += tuple(map('datetime(%s)'.__mod__, xrange(7)))
try:
  # BBB
  from Shared.DC.ZRDB.sqlvar import valid_type
  sqlvar.valid_type = new_valid_types.__contains__
except ImportError:
  sqlvar.valid_types = new_valid_types
    

SQLVar.render = SQLVar_render
SQLVar.__call__ = SQLVar_render
