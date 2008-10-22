REST2HTML=html.py --compact-lists --date --generator

all: user_manual.html dev_manual.html

user_manual.html: user_manual.rst
	$(REST2HTML) user_manual.rst user_manual.html

dev_manual.html: dev_manual.rst
	$(REST2HTML) dev_manual.rst dev_manual.html

clean:
	rm *.html
