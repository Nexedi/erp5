# -*- coding: utf-8 -*-
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

from builtins import map
from builtins import str
from builtins import range
from builtins import object
import re
from future import standard_library
standard_library.install_aliases()
import six

# Import everything right now, not after
# or new patch will not work
from Shared.DC.xml.ppml import *
from Shared.DC.xml import ppml

from marshal import dumps as mdumps
from zLOG import LOG

# For converting to a more readable expression.
reprs = {}
### patch begin: create a conversion table for [\x00-\x1f]. this table is
###              used for a valid utf-8 string.
for c in map(chr, list(range(32))): reprs[c] = repr(c)[1:-1]
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

reprs_re = re.compile('|'.join(re.escape(k) for k in list(reprs.keys())))
def sub_reprs(m):
  return reprs[m.group(0)]

reprs2_re = re.compile('|'.join(re.escape(k) for k in list(reprs2.keys())))
def sub_reprs2(m):
  return reprs2[m.group(0)]

def convert(S):
    new = ''
    ### patch begin: if the input string is a valid utf8 string, only
    ###              [\x00-\x1f] characters will be escaped to make a more
    ###              readable output.
    try:
        if isinstance(S, bytes):
            S.decode('utf8')
    except UnicodeDecodeError:
        return 'base64', base64.encodestring(S)[:-1]
    else:
        new = reprs_re.sub(sub_reprs, S)
    ### patch end
    if len(new) > (1.4*len(S)):
        return 'base64', base64.encodestring(S)[:-1]
    elif '>' in new or '<' in S or '&' in S:
        if not ']]>' in S:
            return 'cdata', '<![CDATA[\n\n' + new + '\n\n]]>'
        else:
            return 'repr', reprs2_re.sub(sub_reprs2, new)
    return 'repr', new

ppml.convert = convert

# For optimization.
def unconvert(encoding,S):
    if encoding == 'base64':
        return base64.decodestring(S)
    else:
        return bytes(eval(b"'" + S.replace(b'\n', b'') + b"'"), 'utf-8')

ppml.unconvert = unconvert

class Global(object):

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

ppml.Global = Global

class Scalar(object):

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

ppml.Scalar = Scalar

class Immutable(object):
    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

class String(Scalar):

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
                v = base64.encodestring(self._v)[:-1]
                self._v = self.mapping.convertBase64(v)
            else:
                encoding, self._v = convert(self._v)
            self.encoding = encoding
        v = self.value()
        id = ''
        if encoding == 'repr':
            encoding = '' # JPS repr is default encoding
        else:
            encoding = ' encoding="%s"' % encoding
        name=self.__class__.__name__.lower()
        result = '<%s%s%s>%s</%s>' % (name, id, encoding, v, name)
        if hasattr(self, 'id'):
            # The value is Immutable - let us add it the the immutable mapping
            # to reduce the number of unreadable references
            self.mapping.setImmutable(self.id, Immutable(value = result))
        return '%s%s\n' % (' '*indent, result)

ppml.String = String

class Unicode(String):
    def value(self):
        return self._v.encode('utf-8')

ppml.Unicode = Unicode

class Wrapper(object):

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

ppml.Wrapper = Wrapper

class Collection(object):

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

ppml.Collection = Collection

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

ppml.Dictionary = Dictionary

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

ppml.Sequence = Sequence

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

ppml.Persistent = Persistent

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

ppml.Reference = Reference
Get = Reference
ppml.Get = Get

class Object(Sequence):
    def __init__(self, klass, args, mapping):
        self._subs=[Klass(klass, mapping), args]
        self.mapping = mapping

    def __setstate__(self, v): self.append(State(v, self.mapping))

ppml.Object = Object

blanck_line_expression = re.compile('^ +$')

class NoBlanks(object):
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
            if isinstance(data, bytes):
                import pdb; pdb.set_trace()
                data = data.encode('raw_unicode_escape')
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

                if isinstance(data, bytes):
                    import pdb; pdb.set_trace()
                    data = data.encode('raw_unicode_escape')

                self.append(data)

ppml.NoBlanks = NoBlanks

class IdentityMapping(object):

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


ppml.IdentityMapping = IdentityMapping

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

ppml.MinimalMapping = MinimalMapping

class List(Sequence): pass
class Tuple(Sequence): pass

class Klass(Wrapper): pass
class State(Wrapper): pass
class Pickle(Wrapper): pass

class Int(Scalar): pass
class Float(Scalar): pass

class Key(Wrapper): pass
class Value(Wrapper): pass

class Long(Scalar):
    def value(self):
        result = str(self._v)
        if result[-1:] == 'L':
            return result[:-1]
        return result

if six.PY2:
    from pickle import Unpickler
