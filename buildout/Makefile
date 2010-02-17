software: bin/buildout
	bin/buildout

bin/buildout:
	python bootstrap/bootstrap.py

# run make assert to check that all is working
assert: assert-software

assert-software: assert-python2.4

assert-python2.4: bin/python2.4
	bin/python2.4 -c 'import _ssl'
	bin/python2.4 -c 'import bz2'
	bin/python2.4 -c 'import dbm'
	bin/python2.4 -c 'import xml.parsers.expat'
	bin/python2.4 -c 'import zlib'

create-mandriva2010-rpm: bin/buildout
	bin/buildout -c profiles/mandriva2010.0.cfg buildout:directory=`pwd` install create-rpm
