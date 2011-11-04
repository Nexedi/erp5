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

from ZODB.utils import u64, p64
from Shared.DC.xml import ppml
from base64 import encodestring
from cStringIO import StringIO
from ZODB.serialize import referencesf
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
    pickler.dump(classdef)
    pickler.dump(obj)
    p=newp.getvalue()
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
