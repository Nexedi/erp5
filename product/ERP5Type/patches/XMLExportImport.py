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

# Make sure the xml export will be ordered

import re
from ZODB.utils import u64, p64
from Shared.DC.xml import ppml
from base64 import encodestring
from cStringIO import StringIO
try:
  from ZODB.serialize import referencesf
except ImportError:
  from ZODB.referencesf import referencesf
from ZODB.ExportImport import TemporaryFile
from pickle import Pickler, EMPTY_DICT, MARK, DICT
from cPickle import loads, dumps
from types import TupleType
from types import StringType
from types import DictionaryType
from OFS import ObjectManager, XMLExportImport

from logging import getLogger
log = getLogger(__name__)

# Jython has PyStringMap; it's a dict subclass with string keys
try:
    from org.python.core import PyStringMap
except ImportError:
    PyStringMap = None

# Ordered pickles
class OrderedPickler(Pickler):

    dispatch = Pickler.dispatch.copy()

    def save_dict(self, obj):
        write = self.write

        if self.bin:
            write(EMPTY_DICT)
        else:   # proto 0 -- can't use EMPTY_DICT
            write(MARK + DICT)

        self.memoize(obj)
        item_list = obj.items() # New version by JPS for sorting
        item_list.sort(key=lambda x: x[0]) # New version by JPS for sorting
        self._batch_setitems(item_list.__iter__())

    dispatch[DictionaryType] = save_dict
    if not PyStringMap is None:
        dispatch[PyStringMap] = save_dict


# ExtensionClass.Base.__getnewargs__ XML simplification
# BBB: Remove this whole section of code (and its invocation below) once
# we drop support for Zope 2.8 (i.e. once Base drops __getnewargs__)
from ExtensionClass import Base
Base__getnewargs__ = getattr(Base, '__getnewargs__', None)
if Base__getnewargs__ is None:
  is_old_btree = lambda pickle: None
  def getCleanClass(classdef):
    return classdef
else:
  is_old_btree = re.compile('cBTrees\\._(..)BTree\n(\\1)BTree\n').match
  def getCleanClass(classdef):
    if isinstance(classdef, tuple):
      pureclass, newargs = classdef
      if (newargs == () and
          not isinstance(pureclass, tuple) and
          getattr(pureclass, '__getnewargs__', None) is Base__getnewargs__):
        return pureclass
    return classdef
# END ExtensionClass.Base.__getnewargs__ XML simplification

from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

PICKLE_CLEANERS = {}

def cleaner_for(classdef):
  def wrapper(func):
    PICKLE_CLEANERS[classdef] = func
    return func
  return wrapper

# BBB: Remove this cleaner when we drop support for Zope 2.8
@cleaner_for(ZopePageTemplate)
def cleanup_ZopePageTemplate(state):
    if isinstance(state.get('_text'), str):
        state['_text'] = unicode(state['_text'], 'utf-8')
        state['output_encoding'] = 'utf-8'
    if isinstance(state.get('title'), str):
        state['title'] = unicode(state['title'], 'utf-8')

def cleanupState(classdef, state):
    classdef = getCleanClass(classdef)
    cleanupState = PICKLE_CLEANERS.get(classdef, lambda state: None)
    cleanupState(state)
    return classdef, state

def reorderPickle(jar, p):
    from ZODB.ExportImport import Ghost, Unpickler, Pickler, StringIO, persistent_id

    oids = {}
    storage = jar._storage
    new_oid = storage.new_oid
    store = storage.store

    def persistent_load(ooid,
                        Ghost=Ghost,
                        oids=oids, wrote_oid=oids.has_key,
                        new_oid=storage.new_oid):

        "Remap a persistent id to an existing ID and create a ghost for it."

        if type(ooid) is TupleType: ooid, klass = ooid
        else: klass=None

        try:
          Ghost=Ghost()
          Ghost.oid=ooid
        except TypeError:
          Ghost=Ghost(ooid)
        return Ghost


    # Reorder pickle by doing I/O
    pfile = StringIO(p)
    unpickler=Unpickler(pfile)
    unpickler.persistent_load=persistent_load

    newp=StringIO()
    pickler=OrderedPickler(newp,1)
    pickler.persistent_id=persistent_id

    classdef = unpickler.load()
    obj = unpickler.load()
    classdef, obj = cleanupState(classdef, obj)
    pickler.dump(classdef)
    pickler.dump(obj)
    p=newp.getvalue()
    if is_old_btree(p):
      p = p.replace('_','',1)
    return obj, p

def _mapOid(id_mapping, oid):
    idprefix = str(u64(oid))
    id = id_mapping[idprefix]
    old_aka = encodestring(oid)[:-1]
    aka=encodestring(p64(long(id)))[:-1]  # Rebuild oid based on mapped id
    id_mapping.setConvertedAka(old_aka, aka)
    return idprefix+'.', id, aka

def XMLrecord(oid, plen, p, id_mapping):
    # Proceed as usual
    q=ppml.ToXMLUnpickler
    f=StringIO(p)
    u=q(f)
    u.idprefix, id, aka = _mapOid(id_mapping, oid)
    p=u.load(id_mapping=id_mapping).__str__(4)
    if f.tell() < plen:
        p=p+u.load(id_mapping=id_mapping).__str__(4)
    String='  <record id="%s" aka="%s">\n%s  </record>\n' % (id, aka, p)
    return String

XMLExportImport.XMLrecord = XMLrecord

def exportXML(jar, oid, file=None):
    # For performance reasons, exportXML does not use 'XMLrecord' anymore to map
    # oids. This requires to initialize MinimalMapping.marked_reference before
    # any string output, i.e. in ppml.Reference.__init__
    # This also fixed random failures when DemoStorage is used, because oids
    # can have values that have a shorter representation in 'repr' instead of
    # 'base64' (see ppml.convert) and ppml.String does not support this.
    load = jar._storage.load
    pickle_dict = {oid: None}
    max_cache = [1e7] # do not cache more than 10MB of pickle data
    def getReorderedPickle(oid):
        p = pickle_dict[oid]
        if p is None:
            # Versions are ignored, but some 'load()' implementations require them
            # FIXME: remove "''" when TmpStore.load() on ZODB stops asking for it.
            p = load(oid, '')[0]
            p = reorderPickle(jar, p)[1]
            if len(p) < max_cache[0]:
                max_cache[0] -= len(p)
                pickle_dict[oid] = p
        return p

    # Sort records and initialize id_mapping
    id_mapping = ppml.MinimalMapping()
    reordered_oid_list = [oid]
    for oid in reordered_oid_list:
        _mapOid(id_mapping, oid)
        for oid in referencesf(getReorderedPickle(oid)):
            if oid not in pickle_dict:
                pickle_dict[oid] = None
                reordered_oid_list.append(oid)

    # Do real export
    if file is None:
        file = TemporaryFile()
    elif isinstance(file, basestring):
        file = open(file, 'w+b')
    write = file.write
    write('<?xml version="1.0"?>\n<ZopeData>\n')
    for oid in reordered_oid_list:
        p = getReorderedPickle(oid)
        write(XMLrecord(oid, len(p), p, id_mapping))
    write('</ZopeData>\n')
    return file

ObjectManager.exportXML = XMLExportImport.exportXML = exportXML
