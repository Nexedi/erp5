##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
'''Inserting values with the 'ldifvar' tag

    The 'ldifvar' tag is used to type-safely insert values into LDIF
    text.  The 'ldifvar' tag is similar to the 'var' tag, except that
    it replaces text formatting parameters with LDIF type information.

    The sqlvar tag has the following attributes:

      attr -- The name of the attribute to insert. As with other
              DTML tags.

      type -- The data type of the value to be inserted.  This
              attribute is required and may be one of 'string',
              'int', 'float', or 'nb'.  The 'nb' data type indicates a
              string that must have a length that is greater than 0.

      optional -- A flag indicating that a value is optional.  If a
                  value is optional and is not provided (or is blank
                  when a non-blank value is expected), then the string
                  'null' is inserted.

    For example, given the tag::

      <dtml-ldifvar x attr=objectClass type=nb optional>

    if the value of 'x' is::
      
      inetOrgPerson

    then the text inserted is:

      objectClass: inetOrgPerson

    however, if x is ommitted or an empty string, then the value
    inserted is ''.
'''
#__rcs_id__='$Id: sqlvar.py,v 1.14.10.2 2005/09/02 23:02:00 tseaver Exp $'

############################################################################
#     Copyright
#
#       Copyright 1996 Digital Creations, L.C., 910 Princess Anne
#       Street, Suite 300, Fredericksburg, Virginia 22401 U.S.A. All
#       rights reserved.
#
############################################################################
#__version__='$Revision: 1.14.10.2 $'[11:-2]

from DocumentTemplate.DT_Util import ParseError, parse_params, name_param
from string import find, split, join, atoi, atof
import sha
StringType=type('')

str=__builtins__['str']

class LDIFVar:
    name='ldifvar'

    def __init__(self, args):
        args = parse_params(args, name='', expr='', type=None, optional=1)

        name,expr=name_param(args,'ldifvar',1)
        if expr is None: expr=name
        else: expr=expr.eval
        self.__name__, self.expr = name, expr

        self.args=args
        if not args.has_key('type'):
            raise ParseError, ('the type attribute is required', 'dtvar')
        t=args['type']
        if not valid_type(t):
            raise ParseError, ('invalid type, %s' % t, 'dtvar')

    def render(self, md):
        name=self.__name__
        args=self.args
        t=args['type']
        try:
            expr=self.expr
            if type(expr) is type(''): v=md[expr]
            else: v=expr(md)
        except:
            if args.has_key('optional') and args['optional']:
                return
            if type(expr) is not type(''):
                raise
            raise ValueError, 'Missing input variable, <em>%s</em>' % name

        if v is None:
            return ''

        if t=='int':
            try:
                if type(v) is StringType:
                    if v[-1:]=='L':
                        v=v[:-1]
                    atoi(v)
                else: v=str(int(v))
            except:
                if not v and args.has_key('optional') and args['optional']:
                    return
                raise ValueError, (
                    'Invalid integer value for <em>%s</em>' % name)
        elif t=='float':
            try:
                if type(v) is StringType:
                    if v[-1:]=='L':
                        v=v[:-1]
                    atof(v)
                else: v=str(float(v))
            except:
                if not v and args.has_key('optional') and args['optional']:
                    return
                raise ValueError, (
                    'Invalid floating-point value for <em>%s</em>' % name)

        else:
            if not isinstance(v, (str, unicode)):
                v=str(v)
            if not v and t=='nb':
                if args.has_key('optional') and args['optional']:
                    return
                else:
                    raise ValueError, (
                        'Invalid empty string value for <em>%s</em>' % name)

        return v

    __call__=render

class LDIFLine:
    name='ldifline'

    def __init__(self, args):
        args = parse_params(args, name='', expr='', attr='', type=None, optional=1)

        name,expr=name_param(args,'ldifvar',1)
        if expr is None: expr=name
        else: expr=expr.eval
        self.__name__, self.expr = name, expr

        self.args=args
        if not args.has_key('type'):
            raise ParseError, ('the type attribute is required', 'ldifattr')
        t=args['type']
        if not valid_type(t):
            raise ParseError, ('invalid type, %s' % t, 'dtvar')
        
        if not args.has_key('attr'):
            raise ParseError, ('the attr attribute is required', 'ldifattr')
        a=args['attr']

    def render(self, md):
        name=self.__name__
        args=self.args
        t=args['type']
        a=args['attr']
        default = '%s:' % (a)
        try:
            expr=self.expr
            if type(expr) is type(''): v=md[expr]
            else: v=expr(md)
        except:
            if args.has_key('optional') and args['optional']:
                return default
            if type(expr) is not type(''):
                raise
            raise ValueError, 'Missing input variable, <em>%s</em>' % name

        if v is None:
            if args.has_key('optional') and args['optional']:
                return default
            else:
                raise ValueError, 'Missing input variable, <em>%s</em>' % name
        if a in ['',None]:
            return default

        if t=='int':
            try:
                if type(v) is StringType:
                    if v[-1:]=='L':
                        v=v[:-1]
                    atoi(v)
                else: v=str(int(v))
            except:
                if not v and args.has_key('optional') and args['optional']:
                    return default
                raise ValueError, (
                    'Invalid integer value for <em>%s</em>' % name)
        elif t=='float':
            try:
                if type(v) is StringType:
                    if v[-1:]=='L':
                        v=v[:-1]
                    atof(v)
                else: v=str(float(v))
            except:
                if not v and args.has_key('optional') and args['optional']:
                    return default
                raise ValueError, (
                    'Invalid floating-point value for <em>%s</em>' % name)

        else:
            if not isinstance(v, (str, unicode)):
                v=str(v)
            if not v and t=='nb':
                if args.has_key('optional') and args['optional']:
                    return default
                else:
                    raise ValueError, (
                        'Invalid empty string value for <em>%s</em>' % name)

        return '%s: %s' % (a, v)

    __call__=render

valid_type={'int':1, 'float':1, 'string':1, 'nb': 1}.has_key
