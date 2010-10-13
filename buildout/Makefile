PYTHON=python
BUILDOUT_OPT=-U -v

software: bin/buildout
	$(PYTHON) -S bin/buildout $(BUILDOUT_OPT)

bin/buildout:
	$(PYTHON) -S bootstrap/bootstrap.py -v 1.4.4

# run make assert to check that all is working
assert: bin/python2.4
	bin/python2.4 tests/assertSoftware.py
