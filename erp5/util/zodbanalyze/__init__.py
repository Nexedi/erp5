#!/usr/bin/env python2.4

# Based on a transaction analyzer by Matt Kromer.

import sys
from ZODB.FileStorage import FileStorage
from ZODB.utils import get_pickle_metadata

class Report:
    def __init__(self):
        self.OIDMAP = {}
        self.TYPEMAP = {}
        self.TYPESIZE = {}
        self.FREEMAP = {}
        self.USEDMAP = {}
        self.TIDS = 0
        self.OIDS = 0
        self.DBYTES = 0
        self.COIDS = 0
        self.CBYTES = 0
        self.FOIDS = 0
        self.FBYTES = 0
        self.COIDSMAP = {}
        self.CBYTESMAP = {}
        self.FOIDSMAP = {}
        self.FBYTESMAP = {}

def shorten(s, n):
    l = len(s)
    if l <= n:
        return s
    while len(s) + 3 > n: # account for ...
        i = s.find(".")
        if i == -1:
            # In the worst case, just return the rightmost n bytes
            return s[-n:]
        else:
            s = s[i + 1:]
            l = len(s)
    return "..." + s

def report(rep):
    print "Processed %d records in %d transactions" % (rep.OIDS, rep.TIDS)
    print "Average record size is %7.2f bytes" % (rep.DBYTES * 1.0 / rep.OIDS)
    print ("Average transaction size is %7.2f bytes" %
           (rep.DBYTES * 1.0 / rep.TIDS))

    print "Types used:"
    fmt = "%-46s %7s %9s %6s %7s %7s %9s %7s %9s"
    fmtp = "%-46s %7d %9d %5.1f%% %7.2f %7d %9d %7d %9d" # per-class format
    fmts = "%46s %7d %8dk %5.1f%% %7.2f" # summary format
    print fmt % ("Class Name", "T.Count", "T.Bytes", "Pct", "AvgSize",
                 "C.Count", "C.Bytes", "O.Count", "O.Bytes")
    print fmt % ('-'*46, '-'*7, '-'*9, '-'*5, '-'*7, '-'*7, '-'*9, '-'*7, '-'*9)
    typemap = rep.TYPEMAP.keys()
    typemap.sort(key=lambda a:rep.TYPESIZE[a])
    cumpct = 0.0
    for t in typemap:
        pct = rep.TYPESIZE[t] * 100.0 / rep.DBYTES
        cumpct += pct
        print fmtp % (shorten(t, 46), rep.TYPEMAP[t], rep.TYPESIZE[t],
                      pct, rep.TYPESIZE[t] * 1.0 / rep.TYPEMAP[t],
                      rep.COIDSMAP[t], rep.CBYTESMAP[t],
                      rep.FOIDSMAP.get(t, 0), rep.FBYTESMAP.get(t, 0))

    print fmt % ('='*46, '='*7, '='*9, '='*5, '='*7, '='*7, '='*9, '='*7, '='*9)
    print "%46s %7d %9s %6s %6.2fk" % ('Total Transactions', rep.TIDS, ' ',
        ' ', rep.DBYTES * 1.0 / rep.TIDS / 1024.0)
    print fmts % ('Total Records', rep.OIDS, rep.DBYTES / 1024.0, cumpct,
                  rep.DBYTES * 1.0 / rep.OIDS)

    print fmts % ('Current Objects', rep.COIDS, rep.CBYTES / 1024.0,
                  rep.CBYTES * 100.0 / rep.DBYTES,
                  rep.CBYTES * 1.0 / rep.COIDS)
    if rep.FOIDS:
        print fmts % ('Old Objects', rep.FOIDS, rep.FBYTES / 1024.0,
                      rep.FBYTES * 100.0 / rep.DBYTES,
                      rep.FBYTES * 1.0 / rep.FOIDS)

def analyze(path):
    fs = FileStorage(path, read_only=1)
    fsi = fs.iterator()
    report = Report()
    for txn in fsi:
        analyze_trans(report, txn)
    return report

def analyze_trans(report, txn):
    report.TIDS += 1
    for rec in txn:
        analyze_rec(report, rec)

def get_type(record):
    mod, klass = get_pickle_metadata(record.data)
    return "%s.%s" % (mod, klass)

def analyze_rec(report, record):
    oid = record.oid
    report.OIDS += 1
    if record.data is None:
        # No pickle -- aborted version or undo of object creation.
        return
    try:
        size = len(record.data) # Ignores various overhead
        report.DBYTES += size
        if oid not in report.OIDMAP:
            type = get_type(record)
            report.OIDMAP[oid] = type
            report.USEDMAP[oid] = size
            report.COIDS += 1
            report.CBYTES += size
            report.COIDSMAP[type] = report.COIDSMAP.get(type, 0) + 1
            report.CBYTESMAP[type] = report.CBYTESMAP.get(type, 0) + size
        else:
            type = report.OIDMAP[oid]
            fsize = report.USEDMAP[oid]
            report.FREEMAP[oid] = report.FREEMAP.get(oid, 0) + fsize
            report.USEDMAP[oid] = size
            report.FOIDS += 1
            report.FBYTES += fsize
            report.CBYTES += size - fsize
            report.FOIDSMAP[type] = report.FOIDSMAP.get(type, 0) + 1
            report.FBYTESMAP[type] = report.FBYTESMAP.get(type, 0) + fsize
            report.CBYTESMAP[type] = report.CBYTESMAP.get(type, 0) + size - fsize
        report.TYPEMAP[type] = report.TYPEMAP.get(type, 0) + 1
        report.TYPESIZE[type] = report.TYPESIZE.get(type, 0) + size
    except Exception, err:
        print err

def main():
    path = sys.argv[1]
    report(analyze(path))
