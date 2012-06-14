LocalFolder
===========

The LocalFolder meta type provides a generic solution to internationalize any
Zope object. Use it to provide images in multiple languages, output dates in
locale formats, etc..

To explain how to use local folder objects we will go through an step by step
example:

1. Go to the management screens and create a new LocalFolder object.

   Use "datetime" as the id and "en es" (for english and spanish) as the list
   of languages (later you'll be able to add and remove languages through the
   management screens).

2. Go to the management screens, to the Attributes tab, and add the ids of the
   multilingual objects you want to have, for example, add short_date.

3. Go to the Contents tab and add an object for each language. For example,
   add two Python scripts, short_date_en and short_date_es (put datetime in
   their parameters list). The body of the english version could be::

        return datetime.strftime('%Y/%m/%d')


   The body of the spanish version could be::

        return datetime.strftime('%d/%m/%Y')

4. Now leave the local folder object and create, for example, a DTML method,
   call it today. Its body could be:

   .. code-block:: xml

        <dtml-var standard_html_header>

        <dtml-var "datetime.short_date(_.DateTime())">

        <dtml-var standard_html_footer>

5. View the today method and change the configuration of your browser between
   english and spanish to see how it changes.

In short, what local folder objects do is to let to use different language
versions of any Zope object (Python scripts, images, folders, etc..), which
version is used with each request depends on the language negotiation
facilities. Each multilingual object must be specified in the Attributes tab,
each language version has the form <name>_<language>. For example, if the
multilingual attribute is logo the spanish version's id is logo_es.

