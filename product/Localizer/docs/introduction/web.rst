The web
=======

A personal computer is configured with what is known as a locale, it specifies
the encoding system, the user language, the timezone and other parameters that
will be used by the applications to show their interfaces adapted to the user.

When an application starts, for example a word processor, it reads the locale
information, it only needs to be done once, at the begining. This process is
more complex in a networking environment like the web, where there are many
computers involved with different locale configurations.

In the web the client must send the locale information to the server each time
it requests a page. With this information the server can decide in which
language send the data.

Things become more complex when there is a cache between the server and the
client, then the needed dialog to choose the language involves more parties,
the server, the client and the cache.


.. seealso::

    Related links

    * `HTTP 1.1 language negotiation
      <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4>`_
    * `Apache content negotiation
      <http://httpd.apache.org/docs-2.0/content-negotiation.html>`_


