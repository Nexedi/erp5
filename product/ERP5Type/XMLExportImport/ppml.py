# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2001,2002 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Provide conversion between Python pickles and XML
"""

# XXX-zope4py3: Python3 C implementation does not have Unpickler.dispatch
# attribute. dispatch_table should be used instead.
from zodbpickle.slowpickle import *

import struct

import six
if six.PY2:
  from base64 import encodestring as base64_encodebytes, decodestring as base64_decodebytes
else:
  from base64 import encodebytes as base64_encodebytes, decodebytes as base64_decodebytes
import re
from marshal import loads as mloads
from .xyap import NoBlanks
from .xyap import xyap
from Products.ERP5Type.Utils import str2bytes

from marshal import dumps as mdumps
#from zLOG import LOG

binary = re.compile('[^\x1f-\x7f]').search

if six.PY2:
  data_encoding = 'raw_unicode_escape'
  long_ = long
else:
  data_encoding = 'utf-8'
  long_ = int

def escape(s, encoding='repr'):
    if binary(s) and isinstance(s, str):
        s = base64_encodebytes(s)[:-1]
        encoding = 'base64'
    elif '>' in s or '<' in s or '&' in s:
        if not ']]>' in s:
            s = '<![CDATA[' + s + ']]>'
            encoding = 'cdata'
        else:
            s = s.replace('&', '&amp;')
            s = s.replace('>', '&gt;')
            s = s.replace('<', '&lt;')
    return encoding, s

def unescape(s, encoding):
    if encoding == 'base64':
        return base64_decodebytes(s)
    else:
        s = s.replace(b'&lt;', b'<')
        s = s.replace(b'&gt;', b'>')
        return s.replace(b'&amp;', b'&')

# For converting to a more readable expression.
reprs = {}
### patch begin: create a conversion table for [\x00-\x1f]. this table is
###              used for a valid utf-8 string.
for c in map(chr, range(32)): reprs[c] = repr(c)[1:-1]
### patch end
reprs['\n'] = "\\n\n"
reprs['\t'] = "\\t"
reprs['\\'] = "\\\\"
reprs['\r'] = "\\r"
reprs["'"] = "\\'"
reprs2={}
reprs2['<'] = "\\074"
reprs2['>'] = "\\076"
reprs2['&'] = "\\046"
reprs_re = re.compile('|'.join(re.escape(k) for k in reprs.keys()))
def sub_reprs(m):
  return reprs[m.group(0)]
reprs2_re = re.compile('|'.join(re.escape(k) for k in reprs2.keys()))
def sub_reprs2(m):
  return reprs2[m.group(0)]
def convert(S):
    new = ''
    ### patch begin: if the input string is a valid utf8 string, only
    ###              [\x00-\x1f] characters will be escaped to make a more
    ###              readable output.
    try:
        if not isinstance(S, six.text_type):
            S = S.decode('utf8')
    except UnicodeDecodeError:
        return 'base64', base64_encodebytes(S)[:-1]
    else:
        new = reprs_re.sub(sub_reprs, S)
    ### patch end
    if len(new) > (1.4*len(S)):
        if not isinstance(S, six.binary_type):
            # TODO zope4py3: is this the right place ? this supports Unicode('\n')
            S = S.encode('ascii')
        return 'base64', base64_encodebytes(S)[:-1]
    elif '>' in new or '<' in S or '&' in S:
        if not ']]>' in S:
            return 'cdata', '<![CDATA[\n\n' + new + '\n\n]]>'
        else:
            return 'repr', reprs2_re.sub(sub_reprs2, new)
    return 'repr', new

# For optimization.
def unconvert(encoding,S):
    if encoding == 'base64':
        return base64_decodebytes(S)
    else:
        return str2bytes(eval(b"'" + S.replace(b'\n', b'') + b"'"))

class Global:
    def __init__(self, module, name, mapping):
        self.module=module
        self.name=name
        self.mapping = mapping

    def __str__(self, indent=0):
        id = ''
        if hasattr(self, 'id'):
            if self.mapping.isMarked(self.id): id=' id="%s"' % self.mapping[self.id]
        name=self.__class__.__name__.lower()
        return '%s<%s%s name="%s" module="%s"/>\n' % (
            ' '*indent, name, id, self.name, self.module)

class Immutable:
    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

class Scalar:
    def __init__(self, v, mapping):
        self._v=v
        self.mapping = mapping

    def value(self): return self._v

    def __str__(self, indent=0):
        id = ''
        name=self.__class__.__name__.lower()
        result = '%s<%s%s>%s</%s>\n' % (
            ' '*indent, name, id, self.value(), name)
        if hasattr(self, 'id'):
            # The value is Immutable - let us add it the the immutable mapping
            # to reduce the number of unreadable references
            self.mapping.setImmutable(self.id, Immutable(value = result))
        return result

class Long(Scalar):
    def value(self):
        result = str(self._v)
        if result[-1:] == 'L':
            return result[:-1]
        return result

class String(Scalar):

    def tag_name(self):
        return self.__class__.__name__.lower()

    encoding = None

    def __init__(self, v, mapping, encoding=''):
        self._v=v
        self.mapping = mapping

    def __str__(self,indent=0,map_value=0):
        encoding = self.encoding
        if encoding is None:
            # lazy conversion
            if map_value:
                # This is used when strings represent references which need to
                # be converted.
                encoding = 'base64'
                v = base64_encodebytes(self._v)[:-1]
                self._v = self.mapping.convertBase64(v).decode()
            else:
                encoding, self._v = convert(self._v)
            self.encoding = encoding
        v = self.value()
        id = ''
        if encoding == 'repr':
            encoding = '' # JPS repr is default encoding
        else:
            encoding = ' encoding="%s"' % encoding
        name = self.tag_name()
        result = '<%s%s%s>%s</%s>' % (name, id, encoding, v, name)
        if hasattr(self, 'id'):
            # The value is Immutable - let us add it the the immutable mapping
            # to reduce the number of unreadable references
            self.mapping.setImmutable(self.id, Immutable(value = result))
        return '%s%s\n' % (' '*indent, result)

class Unicode(String):
    def tag_name(self):
        if six.PY3:
            return 'string'
        return super(Unicode, self).tag_name()

class Bytes(String):
    pass


class Wrapper:
    def __init__(self, v, mapping):
        self._v=v
        self.mapping = mapping

    def value(self): return self._v

    def __str__(self, indent=0):
        id = ''
        if hasattr(self, 'id'):
            if self.mapping.isMarked(self.id): id=' id="%s"' % self.mapping[self.id]
        name=self.__class__.__name__.lower()
        v=self._v
        i=' '*indent
        if isinstance(v,Scalar):
            return '%s<%s%s> %s </%s>\n' % (i, name, id, str(v)[:-1], name)
        else:
            v=v.__str__(indent+2)
            return '%s<%s%s>\n%s%s</%s>\n' % (i, name, id, v, i, name)

class Collection:
    def __init__(self, mapping):
        self.mapping = mapping

    def __str__(self, indent=0):
        id = ''
        if hasattr(self, 'id'):
            if self.mapping.isMarked(self.id): id=' id="%s"' % self.mapping[self.id]
        name=self.__class__.__name__.lower()
        i=' '*indent
        if self:
            return '%s<%s%s>\n%s%s</%s>\n' % (
                i, name, id, self.value(indent+2), i, name)
        else:
            return '%s<%s%s/>\n' % (i, name, id)

class Dictionary(Collection):
    def __init__(self, mapping):
        self.mapping = mapping
        self._d=[]

    def __len__(self): return len(self._d)

    def __setitem__(self, k, v): self._d.append((k,v))

    def value(self, indent):
        #self._d.sort(lambda a, b: cmp(a[0]._v, b[0]._v)) # Sort the sequence by key JPS Improvement
        ind = ' ' * indent
        indent = indent + 4
        return ''.join(
            '%s<item>\n%s%s%s</item>\n'
                %
                (ind,
                 Key(i[0], self.mapping).__str__(indent),
                 Value(i[1], self.mapping).__str__(indent),
                 ind)
                 for i in self._d
            )

class Sequence(Collection):
    def __init__(self, mapping, v=None):
        if not v: v=[]
        self._subs=v
        self.mapping = mapping

    def __len__(self): return len(self._subs)

    def append(self, v): self._subs.append(v)

    # Bugfix JPS
    def extend(self, v): self._subs.extend(v)

    def value(self, indent):
        return ''.join(
            v.__str__(indent) for v in
            self._subs)

class none:
    def __str__(self, indent=0):
        return ' ' * indent + '<none/>\n'
none = none()

class Reference(Scalar):
    def __init__(self, v, mapping):
        self._v=v
        self.mapping = mapping
        mapping.mark(v)
    def __str__(self, indent=0):
        v=self._v
        #LOG('Reference', 0, str(v))
        if self.mapping.hasImmutable(v):
          value = self.mapping.getImmutable(v).getValue()
        else:
          name = self.__class__.__name__.lower()
          #LOG('noImmutable', 0, "%s mapped to %s" % (v, self.mapping[v]))
          value = '<%s id="%s"/>' % (name, self.mapping[v])
        return '%s%s\n' % (' '*indent, value)

Get = Reference

class Object(Sequence):
    def __init__(self, klass, args, mapping):
        self._subs=[Klass(klass, mapping), args]
        self.mapping = mapping

    def __setstate__(self, v): self.append(State(v, self.mapping))

class Int(Scalar): pass
class Float(Scalar): pass
class List(Sequence): pass
class Tuple(Sequence): pass
class Key(Wrapper): pass
class Value(Wrapper): pass
class Klass(Wrapper): pass
class State(Wrapper): pass
class Pickle(Wrapper): pass

class Persistent(Wrapper):
    def __str__(self, indent=0):
        id = ''
        if hasattr(self, 'id'):
            if self.mapping.isMarked(self.id): id=' id="%s"' % self.mapping[self.id]
        name=self.__class__.__name__.lower()
        v=self._v
        i=' '*indent
        if isinstance(v,String):
            return '%s<%s%s> %s </%s>\n' % (i, name, id, v.__str__(map_value=1)[:-1], name)
        elif isinstance(v,Scalar):
            return '%s<%s%s> %s </%s>\n' % (i, name, id, str(v)[:-1], name)
        else:
            v=v.__str__(indent+2)
            return '%s<%s%s>\n%s%s</%s>\n' % (i, name, id, v, i, name)

blanck_line_expression = re.compile('^ +$')
class NoBlanks:
    """
    This allows to ignore at least whitespaces between elements and also
    correctly handle string/unicode
    """
    previous_stack_end = None
    previous_discarded_data = None

    def handle_data(self, data):
        """
        Called for each character lines of element data, twice in this
        example:

        <string>abc
        bar</string>
        """
        # Ignore element data between elements (eg '<e> <f> </f> </e>')...
        if data.strip():
            if isinstance(data, six.text_type):
                data = data.encode(data_encoding)
            self.append(data)

        # Except for strings and unicode data as whitespaces should be
        # kept. It happened that javascript files with a line like " ];\n" was
        # replaced by "];\n", so the indent was lost. Indeed the parser was
        # calling this handle_data function first for " ", then for "];". So
        # original code was dropping the " ".
        elif (isinstance(self._stack[-1], list) and
              self._stack[-1][0] in ('string', 'unicode')):
            # If the first character data of this element is a whitespace, it
            # will be concatenated with the next line (if any, but at
            # this point it is not possible to know anyway)
            if len(self._stack[-1]) == 2:
                self.previous_stack_end = self._stack[-1]
                self.previous_discarded_data = data
            else:
                if (self._stack[-1] == self.previous_stack_end and
                    self.previous_discarded_data):
                    data = self.previous_discarded_data + data
                    self.previous_discarded_data = None
                    self.previous_stack_end = None

                if isinstance(data, six.text_type):
                    data = data.encode(data_encoding)

                self.append(data)

class IdentityMapping:
    def __init__(self):
      self.resetMapping()
      self.immutable = {}

    def resetMapping(self):
      pass

    def __getitem__(self, id):
      return id

    def setConvertedAka(self, old, new):
      pass

    def convertBase64(self, s):
      return s

    def mark(self, v):
      pass

    def isMarked(self, v):
      return 1

    def setImmutable(self, k, v):
      self.immutable[k] = v

    def getImmutable(self, k):
      return self.immutable[k]

    def hasImmutable(self, k):
      return k in self.immutable

class MinimalMapping(IdentityMapping):
    def resetMapping(self):
      self.mapped_id = {}
      self.mapped_core_id = {}
      self.last_sub_id = {}
      self.last_id = 1
      self.converted_aka = {}
      self.marked_reference = set()

    def __getitem__(self, id):
      id = str(id)
      split_id = id.split('.')
      if len(split_id) == 2:
        (core_id, sub_id) = split_id
      elif len(split_id) == 1:
        core_id = split_id[0]
        sub_id = None
      else:
        raise
      if core_id not in self.mapped_id:
        if sub_id is not None:
          # Use existing id
          self.mapped_id[core_id] = {}
          self.mapped_core_id[core_id] = self.last_id - 1
          self.last_sub_id[core_id] = 1
        else:
          # Create new core_id if not defined
          self.mapped_id[core_id] = {}
          self.mapped_core_id[core_id] = self.last_id
          self.last_sub_id[core_id] = 1
          self.last_id = self.last_id + 1
      if sub_id is None:
        return self.mapped_core_id[core_id]
      if sub_id not in self.mapped_id[core_id]:
        # Create new sub_id if not defined
        self.mapped_id[core_id][sub_id] = self.last_sub_id[core_id]
        self.last_sub_id[core_id] = self.last_sub_id[core_id] + 1
      return "%s.%s" % (self.mapped_core_id[core_id], self.mapped_id[core_id][sub_id])

    def convertBase64(self, s):
      return self.converted_aka.get(s, s)

    def setConvertedAka(self, old, new):
      self.converted_aka[old] =  new

    def mark(self, v):
      self.marked_reference.add(v)

    def isMarked(self, v):
      return v in self.marked_reference

    def __str__(self, a):
      return "Error here"

class ToXMLUnpickler(Unpickler):
    def load(self, id_mapping=None):
      if id_mapping is None:
        self.id_mapping = IdentityMapping()
      else:
        self.id_mapping = id_mapping
      return Pickle(Unpickler.load(self), self.id_mapping)

    dispatch = {}
    dispatch.update(Unpickler.dispatch.copy())

    def persistent_load(self, v):
        return Persistent(v, self.id_mapping)

    def load_persid(self):
        pid = self.readline()[:-1]
        self.append(self.persistent_load(String(pid, self.id_mapping)))
    if six.PY2:
        dispatch[PERSID] = load_persid
    dispatch[PERSID[0]] = load_persid

    def load_binpersid(self):
        pid = self.stack.pop()
        self.append(self.persistent_load(pid))
    if six.PY2:
        dispatch[BINPERSID] = load_binpersid
    dispatch[BINPERSID[0]] = load_binpersid

    def load_none(self):
        self.append(none)
    if six.PY2:
        dispatch[NONE] = load_none
    dispatch[NONE[0]] = load_none

    def load_int(self):
        self.append(Int(int(self.readline()[:-1]), self.id_mapping))
    if six.PY2:
        dispatch[INT] = load_int
    dispatch[INT[0]] = load_int

    def load_binint(self):
        self.append(Int(mloads(b'i' + self.read(4)), self.id_mapping))
    if six.PY2:
        dispatch[BININT] = load_binint
    dispatch[BININT[0]] = load_binint

    def load_binint1(self):
        self.append(Int(mloads(b'i' + self.read(1) + b'\000\000\000'), self.id_mapping))
    if six.PY2:
        dispatch[BININT1] = load_binint1
    dispatch[BININT1[0]] = load_binint1

    def load_binint2(self):
        self.append(Int(mloads(b'i' + self.read(2) + b'\000\000'), self.id_mapping))
    if six.PY2:
        dispatch[BININT2] = load_binint2
    dispatch[BININT2[0]] = load_binint2

    def load_long(self):
        self.append(Long(long_(self.readline()[:-1], 0), self.id_mapping))
    if six.PY2:
        dispatch[LONG] = load_long
    dispatch[LONG[0]] = load_long

    def load_float(self):
        self.append(Float(float(self.readline()[:-1]), self.id_mapping))
    if six.PY2:
        dispatch[FLOAT] = load_float
    dispatch[FLOAT[0]] = load_float

    def load_binfloat(self, unpack=struct.unpack):
        self.append(Float(unpack('>d', self.read(8))[0], self.id_mapping))
    if six.PY2:
        dispatch[BINFLOAT] = load_binfloat
    dispatch[BINFLOAT[0]] = load_binfloat

    def load_string(self):
        self.append(String(eval(self.readline()[:-1],
                                {'__builtins__': {}}), self.id_mapping)) # Let's be careful
    if six.PY2:
        dispatch[STRING] = load_string
    dispatch[STRING[0]] = load_string

    def load_binstring(self):
        len = mloads(b'i' + self.read(4))
        self.append(String(self.read(len), self.id_mapping))
    if six.PY2:
        dispatch[BINSTRING] = load_binstring
    dispatch[BINSTRING[0]] = load_binstring

    def load_unicode(self):
        line = self.readline()
        self.append(Unicode(six.text_type(eval(line[:-1],
                                         {'__builtins__': {}})), self.id_mapping)) # Let's be careful
    if six.PY2:
        dispatch[UNICODE] = load_unicode
    dispatch[UNICODE[0]] = load_unicode

    def load_binunicode(self):
        len = mloads(b'i' + self.read(4))
        self.append(Unicode(six.text_type(self.read(len), 'utf-8'), self.id_mapping))
    if six.PY2:
        dispatch[BINUNICODE] = load_binunicode
    dispatch[BINUNICODE[0]] = load_binunicode

    def load_short_binstring(self):
        len = mloads(b'i' + self.read(1) + b'\000\000\000')
        self.append(String(self.read(len), self.id_mapping))
    if six.PY2:
        dispatch[SHORT_BINSTRING] = load_short_binstring
    dispatch[SHORT_BINSTRING[0]] = load_short_binstring

    def load_binbytes(self):
        len = mloads(b'i' + self.read(4))
        self.append(Bytes(self.read(len), self.id_mapping))
    if six.PY2:
        dispatch[BINBYTES] = load_binbytes
    dispatch[BINBYTES[0]] = load_binbytes

    def load_short_binbytes(self):
        len = mloads(b'i' + self.read(1) + b'\000\000\000')
        self.append(Bytes(self.read(len), self.id_mapping))
    if six.PY2:
        dispatch[SHORT_BINBYTES] = load_short_binbytes
    dispatch[SHORT_BINBYTES[0]] = load_short_binbytes

    def load_tuple(self):
        k = self.marker()
        #LOG('load_tuple, k',0,k)
        #LOG('load_tuple, stack[k+1:]',0,self.stack[k+1:])
        self.stack[k:] = [Tuple(self.id_mapping, v=self.stack[k+1:])]
    if six.PY2:
        dispatch[TUPLE] = load_tuple
    dispatch[TUPLE[0]] = load_tuple

    def load_tuple1(self):
        self.stack[-1] = Tuple(self.id_mapping, v=(self.stack[-1],))
    if six.PY2:
        dispatch[TUPLE1] = load_tuple1
    dispatch[TUPLE1[0]] = load_tuple1

    def load_tuple2(self):
        self.stack[-2:] = [Tuple(self.id_mapping, v=(self.stack[-2], self.stack[-1]))]
    if six.PY2:
        dispatch[TUPLE2] = load_tuple2
    dispatch[TUPLE2[0]] = load_tuple2

    def load_tuple3(self):
        self.stack[-3:] = [Tuple(self.id_mapping, v=(self.stack[-3], self.stack[-2], self.stack[-1]))]
    if six.PY2:
        dispatch[TUPLE3] = load_tuple3
    dispatch[TUPLE3[0]] = load_tuple3

    def load_empty_tuple(self):
        self.stack.append(Tuple(self.id_mapping))
    if six.PY2:
        dispatch[EMPTY_TUPLE] = load_empty_tuple
    dispatch[EMPTY_TUPLE[0]] = load_empty_tuple

    def load_empty_list(self):
        self.stack.append(List(self.id_mapping))
    if six.PY2:
        dispatch[EMPTY_LIST] = load_empty_list
    dispatch[EMPTY_LIST[0]] = load_empty_list

    def load_empty_dictionary(self):
        self.stack.append(Dictionary(self.id_mapping))
    if six.PY2:
        dispatch[EMPTY_DICT] = load_empty_dictionary
    dispatch[EMPTY_DICT[0]] = load_empty_dictionary

    def load_list(self):
        k = self.marker()
        self.stack[k:] = [List(self.id_mapping, v=self.stack[k+1:])]
    if six.PY2:
        dispatch[LIST] = load_list
    dispatch[LIST[0]] = load_list

    def load_dict(self):
        k = self.marker()
        d = Dictionary(self.id_mapping)
        items = self.stack[k+1:]
        for i in range(0, len(items), 2):
            key = items[i]
            value = items[i+1]
            d[key] = value
        self.stack[k:] = [d]
    if six.PY2:
        dispatch[DICT] = load_dict
    dispatch[DICT[0]] = load_dict

    def load_inst(self):
        k = self.marker()
        args = Tuple(self.id_mapping, v=self.stack[k+1:])
        del self.stack[k:]
        module = self.readline()[:-1].decode()
        name = self.readline()[:-1].decode()
        value=Object(Global(module, name, self.id_mapping), args, self.id_mapping)
        self.append(value)
    if six.PY2:
        dispatch[INST] = load_inst
    dispatch[INST[0]] = load_inst

    def load_obj(self):
        stack = self.stack
        k = self.marker()
        klass = stack[k + 1]
        del stack[k + 1]
        args = Tuple(self.id_mapping, v=stack[k + 1:])
        del stack[k:]
        value=Object(klass,args, self.id_mapping)
        self.append(value)
    if six.PY2:
        dispatch[OBJ] = load_obj
    dispatch[OBJ[0]] = load_obj
    
    def load_newobj(self):
        # TODO: not really sure of this one, maybe we need
        # a NewObj instead of Object
        args = self.stack.pop()
        cls = self.stack[-1]
        obj = Object(cls, args, self.id_mapping)
        self.stack[-1] = obj
        #print('load_newobj', self.stack)
    if six.PY2:
        dispatch[NEWOBJ] = load_newobj
    dispatch[NEWOBJ[0]] = load_newobj

    def load_global(self):
        module = self.readline()[:-1].decode()
        name = self.readline()[:-1].decode()
        self.append(Global(module, name, self.id_mapping))
    if six.PY2:
        dispatch[GLOBAL] = load_global
    dispatch[GLOBAL[0]] = load_global

    def load_reduce(self):
        stack = self.stack

        callable = stack[-2]
        arg_tup  = stack[-1]
        del stack[-2:]

        value=Object(callable, arg_tup, self.id_mapping)
        self.append(value)
    if six.PY2:
        dispatch[REDUCE] = load_reduce
    dispatch[REDUCE[0]] = load_reduce

    idprefix=''

    def load_get(self):
        self.append(Get(self.idprefix+self.readline()[:-1], self.id_mapping))
    if six.PY2:
        dispatch[GET] = load_get
    dispatch[GET[0]] = load_get

    def load_binget(self):
        i = mloads(b'i' + self.read(1) + b'\000\000\000')
        self.append(Get(self.idprefix+repr(i), self.id_mapping))
    if six.PY2:
        dispatch[BINGET] = load_binget
    dispatch[BINGET[0]] = load_binget

    def load_long_binget(self):
        i = mloads(b'i' + self.read(4))
        self.append(Get(self.idprefix+repr(i), self.id_mapping))
    if six.PY2:
        dispatch[LONG_BINGET] = load_long_binget
    dispatch[LONG_BINGET[0]] = load_long_binget

    def load_put(self):
        self.stack[-1].id=self.idprefix+self.readline()[:-1]
    if six.PY2:
        dispatch[PUT] = load_put
    dispatch[PUT[0]] = load_put

    def load_binput(self):
        i = mloads(b'i' + self.read(1) + b'\000\000\000')
        self.stack[-1].id=self.idprefix+repr(i)
    if six.PY2:
        dispatch[BINPUT] = load_binput
    dispatch[BINPUT[0]] = load_binput

    def load_long_binput(self):
        i = mloads(b'i' + self.read(4))
        self.stack[-1].id=self.idprefix+repr(i)
    if six.PY2:
        dispatch[LONG_BINPUT] = load_long_binput
    dispatch[LONG_BINPUT[0]] = load_long_binput

    class LogCall:
      def __init__(self, func):
        self.func = func

      def __call__(self, context):
        #LOG('LogCall', 0, 'self.stack = %r, func = %s' % (context.stack, self.func.__name__))
        return self.func(context)

    # for code in dispatch.keys():
    #   dispatch[code] = LogCall(dispatch[code])

def ToXMLload(file):
    return ToXMLUnpickler(file).load()

def ToXMLloads(str):
    from six import StringIO
    file = StringIO(str)
    return ToXMLUnpickler(file).load()

def name(self, tag, data):
    return b''.join(data[2:]).strip()

def start_pickle(self, tag, attrs):
    self._pickleids = {}
    return [tag, attrs]

def save_int(self, tag, data):
    if self.binary:
        v = int(name(self, tag, data))
        if v >= 0:
            if v <= 0xff:
                return BININT1 + six.int2byte(v)
            if v <= 0xffff:
                return BININT2 + b'%c%c' % (v & 0xff, v >> 8)
        hb = v >> 31
        if hb == 0 or hb == -1:
            return BININT + struct.pack('<i', v)
    return INT + name(self, tag, data) + b'\n'

def save_float(self, tag, data):
    if self.binary:
        return BINFLOAT + struct.pack('>d', float(name(self, tag, data)))
    else:
        return FLOAT + name(self, tag, data) + b'\n'

def save_put(self, v, attrs):
    id = attrs.get('id', '')
    if id:
        prefix = id.rfind('.')
        if prefix >= 0:
            id = id[prefix + 1:]
        elif id[0] == 'i':
            id = id[1:]
        if self.binary:
            id = int(id)
            if id < 256:
                id = BINPUT + six.int2byte(id)
            else:
                id = LONG_BINPUT + struct.pack('<i', id)
        else:
            id = PUT + repr(id) + b'\n'
        return v + id
    return v

def save_string(self, tag, data):
    a = data[1]
    v = b''.join(data[2:])
    encoding = a.get('encoding', 'repr') # JPS: repr is default encoding
    if encoding != '':
        v = unconvert(encoding, v)
    if self.binary:
        l = len(v)
        if l < 256:
            if encoding == 'base64':
              # TODO: zope4py3 (all this is unfinished)
              # We can be here for two reasons:
              # - the input was a string with \n or similar control characters
              # that are not allowed in XML, so the str was exported as base64.
              # - the input was a _p_oid exported from python2, in that case
              # we want to get a zodbpickle.binary back
              # XXX all this seems a bad idea, we need more context if we want
              # to have such heuristics
              if len(v) == 8:
                  # looks like a _p_oid, assume it is a persistent_id -> bytes
                  op = SHORT_BINBYTES
              else:
                  # if it's a valid UTF-8 string -> str
                  try:
                      v.decode('utf-8')
                      # XXX maybe check with repr_re ?
                      op = BINUNICODE
                      v = op + struct.pack('<i', l) + v
                      return save_put(self, v, a)
                  except UnicodeDecodeError:
                      # not valid utf-8 -> bytes
                      op = SHORT_BINBYTES
            else:
              # XXX this branch seems wrong
              op = SHORT_BINSTRING
              try:
                  v.decode('ascii')
                  # XXX zope4py3 we could also create an unpickler with encoding utf-8 ?
              except UnicodeDecodeError:
                  op = BINUNICODE
                  v = op + struct.pack('<i', l) + v
                  return save_put(self, v, a)

            v = op + six.int2byte(l) + v
        else:
            # TODO: zope4py3 see assumption above for SHORT_BINBYTES / SHORT_BINSTRING
            # TODO no! check this more ...
            # op = BINSTRING
            if encoding == 'base64':
                op = BINBYTES
            else:
                op = BINSTRING if six.PY2 else BINUNICODE

            v = op + struct.pack('<i', l) + v
    else:
        v = STRING + repr(v) + '\n'
    return save_put(self, v, a)

def save_bytes(self, tag, data):
    a = data[1]
    v = b''.join(data[2:])
    encoding = a.get('encoding', 'repr')
    assert encoding == 'base64'
    if encoding != '':
        v = unconvert(encoding, v)
    if self.binary:
        l = len(v)
        if l < 256:
            op = SHORT_BINBYTES
            v = op + six.int2byte(l) + v
        else:
            op = BINBYTES
            v = op + struct.pack('<i', l) + v
    else:
        # XXX used ??? seems wrong
        v = BYTES + repr(v) + '\n'
    return save_put(self, v, a)


def save_unicode(self, tag, data):
    binary=self.binary
    v=b''
    a=data[1]
    if len(data)>2:
        for x in data[2:]:
            v=v+x
    encoding=a.get('encoding','repr') # JPS: repr is default encoding
    if encoding != '':
        v=unconvert(encoding,v)
    if binary:
        l=len(v)
        s=mdumps(l)[1:]
        v=BINUNICODE+s+v
    else: v=UNICODE+"'"+v+"'\012"
    return save_put(self, v, a)

def save_tuple(self, tag, data):
    T = data[2:]
    if not T:
        return EMPTY_TUPLE
    return save_put(self, MARK + b''.join(T) + TUPLE, data[1])

def save_list(self, tag, data):
    L = data[2:]
    if self.binary:
        v = save_put(self, EMPTY_LIST, data[1])
        if L:
            v = v + MARK + b''.join(L) + APPENDS
    else:
        v = save_put(self, MARK + LIST, data[1])
        if L:
            v = APPEND.join(L) + APPEND
    return v

def save_dict(self, tag, data):
    D = data[2:]
    if self.binary:
        v = save_put(self, EMPTY_DICT, data[1])
        if D:
            v = v + MARK + b''.join(D) + SETITEMS
    else:
        v = save_put(self, MARK + DICT, data[1])
        if D:
            v = v + SETITEM.join(D) + SETITEM
    return v

def save_reference(self, tag, data):
    a = data[1]
    id = a['id']
    prefix = id.rfind('.')
    if prefix >= 0:
        id = id[prefix + 1:]
    if self.binary:
        id = int(id)
        if id < 256:
            return BINGET + six.int2byte(id)
        else:
            return LONG_BINGET + struct.pack('<i', i)
    else:
        return GET + repr(id) + b'\n'

def save_object(self, tag, data):
    if len(data)==5:
        #OBJECT
        v=b'('+data[2]
        x=data[3][1:]
        stop=x.rfind(b't')  # This seems
        if stop>=0: x=x[:stop]    # wrong!
        v=save_put(self, v+x+b'o', data[1])
        v=v+data[4]+b'b' # state
        return v
    else:
        #REDUCE
        #data does not contain state.(See Object.__setstate__ definition)
        #So, we can assume that this is a reduce. (Yusei)
        v=b'('+data[2]
        v=save_put(self, data[2]+data[3], data[1])
        v=v+b'R'
        return v

def save_global(self, tag, data):
    a = data[1]
    return save_put(self, GLOBAL + str2bytes(a['module']) + b'\n' +
                    str2bytes(a['name']) + b'\n', a)

def save_persis(self, tag, data):
    v = data[2]
    if self.binary:
        return v + BINPERSID
    else:
        return PERSID + v

def save_pickle_start(self, tag, attrs):
    return [tag, attrs]

def save_pickle(self, tag, data):
    return data[2] + b'.'

def save_none(self, tag, data):
    return b'N'

def save_long(self, tag, data):
    return b'L'+data[2]+b'L\012'

def save_item(self, tag, data):
    return b''.join(data[2:])

def save_value(self, tag, data):
    return data[2]

class xmlPickler(NoBlanks, xyap):
    # XXX fix a bug in xyap.
    def unknown_endtag(self, tag):
        _stack = self._stack
        top = _stack.pop()
        append = self.append = _stack[-1].append
        end = self.end_handlers
        if tag in end:
            top = end[tag](self, tag, top)
        if isinstance(top, six.text_type):
            top = top.encode(data_encoding)
        append(top)

    start_handlers={
        'pickle': save_pickle_start,
        }
    end_handlers={
        'pickle': save_pickle,
        'none': save_none,
        'int': save_int,
        'long': save_long,
        'float': save_float,
        'bytes': save_bytes,
        'string': save_string,
        'unicode': save_unicode,
        'reference': save_reference,
        'tuple': save_tuple,
        'list': save_list,
        'dictionary': save_dict,
        'item': save_item,
        'value': save_value,
        'key' : save_value,
        'object': save_object,
        'klass': save_value,
        'state': save_value,
        'global': save_global,
        'persistent': save_persis,
        }

