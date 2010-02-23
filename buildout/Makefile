software: bin/buildout
	bin/buildout

bin/buildout:
	python bootstrap/bootstrap.py

# run make assert to check that all is working
assert: assert-software

assert-software: assert-python2.4 assert-parts-libs

assert-python2.4: bin/python2.4
	bin/python2.4 -V 2>&1 | grep 'Python 2.4.6'
	bin/python2.4 -c 'import ERP5Diff'
	bin/python2.4 -c 'import MySQLdb'
	bin/python2.4 -c 'import SOAPpy'
	bin/python2.4 -c 'import _ssl'
	bin/python2.4 -c 'import _xmlplus'
	bin/python2.4 -c 'import bz2'
	bin/python2.4 -c 'import dbm'
	bin/python2.4 -c 'import elementtree'
	bin/python2.4 -c 'import fpconst'
	bin/python2.4 -c 'import gdbm'
	bin/python2.4 -c 'import itools'
	bin/python2.4 -c 'import ldap'
	bin/python2.4 -c 'import lxml'
	bin/python2.4 -c 'import memcache'
	bin/python2.4 -c 'import numpy'
	bin/python2.4 -c 'import pytz'
	bin/python2.4 -c 'import simplejson'
	bin/python2.4 -c 'import threadframe'
	bin/python2.4 -c 'import xml.parsers.expat'
	bin/python2.4 -c 'import zlib'

assert-parts-libs:
	ldd parts/mysql-tritonn-5.0/libexec/mysqld | grep 'parts/senna/lib/libsenna.so.0'
	ldd develop-eggs/MySQL_python-1.2.3c1-py2.4-linux-x86_64.egg/_mysql.so | grep 'parts/mysql-tritonn-5.0/lib/mysql/libmysqlclient_r.so'
	ldd parts/memcached/bin/memcached | grep 'parts/libevent/lib/libevent'

create-mandriva2010-rpm: bin/buildout
	bin/buildout -c profiles/mandriva2010.0.cfg buildout:directory=`pwd` install create-rpm
