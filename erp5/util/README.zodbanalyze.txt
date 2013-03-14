zodbanalyze
-----------

This is an improved version of ZODB's ZODB/scripts/analyze.py.

* faster
* does not require Products.
* supports csv output by '-c' or '--csv'
* supports using DBM temporary storage to limit memory usage by '-d' or '--dbm', otherwise memory usage is O(n) of number of OIDs.
