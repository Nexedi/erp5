Introduction
============

This is a buildout to create instance for MySQL Tritonn

Usage
=======

Afterwards, type:
    $ bin/supervisord -e debug -n

If everything looks good:
    $ bin/supervisord


Configure
=========

You can change the default ports by editing buildout.cfg:

    [ports]
    …
    supervisor = 9001
    mysql = 3306

Then rerun buildout:
    $ bin/buildout
