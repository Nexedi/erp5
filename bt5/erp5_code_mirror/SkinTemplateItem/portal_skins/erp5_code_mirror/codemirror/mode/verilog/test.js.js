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
            <value> <string>ts21897132.59</string> </value>
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
            <value> <string>// CodeMirror, copyright (c) by Marijn Haverbeke and others\n
// Distributed under an MIT license: http://codemirror.net/LICENSE\n
\n
(function() {\n
  var mode = CodeMirror.getMode({indentUnit: 4}, "verilog");\n
  function MT(name) { test.mode(name, mode, Array.prototype.slice.call(arguments, 1)); }\n
\n
  MT("binary_literals",\n
     "[number 1\'b0]",\n
     "[number 1\'b1]",\n
     "[number 1\'bx]",\n
     "[number 1\'bz]",\n
     "[number 1\'bX]",\n
     "[number 1\'bZ]",\n
     "[number 1\'B0]",\n
     "[number 1\'B1]",\n
     "[number 1\'Bx]",\n
     "[number 1\'Bz]",\n
     "[number 1\'BX]",\n
     "[number 1\'BZ]",\n
     "[number 1\'b0]",\n
     "[number 1\'b1]",\n
     "[number 2\'b01]",\n
     "[number 2\'bxz]",\n
     "[number 2\'b11]",\n
     "[number 2\'b10]",\n
     "[number 2\'b1Z]",\n
     "[number 12\'b0101_0101_0101]",\n
     "[number 1\'b 0]",\n
     "[number \'b0101]"\n
  );\n
\n
  MT("octal_literals",\n
     "[number 3\'o7]",\n
     "[number 3\'O7]",\n
     "[number 3\'so7]",\n
     "[number 3\'SO7]"\n
  );\n
\n
  MT("decimal_literals",\n
     "[number 0]",\n
     "[number 1]",\n
     "[number 7]",\n
     "[number 123_456]",\n
     "[number \'d33]",\n
     "[number 8\'d255]",\n
     "[number 8\'D255]",\n
     "[number 8\'sd255]",\n
     "[number 8\'SD255]",\n
     "[number 32\'d123]",\n
     "[number 32 \'d123]",\n
     "[number 32 \'d 123]"\n
  );\n
\n
  MT("hex_literals",\n
     "[number 4\'h0]",\n
     "[number 4\'ha]",\n
     "[number 4\'hF]",\n
     "[number 4\'hx]",\n
     "[number 4\'hz]",\n
     "[number 4\'hX]",\n
     "[number 4\'hZ]",\n
     "[number 32\'hdc78]",\n
     "[number 32\'hDC78]",\n
     "[number 32 \'hDC78]",\n
     "[number 32\'h DC78]",\n
     "[number 32 \'h DC78]",\n
     "[number 32\'h44x7]",\n
     "[number 32\'hFFF?]"\n
  );\n
\n
  MT("real_number_literals",\n
     "[number 1.2]",\n
     "[number 0.1]",\n
     "[number 2394.26331]",\n
     "[number 1.2E12]",\n
     "[number 1.2e12]",\n
     "[number 1.30e-2]",\n
     "[number 0.1e-0]",\n
     "[number 23E10]",\n
     "[number 29E-2]",\n
     "[number 236.123_763_e-12]"\n
  );\n
\n
  MT("operators",\n
     "[meta ^]"\n
  );\n
\n
  MT("keywords",\n
     "[keyword logic]",\n
     "[keyword logic] [variable foo]",\n
     "[keyword reg] [variable abc]"\n
  );\n
\n
  MT("variables",\n
     "[variable _leading_underscore]",\n
     "[variable _if]",\n
     "[number 12] [variable foo]",\n
     "[variable foo] [number 14]"\n
  );\n
\n
  MT("tick_defines",\n
     "[def `FOO]",\n
     "[def `foo]",\n
     "[def `FOO_bar]"\n
  );\n
\n
  MT("system_calls",\n
     "[meta $display]",\n
     "[meta $vpi_printf]"\n
  );\n
\n
  MT("line_comment", "[comment // Hello world]");\n
\n
  // Alignment tests\n
  MT("align_port_map_style1",\n
     /**\n
      * mod mod(.a(a),\n
      *         .b(b)\n
      *        );\n
      */\n
     "[variable mod] [variable mod][bracket (].[variable a][bracket (][variable a][bracket )],",\n
     "        .[variable b][bracket (][variable b][bracket )]",\n
     "       [bracket )];",\n
     ""\n
  );\n
\n
  MT("align_port_map_style2",\n
     /**\n
      * mod mod(\n
      *     .a(a),\n
      *     .b(b)\n
      * );\n
      */\n
     "[variable mod] [variable mod][bracket (]",\n
     "    .[variable a][bracket (][variable a][bracket )],",\n
     "    .[variable b][bracket (][variable b][bracket )]",\n
     "[bracket )];",\n
     ""\n
  );\n
\n
  // Indentation tests\n
  MT("indent_single_statement_if",\n
      "[keyword if] [bracket (][variable foo][bracket )]",\n
      "    [keyword break];",\n
      ""\n
  );\n
\n
  MT("no_indent_after_single_line_if",\n
      "[keyword if] [bracket (][variable foo][bracket )] [keyword break];",\n
      ""\n
  );\n
\n
  MT("indent_after_if_begin_same_line",\n
      "[keyword if] [bracket (][variable foo][bracket )] [keyword begin]",\n
      "    [keyword break];",\n
      "    [keyword break];",\n
      "[keyword end]",\n
      ""\n
  );\n
\n
  MT("indent_after_if_begin_next_line",\n
      "[keyword if] [bracket (][variable foo][bracket )]",\n
      "    [keyword begin]",\n
      "        [keyword break];",\n
      "        [keyword break];",\n
      "    [keyword end]",\n
      ""\n
  );\n
\n
  MT("indent_single_statement_if_else",\n
      "[keyword if] [bracket (][variable foo][bracket )]",\n
      "    [keyword break];",\n
      "[keyword else]",\n
      "    [keyword break];",\n
      ""\n
  );\n
\n
  MT("indent_if_else_begin_same_line",\n
      "[keyword if] [bracket (][variable foo][bracket )] [keyword begin]",\n
      "    [keyword break];",\n
      "    [keyword break];",\n
      "[keyword end] [keyword else] [keyword begin]",\n
      "    [keyword break];",\n
      "    [keyword break];",\n
      "[keyword end]",\n
      ""\n
  );\n
\n
  MT("indent_if_else_begin_next_line",\n
      "[keyword if] [bracket (][variable foo][bracket )]",\n
      "    [keyword begin]",\n
      "        [keyword break];",\n
      "        [keyword break];",\n
      "    [keyword end]",\n
      "[keyword else]",\n
      "    [keyword begin]",\n
      "        [keyword break];",\n
      "        [keyword break];",\n
      "    [keyword end]",\n
      ""\n
  );\n
\n
  MT("indent_if_nested_without_begin",\n
      "[keyword if] [bracket (][variable foo][bracket )]",\n
      "    [keyword if] [bracket (][variable foo][bracket )]",\n
      "        [keyword if] [bracket (][variable foo][bracket )]",\n
      "            [keyword break];",\n
      ""\n
  );\n
\n
  MT("indent_case",\n
      "[keyword case] [bracket (][variable state][bracket )]",\n
      "    [variable FOO]:",\n
      "        [keyword break];",\n
      "    [variable BAR]:",\n
      "        [keyword break];",\n
      "[keyword endcase]",\n
      ""\n
  );\n
\n
  MT("unindent_after_end_with_preceding_text",\n
      "[keyword begin]",\n
      "    [keyword break]; [keyword end]",\n
      ""\n
  );\n
\n
  MT("export_function_one_line_does_not_indent",\n
     "[keyword export] [string \\"DPI-C\\"] [keyword function] [variable helloFromSV];",\n
     ""\n
  );\n
\n
  MT("export_task_one_line_does_not_indent",\n
     "[keyword export] [string \\"DPI-C\\"] [keyword task] [variable helloFromSV];",\n
     ""\n
  );\n
\n
  MT("export_function_two_lines_indents_properly",\n
    "[keyword export]",\n
    "    [string \\"DPI-C\\"] [keyword function] [variable helloFromSV];",\n
    ""\n
  );\n
\n
  MT("export_task_two_lines_indents_properly",\n
    "[keyword export]",\n
    "    [string \\"DPI-C\\"] [keyword task] [variable helloFromSV];",\n
    ""\n
  );\n
\n
  MT("import_function_one_line_does_not_indent",\n
    "[keyword import] [string \\"DPI-C\\"] [keyword function] [variable helloFromC];",\n
    ""\n
  );\n
\n
  MT("import_task_one_line_does_not_indent",\n
    "[keyword import] [string \\"DPI-C\\"] [keyword task] [variable helloFromC];",\n
    ""\n
  );\n
\n
  MT("import_package_single_line_does_not_indent",\n
    "[keyword import] [variable p]::[variable x];",\n
    "[keyword import] [variable p]::[variable y];",\n
    ""\n
  );\n
\n
  MT("covergoup_with_function_indents_properly",\n
    "[keyword covergroup] [variable cg] [keyword with] [keyword function] [variable sample][bracket (][keyword bit] [variable b][bracket )];",\n
    "    [variable c] : [keyword coverpoint] [variable c];",\n
    "[keyword endgroup]: [variable cg]",\n
    ""\n
  );\n
\n
})();\n
</string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6776</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
