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

class cleaner_for(object):

    def __init__(self, classdef):
        self.classdef = classdef

    def __call__(self, callable):
        PICKLE_CLEANERS[self.classdef] = callable
        return callable

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

def XMLrecord(oid, plen, p, id_mapping):
    # Proceed as usual
    q=ppml.ToXMLUnpickler
    f=StringIO(p)
    u=q(f)
    id=u64(oid)
    id = id_mapping[id]
    old_aka = encodestring(oid)[:-1]
    aka=encodestring(p64(long(id)))[:-1]  # Rebuild oid based on mapped id
    id_mapping.setConvertedAka(old_aka, aka)
    u.idprefix=str(id)+'.'
    p=u.load(id_mapping=id_mapping).__str__(4)
    if f.tell() < plen:
        p=p+u.load(id_mapping=id_mapping).__str__(4)
    String='  <record id="%s" aka="%s">\n%s  </record>\n' % (id, aka, p)
    return String

XMLExportImport.XMLrecord = XMLrecord

def exportXML(jar, oid, file=None):
    # XXX: For performance reasons, we should change XMLExportImport/ppml code
    #      so that we can call reorderPickle and XMLrecord only once.
    #      This means we should be able to do a real export immediately.
    #      This would also fix random failures when DemoStorage is used,
    #      because oids can have values that have a shorter representation
    #      in 'repr' instead of 'base64' (see ppml.convert) and ppml.String
    #      does not support this.

    if file is None: file=TemporaryFile()
    elif type(file) is StringType: file=open(file,'w+b')
    id_mapping = ppml.MinimalMapping()
    #id_mapping = ppml.IdentityMapping()
    write=file.write
    write('<?xml version="1.0"?>\012<ZopeData>\012')
    # Versions are ignored, but some 'load()' implementations require them
    # FIXME: remove 'version' when TmpStore.load() on ZODB stops asking for it.
    version=''
    ref=referencesf
    oids=[oid]
    done_oids={}
    done=done_oids.has_key
    load=jar._storage.load
    original_oid = oid
    reordered_pickle = []
    # Build mapping for refs
    while oids:
        oid=oids[0]
        del oids[0]
        if done(oid): continue
        done_oids[oid]=1
        try: p, serial = load(oid, version)
        except:
            # Ick, a broken reference
            log.error('exportXML: could not load oid %r' % oid,
                      exc_info=True)
        else:
            o, p = reorderPickle(jar, p)
            reordered_pickle.append((oid, o, p))
            XMLrecord(oid,len(p),p, id_mapping)
            # Determine new oids added to the list after reference calculation
            old_oids = tuple(oids)
            ref(p, oids)
            new_oids = []
            for i in oids:
                if i not in old_oids: new_oids.append(i)
            # Sort new oids based on id of object
            new_oidict = {}
            for oid in new_oids:
                try:
                    p, serial = load(oid, version)
                    o, p = reorderPickle(jar, p)
                    new_oidict[oid] = getattr(o, 'id', None)
                except:
                    log.error('exportXML: could not load oid %r' % oid,
                              exc_info=True)
                    new_oidict[oid] = None # Ick, a broken reference
            new_oids.sort(key=lambda x: new_oidict[x])
            # Build new sorted oids
            oids = list(old_oids) + new_oids
    # Do real export
    for (oid, o, p) in reordered_pickle:
        write(XMLrecord(oid,len(p),p, id_mapping))
    write('</ZopeData>\n')
    return file

ObjectManager.exportXML = XMLExportImport.exportXML = exportXML
