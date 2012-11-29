Multilingual content
====================


LocalProperty and LocalPropertyManager
--------------------------------------

The multilingual features of the LocalContent class are actually provided by
the LocalPropertyManager mixin class. Now I'm going to explain how to develop
your own multilingual classes.

Let's imagine that you want to manage multilingual articles, each article has
three multilingual properties, the title, the abstract and the body. The
commented code would be::

    # Import the needed classes from Localizer
    from Products.Localizer import LocalAttribute, LocalPropertyManager

    # The class must inherit from LocalPropertyManager
    class Article(LocalPropertyManager, SimpleItem):
        meta_type = 'Article'

        # The multilingual properties are instances of
        # LocalAttribute, they can be class variables.
        # The constructor takes 1 argument, which must
        # be the name of the attribute.
        title = LocalAttribute('title')
        abstract = LocalAttribute('abstract')
        body = LocalAttribute('body')

        # LocalPropertyManager needs some metadata,
        # this is similar to the PropertyManager mixin class.
        _local_properties_metadata = ({'id': 'title', 'type': 'string'},
                                      {'id': 'abstract', 'type': 'text'},
                                      {'id': 'body', 'type': 'text'})

