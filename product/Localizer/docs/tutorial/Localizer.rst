Localizer
=========

.. highlight:: xml

By default only the browser configuration (the **AcceptLanguage** header) is
used to choose the language. Localizer implements the HTTP standard, it
represents the user prefered languages as a tree where each node has a quality
between 0.0 and 1.0 (a higher quality means the language is more prefered by
the user). For more information see the HTTP protocol specification.

The **Localizer** meta type lets to use other criterias to choose the
language. Usually there's one instance in the root of the web site. Its id is
always Localizer and can't be changed.

A Localizer object has a property named **accept_methods** (of type tokens)
which contains a list of method ids. Each method specified in this list will
be called every time the folder where the Localizer object lives is traversed.
By default it includes two builtin methods that add two new criterias to
choose the language:

accept_cookie

    Lets to specify the language with the cookie LOCALIZER_LANGUAGE, which
    must contain a language code. This method assigns a quality of 2.0 to the
    language specified in the cookie. This way it takes precedence over the
    browser configuration.

accept_path

    Lets to specify the language in the url. For example, if there's a
    Localizer object at the root of the web site, the url
    http://www.example.com/es/index.html will set the quality for spanish to
    3.0, this way it will take precedence over the browser configuration and
    the cookie.


Customize
---------

To change the language negotiation policy to fit your needs you have to modify
the property accept_methods. You can remove any of the builtin methods (if you
don't want to use cookies or to specify the language in the url) and add new
ones that usually will be implemeted as Python scripts.

The functions that appear in the accept_methods list receive a parameter that
represents the tree of the user prefered languages. This object offers a
complete API, but usually only the method set will be used.

For example, create a Python script within the Localizer instance named
accept_french, add accept_language to its parameter list. The body of the
script could be the line:

.. code-block:: python

    accept_language.set("fr", 4.0)

This would set french as the user prefered language with a quality of 4.0,
taking precedence over the browser, the cookie and the laguage specified in
the url. Finally just add its id to the list accept_methods.


The change language form
------------------------

The Localizer object also provides the HTML form changeLanguageForm and its
action, changeLanguage. They provide a quick way to implement a language
selection box, the action modifies the LOCALIZER_LANGUAGE cookie.

For DTML type::

    <dtml-var "Localizer.changeLanguageForm()">

For ZPT type::

    <tal:block content="structure here/Localizer/changeLanguageForm" />



