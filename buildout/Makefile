software: bin/buildout
	bin/buildout

bin/buildout:
	python bootstrap/bootstrap.py

# run make assert to check that all is working
assert: assert-software

assert-software: assert-python2.4

assert-python2.4: bin/python2.4
	bin/python2.4 -c 'import zlib'
	bin/python2.4 -c 'import dbm'
