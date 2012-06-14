Quick start (5 min)
===================

.. highlight:: xml


Output the "Hello world" message in multiple languages
------------------------------------------------------

#. Create a folder named, for example, TestLocalizer, and go inside it.
#. Create a MessageCatalog named, for example, gettext.
#. Go to the management interfaces of the message catalog, go to the tab
   languages and add the languages you want.
#. Create a DTML method named test_gettext.
#. In the DTML method type::

        <dtml-var "gettext('Hello world!')">

#. View the DTML method.
#. Go to the management screens of the message catalog, provide translations
   to the message "Hello world!".
#. View again the DTML method, change the language configuration of your
   browser and reload the page to see how the message changes.


Add a language selection box
----------------------------

1. Add a Localizer instance.
2. Edit the DTML method test_gettext and add::

        <dtml-var "Localizer.changeLanguageForm()">

3. View again the DTML method and use the selection box to change the language
   (you need to active cookies and javascript in your browser).


