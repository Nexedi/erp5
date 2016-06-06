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
            <value> <string>ts21897137.21</string> </value>
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
  var mode = CodeMirror.getMode({indentUnit: 2}, "php");\n
  function MT(name) { test.mode(name, mode, Array.prototype.slice.call(arguments, 1)); }\n
\n
  MT(\'simple_test\',\n
     \'[meta <?php] \' +\n
     \'[keyword echo] [string "aaa"]; \' +\n
     \'[meta ?>]\');\n
\n
  MT(\'variable_interpolation_non_alphanumeric\',\n
     \'[meta <?php]\',\n
     \'[keyword echo] [string "aaa$~$!$@$#$$$%$^$&$*$($)$.$<$>$/$\\\\$}$\\\\\\"$:$;$?$|$[[$]]$+$=aaa"]\',\n
     \'[meta ?>]\');\n
\n
  MT(\'variable_interpolation_digits\',\n
     \'[meta <?php]\',\n
     \'[keyword echo] [string "aaa$1$2$3$4$5$6$7$8$9$0aaa"]\',\n
     \'[meta ?>]\');\n
\n
  MT(\'variable_interpolation_simple_syntax_1\',\n
     \'[meta <?php]\',\n
     \'[keyword echo] [string "aaa][variable-2 $aaa][string .aaa"];\',\n
     \'[meta ?>]\');\n
\n
  MT(\'variable_interpolation_simple_syntax_2\',\n
     \'[meta <?php]\',\n
     \'[keyword echo] [string "][variable-2 $aaaa][[\',\'[number 2]\',         \']][string aa"];\',\n
     \'[keyword echo] [string "][variable-2 $aaaa][[\',\'[number 2345]\',      \']][string aa"];\',\n
     \'[keyword echo] [string "][variable-2 $aaaa][[\',\'[number 2.3]\',       \']][string aa"];\',\n
     \'[keyword echo] [string "][variable-2 $aaaa][[\',\'[variable aaaaa]\',   \']][string aa"];\',\n
     \'[keyword echo] [string "][variable-2 $aaaa][[\',\'[variable-2 $aaaaa]\',\']][string aa"];\',\n
\n
     \'[keyword echo] [string "1aaa][variable-2 $aaaa][[\',\'[number 2]\',         \']][string aa"];\',\n
     \'[keyword echo] [string "aaa][variable-2 $aaaa][[\',\'[number 2345]\',      \']][string aa"];\',\n
     \'[keyword echo] [string "aaa][variable-2 $aaaa][[\',\'[number 2.3]\',       \']][string aa"];\',\n
     \'[keyword echo] [string "aaa][variable-2 $aaaa][[\',\'[variable aaaaa]\',   \']][string aa"];\',\n
     \'[keyword echo] [string "aaa][variable-2 $aaaa][[\',\'[variable-2 $aaaaa]\',\']][string aa"];\',\n
     \'[meta ?>]\');\n
\n
  MT(\'variable_interpolation_simple_syntax_3\',\n
     \'[meta <?php]\',\n
     \'[keyword echo] [string "aaa][variable-2 $aaaa]->[variable aaaaa][string .aaaaaa"];\',\n
     \'[keyword echo] [string "aaa][variable-2 $aaaa][string ->][variable-2 $aaaaa][string .aaaaaa"];\',\n
     \'[keyword echo] [string "aaa][variable-2 $aaaa]->[variable aaaaa][string [[2]].aaaaaa"];\',\n
     \'[keyword echo] [string "aaa][variable-2 $aaaa]->[variable aaaaa][string ->aaaa2.aaaaaa"];\',\n
     \'[meta ?>]\');\n
\n
  MT(\'variable_interpolation_escaping\',\n
     \'[meta <?php] [comment /* Escaping */]\',\n
     \'[keyword echo] [string "aaa\\\\$aaaa->aaa.aaa"];\',\n
     \'[keyword echo] [string "aaa\\\\$aaaa[[2]]aaa.aaa"];\',\n
     \'[keyword echo] [string "aaa\\\\$aaaa[[asd]]aaa.aaa"];\',\n
     \'[keyword echo] [string "aaa{\\\\$aaaa->aaa.aaa"];\',\n
     \'[keyword echo] [string "aaa{\\\\$aaaa[[2]]aaa.aaa"];\',\n
     \'[keyword echo] [string "aaa{\\\\aaaaa[[asd]]aaa.aaa"];\',\n
     \'[keyword echo] [string "aaa\\\\${aaaa->aaa.aaa"];\',\n
     \'[keyword echo] [string "aaa\\\\${aaaa[[2]]aaa.aaa"];\',\n
     \'[keyword echo] [string "aaa\\\\${aaaa[[asd]]aaa.aaa"];\',\n
     \'[meta ?>]\');\n
\n
  MT(\'variable_interpolation_complex_syntax_1\',\n
     \'[meta <?php]\',\n
     \'[keyword echo] [string "aaa][variable-2 $]{[variable aaaa]}[string ->aaa.aaa"];\',\n
     \'[keyword echo] [string "aaa][variable-2 $]{[variable-2 $aaaa]}[string ->aaa.aaa"];\',\n
     \'[keyword echo] [string "aaa][variable-2 $]{[variable-2 $aaaa][[\',\'  [number 42]\',\']]}[string ->aaa.aaa"];\',\n
     \'[keyword echo] [string "aaa][variable-2 $]{[variable aaaa][meta ?>]aaaaaa\');\n
\n
  MT(\'variable_interpolation_complex_syntax_2\',\n
     \'[meta <?php] [comment /* Monsters */]\',\n
     \'[keyword echo] [string "][variable-2 $]{[variable aaa][comment /*}?>} $aaa<?php } */]}[string ->aaa.aaa"];\',\n
     \'[keyword echo] [string "][variable-2 $]{[variable aaa][comment /*}?>*/][[\',\'  [string "aaa][variable-2 $aaa][string {}][variable-2 $]{[variable aaa]}[string "]\',\']]}[string ->aaa.aaa"];\',\n
     \'[keyword echo] [string "][variable-2 $]{[variable aaa][comment /*} } $aaa } */]}[string ->aaa.aaa"];\');\n
\n
\n
  function build_recursive_monsters(nt, t, n){\n
    var monsters = [t];\n
    for (var i = 1; i <= n; ++i)\n
      monsters[i] = nt.join(monsters[i - 1]);\n
    return monsters;\n
  }\n
\n
  var m1 = build_recursive_monsters(\n
    [\'[string "][variable-2 $]{[variable aaa] [operator +] \', \'}[string "]\'],\n
    \'[comment /* }?>} */] [string "aaa][variable-2 $aaa][string .aaa"]\',\n
    10\n
  );\n
\n
  MT(\'variable_interpolation_complex_syntax_3_1\',\n
     \'[meta <?php] [comment /* Recursive monsters */]\',\n
     \'[keyword echo] \' + m1[4] + \';\',\n
     \'[keyword echo] \' + m1[7] + \';\',\n
     \'[keyword echo] \' + m1[8] + \';\',\n
     \'[keyword echo] \' + m1[5] + \';\',\n
     \'[keyword echo] \' + m1[1] + \';\',\n
     \'[keyword echo] \' + m1[6] + \';\',\n
     \'[keyword echo] \' + m1[9] + \';\',\n
     \'[keyword echo] \' + m1[0] + \';\',\n
     \'[keyword echo] \' + m1[10] + \';\',\n
     \'[keyword echo] \' + m1[2] + \';\',\n
     \'[keyword echo] \' + m1[3] + \';\',\n
     \'[keyword echo] [string "end"];\',\n
     \'[meta ?>]\');\n
\n
  var m2 = build_recursive_monsters(\n
    [\'[string "a][variable-2 $]{[variable aaa] [operator +] \', \' [operator +] \', \'}[string .a"]\'],\n
    \'[comment /* }?>{{ */] [string "a?>}{{aa][variable-2 $aaa][string .a}a?>a"]\',\n
    5\n
  );\n
\n
  MT(\'variable_interpolation_complex_syntax_3_2\',\n
     \'[meta <?php] [comment /* Recursive monsters 2 */]\',\n
     \'[keyword echo] \' + m2[0] + \';\',\n
     \'[keyword echo] \' + m2[1] + \';\',\n
     \'[keyword echo] \' + m2[5] + \';\',\n
     \'[keyword echo] \' + m2[4] + \';\',\n
     \'[keyword echo] \' + m2[2] + \';\',\n
     \'[keyword echo] \' + m2[3] + \';\',\n
     \'[keyword echo] [string "end"];\',\n
     \'[meta ?>]\');\n
\n
  function build_recursive_monsters_2(mf1, mf2, nt, t, n){\n
    var monsters = [t];\n
    for (var i = 1; i <= n; ++i)\n
      monsters[i] = nt[0] + mf1[i - 1] + nt[1] + mf2[i - 1] + nt[2] + monsters[i - 1] + nt[3];\n
    return monsters;\n
  }\n
\n
  var m3 = build_recursive_monsters_2(\n
    m1,\n
    m2,\n
    [\'[string "a][variable-2 $]{[variable aaa] [operator +] \', \' [operator +] \', \' [operator +] \', \'}[string .a"]\'],\n
    \'[comment /* }?>{{ */] [string "a?>}{{aa][variable-2 $aaa][string .a}a?>a"]\',\n
    4\n
  );\n
\n
  MT(\'variable_interpolation_complex_syntax_3_3\',\n
     \'[meta <?php] [comment /* Recursive monsters 2 */]\',\n
     \'[keyword echo] \' + m3[4] + \';\',\n
     \'[keyword echo] \' + m3[0] + \';\',\n
     \'[keyword echo] \' + m3[3] + \';\',\n
     \'[keyword echo] \' + m3[1] + \';\',\n
     \'[keyword echo] \' + m3[2] + \';\',\n
     \'[keyword echo] [string "end"];\',\n
     \'[meta ?>]\');\n
\n
  MT("variable_interpolation_heredoc",\n
     "[meta <?php]",\n
     "[string <<<here]",\n
     "[string doc ][variable-2 $]{[variable yay]}[string more]",\n
     "[string here]; [comment // normal]");\n
})();\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6637</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