else:
    from pickle import _Unpickler as Unpickler
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
    dispatch[PERSID] = load_persid

    def load_none(self):
        self.append(none)
    dispatch[NONE] = load_none

    def load_int(self):
        self.append(Int(int(self.readline()[:-1]), self.id_mapping))
    dispatch[INT] = load_int

    def load_binint(self):
        self.append(Int(mloads('i' + self.read(4)), self.id_mapping))
    dispatch[BININT] = load_binint

    def load_binint1(self):
        self.append(Int(mloads('i' + self.read(1) + '\000\000\000'), self.id_mapping))
    dispatch[BININT1] = load_binint1

    def load_binint2(self):
        self.append(Int(mloads('i' + self.read(2) + '\000\000'), self.id_mapping))
    dispatch[BININT2] = load_binint2

    def load_long(self):
        self.append(Long(int(self.readline()[:-1], 0), self.id_mapping))
    dispatch[LONG] = load_long

    def load_float(self):
        self.append(Float(float(self.readline()[:-1]), self.id_mapping))
    dispatch[FLOAT] = load_float

    def load_binfloat(self, unpack=struct.unpack):
        self.append(Float(unpack('>d', self.read(8))[0], self.id_mapping))
    dispatch[BINFLOAT] = load_binfloat

    def load_string(self):
        self.append(String(eval(self.readline()[:-1],
                                {'__builtins__': {}}), self.id_mapping)) # Let's be careful
    dispatch[STRING] = load_string

    def load_binstring(self):
        len = mloads('i' + self.read(4))
        self.append(String(self.read(len), self.id_mapping))
    dispatch[BINSTRING] = load_binstring

    def load_unicode(self):
        self.append(Unicode(str(eval(self.readline()[:-1],
                                         {'__builtins__': {}})), self.id_mapping)) # Let's be careful
    dispatch[UNICODE] = load_unicode

    def load_binunicode(self):
        len = mloads('i' + self.read(4))
        self.append(Unicode(str(self.read(len), 'utf-8'), self.id_mapping))
    dispatch[BINUNICODE] = load_binunicode

    def load_short_binstring(self):
        len = mloads('i' + self.read(1) + '\000\000\000')
        self.append(String(self.read(len), self.id_mapping))
    dispatch[SHORT_BINSTRING] = load_short_binstring

    def load_tuple(self):
        k = self.marker()
        #LOG('load_tuple, k',0,k)
        #LOG('load_tuple, stack[k+1:]',0,self.stack[k+1:])
        self.stack[k:] = [Tuple(self.id_mapping, v=self.stack[k+1:])]
    dispatch[TUPLE] = load_tuple

    def load_empty_tuple(self):
        self.stack.append(Tuple(self.id_mapping))
    dispatch[EMPTY_TUPLE] = load_empty_tuple

    def load_empty_list(self):
        self.stack.append(List(self.id_mapping))
    dispatch[EMPTY_LIST] = load_empty_list

    def load_empty_dictionary(self):
        self.stack.append(Dictionary(self.id_mapping))
    dispatch[EMPTY_DICT] = load_empty_dictionary

    def load_list(self):
        k = self.marker()
        self.stack[k:] = [List(self.id_mapping, v=self.stack[k+1:])]
    dispatch[LIST] = load_list

    def load_dict(self):
        k = self.marker()
        d = Dictionary(self.id_mapping)
        items = self.stack[k+1:]
        for i in range(0, len(items), 2):
            key = items[i]
            value = items[i+1]
            d[key] = value
        self.stack[k:] = [d]
    dispatch[DICT] = load_dict

    def load_inst(self):
        k = self.marker()
        args = Tuple(self.id_mapping, v=self.stack[k+1:])
        del self.stack[k:]
        module = self.readline()[:-1]
        name = self.readline()[:-1]
        value=Object(Global(module, name, self.id_mapping), args, self.id_mapping)
        self.append(value)
    dispatch[INST] = load_inst

    def load_obj(self):
        stack = self.stack
        k = self.marker()
        klass = stack[k + 1]
        del stack[k + 1]
        args = Tuple(self.id_mapping, v=stack[k + 1:])
        del stack[k:]
        value=Object(klass,args, self.id_mapping)
        self.append(value)
    dispatch[OBJ] = load_obj

    def load_global(self):
