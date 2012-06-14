Multilingual software
=====================

Software provides always a user interface, doesn't matters wether it's a text
based interface, a graphical application or a web site. The error messages,
the buttons, the labels, etc.. need to be translated.

This is a well known problem for which there're available mature solutions.
But first we'll introduce some basic terminology that will be needed to read
the rest of this guide:

Message
    A piece of text that needs to be translated.
Message translation
    The translation of a message.
Message catalog
    A database that stores the message translations, and provides ways to get
    them.


Gettext
-------

In the free software world the de facto standard solution to translate the
user interfaces are the `GNU gettext
<http://www.gnu.org/software/gettext/gettext.html>`_ utilities. Gettext is
used to translate the GNU software and also other projects like KDE.

Initially developed to translate C or C++ programs its usage has grown and now
it's also used with other languages. For example, Python 2.x includes a
gettext module that lets to use the GNU gettext tools, and the last versions
of the well know `Mailman <http://www.list.org/>`_ application use it to
provide a multilingual interface.

