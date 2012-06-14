Unicode
=======


Encoding systems
----------------

Computers deal with numbers, this means that letters and other characters are
internally represented as numbers. Basically, an encoding system associates
each character with a number. For example, for the encoding named ASCII the
number 97 represents the character "a". So a text is just a sequence of
characters, and for computers it's just a sequence of numbers.

There're many different encoding systems, each one is used to represent
characters from one or more languages. For example the ASCII encoding is used
for english; ISO-8859-1 can be used with spanish, french or german; EUC-JP
represents japanese characters; etc..

The problem is that different encodings can use the same number to represent
different charecters, then they're incompatible. This is a problem for example
if you want to mix different languages in the same text.


Unicode
-------

To solve this problem Unicode appeared. Unicode is an encoding system that is
able to represent all the characters in the world. Using Unicode it's possible
to mix different languages in the same text without problems.


Python
------

The Python programming language provides two types of strings, normal strings
and unicode strings. Internationalized software written in Python always
should use unicode strings for text.

Normal strings represent sequences of bytes while unicode strings represent
sequences of characters. Unicode strings provide a higher abstraction layer
for the programmer that lets to forget, most of the time, about the encoding
issues.

Encoding becomes an issue when an unicode string needs to be serialized, for
example when the server response is sent to the browser. Then an specific
encoding needs to be choosen. For fully multilingual applications this should
be UTF-8, which is a particular representation of the Unicode character set.


.. seealso::

    Related links

    General information about Unicode:

        * `Official Unicode web site <http://www.unicode.org/>`_
        * `UTF-8 and Unicode FAQ for Unix/Linux
          <http://www.cl.cam.ac.uk/~mgk25/unicode.html>`_
        * `Unicode and Multilingual Support in HTML, Fonts, Web Browsers and
          Other Applications <http://www.alanwood.net/unicode/>`_

    Python resources for Unicode:

        * `Python Unicode Tutorial
          <http://www.reportlab.com/i18n/python_unicode_tutorial.html>`_
        * `Python Internationalization Special Interest Group
          <http://www.python.org/sigs/i18n-sig/>`_


