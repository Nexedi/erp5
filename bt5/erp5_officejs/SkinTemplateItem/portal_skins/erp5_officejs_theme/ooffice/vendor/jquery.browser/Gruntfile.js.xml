<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts44314533.34</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Gruntfile.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

module.exports = function(grunt) { \n
\tgrunt.initConfig({\n
\t\tpkg: grunt.file.readJSON(\'package.json\'),\n
\t\tjshint: {\n
\t\t\tfiles: [\'gruntfile.js\', \'jquery.browser.js\'],\n
\n
\t\t\toptions: {\n
\t\t\t\tglobals: {\n
\t\t\t\t\tjQuery: true,\n
\t\t\t\t\tconsole: true,\n
\t\t\t\t\tmodule: true\n
\t\t\t\t}\n
\t\t\t}\n
\t\t},\n
\t\tuglify: {\n
\t\t\toptions: {\n
\t\t\t\tbanner: \'/*!\\n * jQuery Browser Plugin <%= pkg.version %>\\n * https://github.com/gabceb/jquery-browser-plugin\\n *\\n * Original jquery-browser code Copyright 2005, 2013 jQuery Foundation, Inc. and other contributors\\n * http://jquery.org/license\\n *\\n * Modifications Copyright <%= grunt.template.today("yyyy") %> Gabriel Cebrian\\n * https://github.com/gabceb\\n *\\n * Released under the MIT license\\n *\\n * Date: <%= grunt.template.today("dd-mm-yyyy")%>\\n */\'\n
\t\t\t},\n
\t\t\tdist: {\n
\t\t\t\tfiles: {\n
\t\t\t\t\t\'dist/<%= pkg.name %>.min.js\': \'dist/<%= pkg.name %>.js\'\n
\t\t\t\t}\n
\t\t\t}\n
\t\t},\n
\t\tcopy: {\n
\t\t\tmain:{\n
\t\t\t\tsrc: "dist/<%= pkg.name %>.js",\n
\t\t\t\tdest: "test/src/<%= pkg.name %>.js"\n
\t\t\t}\n
\t\t},\n
\t\texec: {\n
\t\t\ttest: {\n
\t\t\t\tcommand: "casperjs test test/test.js",\n
\t\t\t\tstdout: true,\n
\t\t\t\tstderr: true\n
\t\t\t}\n
\t\t}\n
\t});\n
\n
\tgrunt.loadNpmTasks(\'grunt-contrib-jshint\');\n
\tgrunt.loadNpmTasks(\'grunt-contrib-uglify\');\n
\tgrunt.loadNpmTasks(\'grunt-contrib-copy\');\n
\tgrunt.loadNpmTasks(\'grunt-exec\');\n
\n
\tgrunt.registerTask(\'default\', [\'jshint\', \'uglify\', \'copy\']);\n
\tgrunt.registerTask(\'test\', [\'exec\']);\n
};

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1353</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
