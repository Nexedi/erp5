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
            <value> <string>ts40515059.48</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>savefile.php</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-php</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<?php\n
\t// You must first create a file "savefile_config.php" in this extensions directory and do whatever\n
\t//   checking of user credentials, etc. that you wish; otherwise anyone will be able to post SVG\n
\t//   files to your server which may cause disk space or possibly security problems\n
  require(\'savefile_config.php\');\n
  if (!isset($_POST[\'output_svg\'])) {\n
\t\tprint "You must supply output_svg";\n
\t\texit;\n
\t}\n
\t$svg = $_POST[\'output_svg\'];\n
\t$filename = (isset($_POST[\'filename\']) && !empty($_POST[\'filename\']) ? preg_replace(\'@[\\\\\\\\/:*?"<>|]@u\', \'_\', $_POST[\'filename\']) : \'saved\') . \'.svg\'; // These characters are indicated as prohibited by Windows\n
\n
\t$fh = fopen($filename, \'w\') or die("Can\'t open file");\n
\tfwrite($fh, $svg);\n
\tfclose($fh);\n
?>\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>744</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
