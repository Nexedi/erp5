LocalContent
============

The **LocalContent** meta type is used to store and manage multilingual data.
A single object has different properties, multilingual and monolingual, for
the multilingual ones it's possible to have different language versions.

To explain how to use local content objects we'll go through an step by step
example:

1. Go to the management screens and create a new LocalContent object.

   Just type an id, for example "index_html", and a list of languages (iso
   codes) separated by spaces, for example "en es fr" for english, spanish,
   and french (later you'll be able to add and remove languages through the
   management screens).

2. Edit the object, put some text in the "title" and "body" properties for
   each language.

3. Create a template to view the object, for example a Page Template named
   view

   .. code-block:: html

        <html>
          <head>
            <title tal:content="here/title">Title</title>
          </head>
          <body>
            <h1 tal:content="here/title">Title</h1>
            <p tal:content="here/body">Body</p>
          </body>
        </html>

4. View the object with the url <path>/index_html/view. Try to change the
   language configuration of your browser and reload the page to see how it
   changes.

5. Try to look the url <path>/index_html, it doesn't works. Rename the
   template view to default_template and try again.

   When no template is specified a default one named default_template is used.

6. You can change the default template too, just go to the object index_html,
   go to the Properties tab and add a new property named default_template of
   type string, choose for example view as its value. Now rename
   default_template to view, and visit the url <path>/index_html again.

   This is useful because sometimes different "LocalContent" objects should
   have different default templates.


Indexing and searching
----------------------

Local content objects are catalog aware, if you have a catalog named Catalog
in the acquisition path your local content objects will be automatically
cataloged when you create, modify or delete them.

Local content objects have computed attributes of the form <property>_<lang>,
for instance title_es returns the title of the object in spanish and body_en
returns the english version of the body. This feature lets you, for example,
search through all language versions of a local content object simply by using
these attributes as indexes in the catalog.

