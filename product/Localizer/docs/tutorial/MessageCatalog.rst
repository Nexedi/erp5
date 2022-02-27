MessageCatalog
==============

.. highlight:: xml

The Localizer product provides the class MessageCatalog, it stores messages
and their translations and provides a web interface to manage them. They're
useful to translate the application interface: labels, buttons, etc..

The messages are stored in the ZODB, though they can be exported and imported
to and from "po" files. It's also possible to manage a message catalog through
FTP.


Getting translations
--------------------

To get the translations message catalogs provide the gettext method, for
example::

    <dtml-var "messages.gettext('Hello world!')">

The message catalog is callable, this means it's possible to use a shorter
version::

    <dtml-var "messages('Hello world!')">

The gettext method accepts two optional parameters, it's signature is:

.. code-block:: python

    gettext(message, language=None, add=1)

The parameters are:

    +----------+--------------------------------------+
    | message  | The message to be translated.        |
    +----------+--------------------------------------+
    | language | The destination language, if None    |
    |          | (default) the selection language     |
    |          | algortihm will be used to choose     |
    |          | the destination language.            |
    +----------+--------------------------------------+
    |  add     | If true (default) the message will   |
    |          | be automatically added to the        |
    |          | catalog if it doesn't exists.        |
    +----------+--------------------------------------+


Zope Page Templates
-------------------

Message catalogs can also be used from ZPT, for example::

  <span tal:replace="python:here.messages('Hello world!')">
    Hello world!
  </span>


