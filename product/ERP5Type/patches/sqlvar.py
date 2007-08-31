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
from types import StringType
from Products.ERP5Type.PsycoWrapper import psyco

def SQLVar_render(self, md):
    name=self.__name__
    args=self.args
    t=args['type']
    try:
        expr=self.expr
        if type(expr) is type(''): v=md[expr]
        else: v=expr(md)
    except:
        if args.has_key('optional') and args['optional']:
            return 'null'
        if type(expr) is not type(''):
            raise
        raise ValueError, 'Missing input variable, <em>%s</em>' % name

    if t=='int':
        try:
            if type(v) is StringType:
                if v[-1:]=='L':
                    v=v[:-1]
                atoi(v)
            else: v=str(int(v))
        except:
            if not v and args.has_key('optional') and args['optional']:
                return 'null'
            raise ValueError, (
                'Invalid integer value for <em>%s</em>: %r' % (name, v))
    elif t=='float':
        try:
            if type(v) is StringType:
                if v[-1:]=='L':
                    v=v[:-1]
                atof(v)
            else: v=str(float(v))
        except:
            if not v and args.has_key('optional') and args['optional']:
                return 'null'
            raise ValueError, (
                'Invalid floating-point value for <em>%s</em>: %r' % (name, v))
    # Patched by yo
    elif t=='datetime':
        if v is None:
            if args.has_key('optional') and args['optional']:
                return 'null'
            else:
                raise ValueError, (
                    'Invalid datetime value for <em>%s</em>: %r' % (name, v))

        try:
            if getattr(v, 'ISO', None) is not None:
                v=v.ISO()
            elif getattr(v, 'strftime', None) is not None:
                v=v.strftime('%Y-%m-%d %H:%M:%S')
            else: 
                v=str(v)
        except:
            if not v and args.has_key('optional') and args['optional']:
                return 'null'
            raise ValueError, (
                'Invalid datetime value for <em>%s</em>: %r' % (name, v))

        v=md.getitem('sql_quote__',0)(v)
    # End of patch
    else:
        # Patched by yo
        if v is None:
            if args.has_key('optional') and args['optional']:
                return 'null'
            else:
                raise ValueError, (
                    'Invalid string value for <em>%s</em>: %r' % (name, v))
        # End of patch

        if not isinstance(v, (str, unicode)):
            v=str(v)
        if not v and t=='nb':
            if args.has_key('optional') and args['optional']:
                return 'null'
            else:
                raise ValueError, (
                    'Invalid empty string value for <em>%s</em>' % name)

        v=md.getitem('sql_quote__',0)(v)
        #if find(v,"\'") >= 0: v=join(split(v,"\'"),"''")
        #v="'%s'" % v

    return v

psyco.bind(SQLVar_render)

# Patched by yo. datetime is added.
valid_type={'int':1, 'float':1, 'string':1, 'nb': 1, 'datetime' : 1}.has_key

SQLVar.render = SQLVar_render
SQLVar.__call__ = SQLVar_render
sqlvar.valid_type = valid_type
