Multilingual data
=================

Internatiolizing software is the easy part, managing multilingual content is
the hard one.

In a multilingual information system there will be people that introduces
content and people that translates it. To keep the information synchronized
and to reduce the translation costs as much as possible are the goals.


The problem
-----------

Here are some elements to be considered:

* A translator aware workflow

  When a new document is introduced into the system or when an existing
  document changes, the translators must be notified. The same document could
  be in different states depending on the language, for example the english
  version could be ready to be published while the french version could be
  unfinished yet.

  Translators are specialized, they can't translate from any language to any
  language. For example a translator could do translations from spanish to
  french, while another one could translate from english to french and
  spanish, or between spanish and french (in both directions).

* Identify the original content.

  It's better to translate from the original content than from another
  translation because, usually, through the translation process there's a
  quality loss. This information is important to improve the translation
  process and also for the end user, who always should know which is the
  original version of the document, the one that contains the more accurate
  data.

* Reduce the translation cost

  Translations are expensive, you should use automatic translation systems to
  reduce the cost. The output of these systems is not good enough to directly
  publish it, but can help a lot to the human translators to do their work
  quickly.

  It's also important to provide translators the possibility to work off-line,
  this is specially important when external translators are used, sometimes
  freelancers.


Translation memories
--------------------

The standard solution to address these problems is known as translation
memories systems. Basically, the procedure used is:

1. First the text is splitted in sentences
2. Each sentence is automatically translated, usually using fuzzy matching
   against a database. The result is proposed to the translator.
3. The translator corrects the translation and the good one is re-introduced
   in the system to improve future translations.

Sophisticated tools for translators with easy to use interfaces, workflow and
versioning systems to manage the content and advanced automatic translation
engines are an important part of the solution.


.. seealso::

    Related links

    Institutions:

        * the `Localisation Research Centre <http://www.localisation.ie/>`_
        * the `Localisation Standards Industry Association
          <http://www.lisa.org/>`_

    Publications:

        * `Localisation focus
          <http://www.localisation.ie/resources/locfocus/index.htm>`_

    Standards:

        * the `Translation Memory eXchange <http://www.lisa.org/tmx>`_
          standard;

    Papers:

        * `Evaluation of Natural Language Processing Systems
          <http://www.issco.unige.ch/ewg95>`_, final report


