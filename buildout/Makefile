software: bin/buildout
	bin/buildout

bin/buildout:
	python bootstrap/bootstrap.py

# run make assert to check that all is working
assert: assert-software

assert-software: assert-python2.4 assert-eggs-2.4 assert-parts-libs

assert-python2.4: bin/python2.4
	bin/python2.4 -c 'import _ssl'
	bin/python2.4 -c 'import bz2'
	bin/python2.4 -c 'import dbm'
	bin/python2.4 -c 'import xml.parsers.expat'
	bin/python2.4 -c 'import zlib'

assert-eggs-2.4:
	ls -d eggs/erp5diff-*-py2.4.egg
	ls -d eggs/fpconst-*-py2.4.egg
	ls -d eggs/lxml-*-py2.4-*-*.egg
	ls -d eggs/numpy-*-py2.4-*-*.egg
	ls -d eggs/python_ldap-*-py2.4-*-*.egg
	ls -d eggs/python_memcached-*-py2.4.egg
	ls -d eggs/pytz-*-py2.4.egg
	ls -d eggs/PyXML-*-py2.4-*-*.egg
	ls -d eggs/simplejson-*-py2.4-*-*.egg
	ls -d eggs/SOAPpy-*-py2.4.egg
	ls -d eggs/threadframe-*-py2.4-*-*.egg
	ls -d eggs/timerserver-*-py2.4.egg
	ls -d develop-eggs/itools-*-py2.4-*-*.egg
	ls -d develop-eggs/itools-*-py2.4-*-*.egg
	ls -d develop-eggs/MySQL_python-*-py2.4-*-*.egg
	ldd develop-eggs/MySQL_python-1.2.3c1-py2.4-linux-x86_64.egg/_mysql.so | grep 'parts/mysql-tritonn-5.0/lib/mysql/libmysqlclient_r.so'

assert-parts-libs:
	ldd parts/mysql-tritonn-5.0/libexec/mysqld | grep 'parts/senna/lib/libsenna.so.0'
	ldd parts/memcached/bin/memcached | grep 'parts/libevent/lib/libevent'

create-mandriva2010-rpm: bin/buildout
	bin/buildout -c profiles/mandriva2010.0.cfg buildout:directory=`pwd` install create-rpm
