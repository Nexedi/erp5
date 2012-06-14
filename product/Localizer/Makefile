
PYTHON=python


po:
	${PYTHON} zgettext.py *.py ui/*.dtml -l ca de es eu fr hu it ja pt ru

mo:
	${PYTHON} zgettext.py -m

clean:
	rm -f *~ *.pyc
	rm -f locale/*~ locale/locale.pot.bak locale/*.mo
	rm -f help/*~
	rm -f tests/*~ tests/*.pyc
	rm -f ui/*~

test:
	${PYTHON} tests/test_zgettext.py


binary: clean mo
	rm -f refresh.txt
