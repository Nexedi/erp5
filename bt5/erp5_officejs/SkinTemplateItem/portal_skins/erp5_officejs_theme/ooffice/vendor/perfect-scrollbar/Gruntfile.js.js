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
            <value> <string>ts44314542.67</string> </value>
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

\'use strict\';\n
\n
module.exports = function (grunt) {\n
\n
  // Project configuration.\n
  grunt.initConfig({\n
    // Metadata.\n
    pkg: grunt.file.readJSON(\'perfect-scrollbar.jquery.json\'),\n
    version: grunt.file.readJSON(\'package.json\').version,\n
    banner: \'/*! <%= pkg.title || pkg.name %> - v<%= version %>\\n\' +\n
      \'<%= pkg.homepage ? "* " + pkg.homepage + "\\\\n" : "" %>\' +\n
      \'* Copyright (c) <%= grunt.template.today("yyyy") %> <%= pkg.author.name %>;\' +\n
      \' Licensed <%= _.pluck(pkg.licenses, "type").join(", ") %> */\\n\',\n
    clean: {\n
      files: [\'min\']\n
    },\n
    // Task configuration.\n
    uglify: {\n
      options: {\n
        banner: \'<%= banner %>\'\n
      },\n
      min: {\n
        files: {\n
          \'min/perfect-scrollbar-<%= version %>.min.js\': [\'src/perfect-scrollbar.js\'],\n
          \'min/perfect-scrollbar-<%= version %>.with-mousewheel.min.js\': [\n
            \'src/perfect-scrollbar.js\',\n
            \'src/jquery.mousewheel.js\'\n
          ]\n
        }\n
      }\n
    },\n
    jshint: {\n
      gruntfile: {\n
        options: {\n
          jshintrc: \'.jshintrc\'\n
        },\n
        src: \'Gruntfile.js\'\n
      },\n
      src: {\n
        options: {\n
          jshintrc: \'.jshintrc\'\n
        },\n
        src: \'src/perfect-scrollbar.js\'\n
      }\n
    },\n
    csslint: {\n
      strict: {\n
        options: {\n
          csslintrc: \'.csslintrc\',\n
          \'import\': 2\n
        },\n
        src: [\'src/perfect-scrollbar.css\']\n
      }\n
    },\n
    cssmin: {\n
      options: {\n
        banner: \'<%= banner %>\'\n
      },\n
      minify: {\n
        expand: true,\n
        cwd: \'src/\',\n
        src: [\'perfect-scrollbar.css\'],\n
        dest: \'min/\',\n
        ext: \'-<%= version %>.min.css\'\n
      }\n
    }\n
  });\n
\n
  // These plugins provide necessary tasks.\n
  grunt.loadNpmTasks(\'grunt-contrib-uglify\');\n
  grunt.loadNpmTasks(\'grunt-contrib-jshint\');\n
  grunt.loadNpmTasks(\'grunt-contrib-clean\');\n
  grunt.loadNpmTasks(\'grunt-contrib-csslint\');\n
  grunt.loadNpmTasks(\'grunt-contrib-cssmin\');\n
\n
  grunt.registerTask(\'default\', \'List commands\', function () {\n
    grunt.log.writeln("");\n
\n
    grunt.log.writeln("Run \'grunt lint\' to lint the source files");\n
    grunt.log.writeln("Run \'grunt build\' to minify the source files");\n
  });\n
\n
  grunt.registerTask(\'lint\', [\'jshint\', \'csslint\']);\n
  grunt.registerTask(\'build\', [\'clean\', \'uglify\', \'cssmin\']);\n
  grunt.registerTask(\'travis\', [\'lint\']);\n
\n
};\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2343</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
