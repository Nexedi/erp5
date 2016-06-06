<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts21897141.08</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>test.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

// CodeMirror, copyright (c) by Marijn Haverbeke and others\n
// Distributed under an MIT license: http://codemirror.net/LICENSE\n
\n
(function() {\n
  var mode = CodeMirror.getMode({tabSize: 4}, \'textile\');\n
  function MT(name) { test.mode(name, mode, Array.prototype.slice.call(arguments, 1)); }\n
\n
  MT(\'simpleParagraphs\',\n
      \'Some text.\',\n
      \'\',\n
      \'Some more text.\');\n
\n
  /*\n
   * Phrase Modifiers\n
   */\n
\n
  MT(\'em\',\n
      \'foo [em _bar_]\');\n
\n
  MT(\'emBoogus\',\n
      \'code_mirror\');\n
\n
  MT(\'strong\',\n
      \'foo [strong *bar*]\');\n
\n
  MT(\'strongBogus\',\n
      \'3 * 3 = 9\');\n
\n
  MT(\'italic\',\n
      \'foo [em __bar__]\');\n
\n
  MT(\'italicBogus\',\n
      \'code__mirror\');\n
\n
  MT(\'bold\',\n
      \'foo [strong **bar**]\');\n
\n
  MT(\'boldBogus\',\n
      \'3 ** 3 = 27\');\n
\n
  MT(\'simpleLink\',\n
      \'[link "CodeMirror":http://codemirror.net]\');\n
\n
  MT(\'referenceLink\',\n
      \'[link "CodeMirror":code_mirror]\',\n
      \'Normal Text.\',\n
      \'[link [[code_mirror]]http://codemirror.net]\');\n
\n
  MT(\'footCite\',\n
      \'foo bar[qualifier [[1]]]\');\n
\n
  MT(\'footCiteBogus\',\n
      \'foo bar[[1a2]]\');\n
\n
  MT(\'special-characters\',\n
          \'Registered [tag (r)], \' +\n
          \'Trademark [tag (tm)], and \' +\n
          \'Copyright [tag (c)] 2008\');\n
\n
  MT(\'cite\',\n
      "A book is [keyword ??The Count of Monte Cristo??] by Dumas.");\n
\n
  MT(\'additionAndDeletion\',\n
      \'The news networks declared [negative -Al Gore-] \' +\n
        \'[positive +George W. Bush+] the winner in Florida.\');\n
\n
  MT(\'subAndSup\',\n
      \'f(x, n) = log [builtin ~4~] x [builtin ^n^]\');\n
\n
  MT(\'spanAndCode\',\n
      \'A [quote %span element%] and [atom @code element@]\');\n
\n
  MT(\'spanBogus\',\n
      \'Percentage 25% is not a span.\');\n
\n
  MT(\'citeBogus\',\n
      \'Question? is not a citation.\');\n
\n
  MT(\'codeBogus\',\n
      \'user@example.com\');\n
\n
  MT(\'subBogus\',\n
      \'~username\');\n
\n
  MT(\'supBogus\',\n
      \'foo ^ bar\');\n
\n
  MT(\'deletionBogus\',\n
      \'3 - 3 = 0\');\n
\n
  MT(\'additionBogus\',\n
      \'3 + 3 = 6\');\n
\n
  MT(\'image\',\n
      \'An image: [string !http://www.example.com/image.png!]\');\n
\n
  MT(\'imageWithAltText\',\n
      \'An image: [string !http://www.example.com/image.png (Alt Text)!]\');\n
\n
  MT(\'imageWithUrl\',\n
      \'An image: [string !http://www.example.com/image.png!:http://www.example.com/]\');\n
\n
  /*\n
   * Headers\n
   */\n
\n
  MT(\'h1\',\n
      \'[header&header-1 h1. foo]\');\n
\n
  MT(\'h2\',\n
      \'[header&header-2 h2. foo]\');\n
\n
  MT(\'h3\',\n
      \'[header&header-3 h3. foo]\');\n
\n
  MT(\'h4\',\n
      \'[header&header-4 h4. foo]\');\n
\n
  MT(\'h5\',\n
      \'[header&header-5 h5. foo]\');\n
\n
  MT(\'h6\',\n
      \'[header&header-6 h6. foo]\');\n
\n
  MT(\'h7Bogus\',\n
      \'h7. foo\');\n
\n
  MT(\'multipleHeaders\',\n
      \'[header&header-1 h1. Heading 1]\',\n
      \'\',\n
      \'Some text.\',\n
      \'\',\n
      \'[header&header-2 h2. Heading 2]\',\n
      \'\',\n
      \'More text.\');\n
\n
  MT(\'h1inline\',\n
      \'[header&header-1 h1. foo ][header&header-1&em _bar_][header&header-1  baz]\');\n
\n
  /*\n
   * Lists\n
   */\n
\n
  MT(\'ul\',\n
      \'foo\',\n
      \'bar\',\n
      \'\',\n
      \'[variable-2 * foo]\',\n
      \'[variable-2 * bar]\');\n
\n
  MT(\'ulNoBlank\',\n
      \'foo\',\n
      \'bar\',\n
      \'[variable-2 * foo]\',\n
      \'[variable-2 * bar]\');\n
\n
  MT(\'ol\',\n
      \'foo\',\n
      \'bar\',\n
      \'\',\n
      \'[variable-2 # foo]\',\n
      \'[variable-2 # bar]\');\n
\n
  MT(\'olNoBlank\',\n
      \'foo\',\n
      \'bar\',\n
      \'[variable-2 # foo]\',\n
      \'[variable-2 # bar]\');\n
\n
  MT(\'ulFormatting\',\n
      \'[variable-2 * ][variable-2&em _foo_][variable-2  bar]\',\n
      \'[variable-2 * ][variable-2&strong *][variable-2&em&strong _foo_]\' +\n
        \'[variable-2&strong *][variable-2  bar]\',\n
      \'[variable-2 * ][variable-2&strong *foo*][variable-2  bar]\');\n
\n
  MT(\'olFormatting\',\n
      \'[variable-2 # ][variable-2&em _foo_][variable-2  bar]\',\n
      \'[variable-2 # ][variable-2&strong *][variable-2&em&strong _foo_]\' +\n
        \'[variable-2&strong *][variable-2  bar]\',\n
      \'[variable-2 # ][variable-2&strong *foo*][variable-2  bar]\');\n
\n
  MT(\'ulNested\',\n
      \'[variable-2 * foo]\',\n
      \'[variable-3 ** bar]\',\n
      \'[keyword *** bar]\',\n
      \'[variable-2 **** bar]\',\n
      \'[variable-3 ** bar]\');\n
\n
  MT(\'olNested\',\n
      \'[variable-2 # foo]\',\n
      \'[variable-3 ## bar]\',\n
      \'[keyword ### bar]\',\n
      \'[variable-2 #### bar]\',\n
      \'[variable-3 ## bar]\');\n
\n
  MT(\'ulNestedWithOl\',\n
      \'[variable-2 * foo]\',\n
      \'[variable-3 ## bar]\',\n
      \'[keyword *** bar]\',\n
      \'[variable-2 #### bar]\',\n
      \'[variable-3 ** bar]\');\n
\n
  MT(\'olNestedWithUl\',\n
      \'[variable-2 # foo]\',\n
      \'[variable-3 ** bar]\',\n
      \'[keyword ### bar]\',\n
      \'[variable-2 **** bar]\',\n
      \'[variable-3 ## bar]\');\n
\n
  MT(\'definitionList\',\n
      \'[number - coffee := Hot ][number&em _and_][number  black]\',\n
      \'\',\n
      \'Normal text.\');\n
\n
  MT(\'definitionListSpan\',\n
      \'[number - coffee :=]\',\n
      \'\',\n
      \'[number Hot ][number&em _and_][number  black =:]\',\n
      \'\',\n
      \'Normal text.\');\n
\n
  MT(\'boo\',\n
      \'[number - dog := woof woof]\',\n
      \'[number - cat := meow meow]\',\n
      \'[number - whale :=]\',\n
      \'[number Whale noises.]\',\n
      \'\',\n
      \'[number Also, ][number&em _splashing_][number . =:]\');\n
\n
  /*\n
   * Attributes\n
   */\n
\n
  MT(\'divWithAttribute\',\n
      \'[punctuation div][punctuation&attribute (#my-id)][punctuation . foo bar]\');\n
\n
  MT(\'divWithAttributeAnd2emRightPadding\',\n
      \'[punctuation div][punctuation&attribute (#my-id)((][punctuation . foo bar]\');\n
\n
  MT(\'divWithClassAndId\',\n
      \'[punctuation div][punctuation&attribute (my-class#my-id)][punctuation . foo bar]\');\n
\n
  MT(\'paragraphWithCss\',\n
      \'p[attribute {color:red;}]. foo bar\');\n
\n
  MT(\'paragraphNestedStyles\',\n
      \'p. [strong *foo ][strong&em _bar_][strong *]\');\n
\n
  MT(\'paragraphWithLanguage\',\n
      \'p[attribute [[fr]]]. Parlez-vous français?\');\n
\n
  MT(\'paragraphLeftAlign\',\n
      \'p[attribute <]. Left\');\n
\n
  MT(\'paragraphRightAlign\',\n
      \'p[attribute >]. Right\');\n
\n
  MT(\'paragraphRightAlign\',\n
      \'p[attribute =]. Center\');\n
\n
  MT(\'paragraphJustified\',\n
      \'p[attribute <>]. Justified\');\n
\n
  MT(\'paragraphWithLeftIndent1em\',\n
      \'p[attribute (]. Left\');\n
\n
  MT(\'paragraphWithRightIndent1em\',\n
      \'p[attribute )]. Right\');\n
\n
  MT(\'paragraphWithLeftIndent2em\',\n
      \'p[attribute ((]. Left\');\n
\n
  MT(\'paragraphWithRightIndent2em\',\n
      \'p[attribute ))]. Right\');\n
\n
  MT(\'paragraphWithLeftIndent3emRightIndent2em\',\n
      \'p[attribute ((())]. Right\');\n
\n
  MT(\'divFormatting\',\n
      \'[punctuation div. ][punctuation&strong *foo ]\' +\n
        \'[punctuation&strong&em _bar_][punctuation&strong *]\');\n
\n
  MT(\'phraseModifierAttributes\',\n
      \'p[attribute (my-class)]. This is a paragraph that has a class and\' +\n
      \' this [em _][em&attribute (#special-phrase)][em emphasized phrase_]\' +\n
      \' has an id.\');\n
\n
  MT(\'linkWithClass\',\n
      \'[link "(my-class). This is a link with class":http://redcloth.org]\');\n
\n
  /*\n
   * Layouts\n
   */\n
\n
  MT(\'paragraphLayouts\',\n
      \'p. This is one paragraph.\',\n
      \'\',\n
      \'p. This is another.\');\n
\n
  MT(\'div\',\n
      \'[punctuation div. foo bar]\');\n
\n
  MT(\'pre\',\n
      \'[operator pre. Text]\');\n
\n
  MT(\'bq.\',\n
      \'[bracket bq. foo bar]\',\n
      \'\',\n
      \'Normal text.\');\n
\n
  MT(\'footnote\',\n
      \'[variable fn123. foo ][variable&strong *bar*]\');\n
\n
  /*\n
   * Spanning Layouts\n
   */\n
\n
  MT(\'bq..ThenParagraph\',\n
      \'[bracket bq.. foo bar]\',\n
      \'\',\n
      \'[bracket More quote.]\',\n
      \'p. Normal Text\');\n
\n
  MT(\'bq..ThenH1\',\n
      \'[bracket bq.. foo bar]\',\n
      \'\',\n
      \'[bracket More quote.]\',\n
      \'[header&header-1 h1. Header Text]\');\n
\n
  MT(\'bc..ThenParagraph\',\n
      \'[atom bc.. # Some ruby code]\',\n
      \'[atom obj = {foo: :bar}]\',\n
      \'[atom puts obj]\',\n
      \'\',\n
      \'[atom obj[[:love]] = "*love*"]\',\n
      \'[atom puts obj.love.upcase]\',\n
      \'\',\n
      \'p. Normal text.\');\n
\n
  MT(\'fn1..ThenParagraph\',\n
      \'[variable fn1.. foo bar]\',\n
      \'\',\n
      \'[variable More.]\',\n
      \'p. Normal Text\');\n
\n
  MT(\'pre..ThenParagraph\',\n
      \'[operator pre.. foo bar]\',\n
      \'\',\n
      \'[operator More.]\',\n
      \'p. Normal Text\');\n
\n
  /*\n
   * Tables\n
   */\n
\n
  MT(\'table\',\n
      \'[variable-3&operator |_. name |_. age|]\',\n
      \'[variable-3 |][variable-3&strong *Walter*][variable-3 |   5  |]\',\n
      \'[variable-3 |Florence|   6  |]\',\n
      \'\',\n
      \'p. Normal text.\');\n
\n
  MT(\'tableWithAttributes\',\n
      \'[variable-3&operator |_. name |_. age|]\',\n
      \'[variable-3 |][variable-3&attribute /2.][variable-3  Jim |]\',\n
      \'[variable-3 |][variable-3&attribute \\\\2{color: red}.][variable-3  Sam |]\');\n
\n
  /*\n
   * HTML\n
   */\n
\n
  MT(\'html\',\n
      \'[comment <div id="wrapper">]\',\n
      \'[comment <section id="introduction">]\',\n
      \'\',\n
      \'[header&header-1 h1. Welcome]\',\n
      \'\',\n
      \'[variable-2 * Item one]\',\n
      \'[variable-2 * Item two]\',\n
      \'\',\n
      \'[comment <a href="http://example.com">Example</a>]\',\n
      \'\',\n
      \'[comment </section>]\',\n
      \'[comment </div>]\');\n
\n
  MT(\'inlineHtml\',\n
      \'I can use HTML directly in my [comment <span class="youbetcha">Textile</span>].\');\n
\n
  /*\n
   * No-Textile\n
   */\n
\n
  MT(\'notextile\',\n
    \'[string-2 notextile. *No* formatting]\');\n
\n
  MT(\'notextileInline\',\n
      \'Use [string-2 ==*asterisks*==] for [strong *strong*] text.\');\n
\n
  MT(\'notextileWithPre\',\n
      \'[operator pre. *No* formatting]\');\n
\n
  MT(\'notextileWithSpanningPre\',\n
      \'[operator pre.. *No* formatting]\',\n
      \'\',\n
      \'[operator *No* formatting]\');\n
\n
  /* Only toggling phrases between non-word chars. */\n
\n
  MT(\'phrase-in-word\',\n
     \'foo_bar_baz\');\n
\n
  MT(\'phrase-non-word\',\n
     \'[negative -x-] aaa-bbb ccc-ddd [negative -eee-] fff [negative -ggg-]\');\n
\n
  MT(\'phrase-lone-dash\',\n
     \'foo - bar - baz\');\n
})();\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>9437</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