#        import pdb; pdb.set_trace()
        module = self.readline()[:-1]
        name = self.readline()[:-1]
        self.append(Global(module, name, self.id_mapping))
    dispatch[GLOBAL] = load_global

    def load_reduce(self):
        stack = self.stack

        callable = stack[-2]
        arg_tup  = stack[-1]
        del stack[-2:]

        value=Object(callable, arg_tup, self.id_mapping)
        self.append(value)
    dispatch[REDUCE] = load_reduce

    idprefix=''

    def load_get(self):
        self.append(Get(self.idprefix+self.readline()[:-1], self.id_mapping))
    dispatch[GET] = load_get

    def load_binget(self):
        i = mloads('i' + self.read(1) + '\000\000\000')
        self.append(Get(self.idprefix+repr(i), self.id_mapping))
    dispatch[BINGET] = load_binget

    def load_long_binget(self):
        i = mloads('i' + self.read(4))
        self.append(Get(self.idprefix+repr(i), self.id_mapping))
    dispatch[LONG_BINGET] = load_long_binget

    def load_put(self):
        self.stack[-1].id=self.idprefix+self.readline()[:-1]
    dispatch[PUT] = load_put

    def load_binput(self):
        i = mloads('i' + self.read(1) + '\000\000\000')
        #LOG('load_binput', 0, 'self.stack = %r, self.idprefix+`i` = %r' % (self.stack, self.idprefix+`i`))
        self.stack[-1].id=self.idprefix+repr(i)
    dispatch[BINPUT] = load_binput

    def load_long_binput(self):
        i = mloads('i' + self.read(4))
        self.stack[-1].id=self.idprefix+repr(i)
    dispatch[LONG_BINPUT] = load_long_binput

    class LogCall(object):
      def __init__(self, func):
        self.func = func

      def __call__(self, context):
        #LOG('LogCall', 0, 'self.stack = %r, func = %s' % (context.stack, self.func.__name__))
        return self.func(context)

    #for code in dispatch.keys():
    #  dispatch[code] = LogCall(dispatch[code])

ppml.ToXMLUnpickler = ToXMLUnpickler

def save_string(self, tag, data):
    a = data[1]
    v = b''.join(data[2:])
    encoding = a.get('encoding', 'repr') # JPS: repr is default encoding
    if encoding is not '':
        v = unconvert(encoding, v)
    if self.binary:
        l = len(v)
        if l < 256:
            if isinstance(v, str):
                import pdb; pdb.set_trace()
            if encoding == 'base64':
              op = SHORT_BINBYTES
            else:
              op = SHORT_BINSTRING
            v = op + bytes([l]) + v
        else:
            if encoding == 'base64':
              op = BINBYTES
            else:
              op = BINSTRING
            v = op + struct.pack('<i', l) + v
    else:
        v = STRING + repr(v) + '\n'
    return save_put(self, v, a)

ppml.save_string = save_string

def save_unicode(self, tag, data):
    binary=self.binary
    v=b''
    a=data[1]
    if len(data)>2:
        for x in data[2:]:
            v=v+x
    encoding=a.get('encoding','repr') # JPS: repr is default encoding
    if encoding is not '':
        v=unconvert(encoding,v)
    if binary:
        l=len(v)
        s=mdumps(l)[1:]
        v=BINUNICODE+s+v
    else: v=UNICODE+"'"+v+"'\012"
    return save_put(self, v, a)

ppml.save_unicode = save_unicode

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

ppml.save_object = save_object

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
        if isinstance(top, str):
            import pdb; pdb.set_trace()
            top = top.encode('raw_unicode_escape')
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

# FIXME: Leo: Do we still need to replace ppml.xmlPickler now that we're
# using our own xmlPickler in our own importXML function below? Do we support
# any other use of xmlPickler except for Business Template export/import?
ppml.xmlPickler = xmlPickler

class Tuple(Sequence): pass

ppml.Tuple = Tuple

# Copied from OFS.XMLExportImport.importXML (of Zope 2.12)
# Imported and used directly by Products.ERP5.Document.BusinessTemplate
from OFS.XMLExportImport import save_record, save_zopedata, start_zopedata
from tempfile import TemporaryFile
import xml.parsers.expat
def importXML(jar, file, clue=''):
    if type(file) is str:
        file=open(file, 'rb')
    outfile=TemporaryFile()
#    def write(*args, **kwargs):
#      import pdb; pdb.set_trace()
#      return TemporaryFile.write(*args, **kwargs)
#    outfile.write = write
    data=file.read()
    F=xmlPickler()
    F.end_handlers['record'] = save_record
    F.end_handlers['ZopeData'] = save_zopedata
    F.start_handlers['ZopeData'] = start_zopedata
    F.binary=1
    F.file=outfile
    # <patch>
    # Our BTs XML files don't declare encoding but have accented chars in them
    # So we have to declare an encoding but not use unicode, so the unpickler
    # can deal with the utf-8 strings directly
    p=xml.parsers.expat.ParserCreate('utf-8')
#    p.returns_unicode = False
    # </patch>
    p.CharacterDataHandler=F.handle_data
    p.StartElementHandler=F.unknown_starttag
    p.EndElementHandler=F.unknown_endtag
    r=p.Parse(data)
    outfile.seek(0)
    return jar.importFile(outfile,clue)
