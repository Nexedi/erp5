##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
from Shared.DC.ZRDB.sqltest import *
from Shared.DC.ZRDB import sqltest
from DateTime import DateTime

list_type_list = list, tuple, set, frozenset, dict

if 1: # For easy diff with original
    def render(self, md):
        name=self.__name__

        t=self.type
        args=self.args
        try:
            expr=self.expr
            if type(expr) is type(''):
                v=md[expr]
            else:
                v=expr(md)
        except (KeyError, NameError):
            if 'optional' in args and args['optional']:
                return ''
            raise ValueError('Missing input variable, <em>%s</em>' % name)

        # PATCH: use isinstance instead of type comparison, to allow
        # subclassing.
        if isinstance(v, list_type_list):
            if len(v) > 1 and not self.multiple:
                raise ValueError(
                    'multiple values are not allowed for <em>%s</em>'
                    % name)
        else: v=[v]

        vs=[]
        for v in v:
            if not v and type(v) is StringType and t != 'string': continue
            if t=='int':
                try:
                    if type(v) is StringType:
                        if v[-1:]=='L':
                            v=v[:-1]
                        atoi(v)
                    else: v=str(int(v))
                except ValueError:
                    raise ValueError(
                        'Invalid integer value for <em>%s</em>' % name)
            elif t=='float':
                if not v and type(v) is StringType: continue
                try:
                    if type(v) is StringType: atof(v)
                    else: v=str(float(v))
                except ValueError:
                    raise ValueError(
                        'Invalid floating-point value for <em>%s</em>' % name)
            elif t.startswith('datetime'):
                # For subsecond precision, use 'datetime(N)' MySQL type,
                # where N is the number of digits after the decimal point.
                n = 0 if t == 'datetime' else int(t[9])
                v = (v if isinstance(v, DateTime) else DateTime(v)).toZone('UTC')
                v = "'%s%s'" % (v.ISO(),
                    ('.%06u' % (v.micros() % 1000000))[:1+n] if n else '')

            else:
                if not isinstance(v, (str, unicode)):
                    v = str(v)
                v=md.getitem('sql_quote__',0)(v)
                #if find(v,"\'") >= 0: v=join(split(v,"\'"),"''")
                #v="'%s'" % v
            vs.append(v)

        if not vs and t=='nb':
            if 'optional' in args and args['optional']:
                return ''
            else:
                raise ValueError(
                    'Invalid empty string value for <em>%s</em>' % name)

        if not vs:
            if self.optional: return ''
            raise ValueError(
                'No input was provided for <em>%s</em>' % name)

        if len(vs) > 1:
            vs=join(map(str,vs),', ')
            if self.op == '<>':
                ## Do the equivalent of 'not-equal' for a list,
                ## "a not in (b,c)"
                return "%s not in (%s)" % (self.column, vs)
            else:
                ## "a in (b,c)"
                return "%s in (%s)" % (self.column, vs)
        return "%s %s %s" % (self.column, self.op, vs[0])
    SQLTest.render = SQLTest.__call__ = render

sqltest.valid_type = (('int', 'float', 'string', 'nb', 'datetime') + tuple('datetime(%s)' % x for x in xrange(7))).__contains__
