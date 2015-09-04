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
            <value> <string>fileopen.php</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-php</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<!DOCTYPE html>\n
<?php\n
/*\n
 * fileopen.php\n
 * To be used with ext-server_opensave.js for SVG-edit\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 *\n
 */\n
\t// Very minimal PHP file, all we do is Base64 encode the uploaded file and\n
\t// return it to the editor\n
\t\n
\t$type = $_REQUEST[\'type\'];\n
\tif (!in_array($type, array(\'load_svg\', \'import_svg\', \'import_img\'))) {\n
\t\texit;\n
\t}\n
\trequire(\'allowedMimeTypes.php\');\n
\t\n
\t$file = $_FILES[\'svg_file\'][\'tmp_name\'];\n
\t\n
\t$output = file_get_contents($file);\n
\t\n
\t$prefix = \'\';\n
\t\n
\t// Make Data URL prefix for import image\n
\tif ($type == \'import_img\') {\n
\t\t$info = getimagesize($file);\n
\t\tif (!in_array($info[\'mime\'], $allowedMimeTypesBySuffix)) {\n
\t\t\texit;\n
\t\t}\n
\t\t$prefix = \'data:\' . $info[\'mime\'] . \';base64,\';\n
\t}\n
?>\n
<html xmlns="http://www.w3.org/1999/xhtml">\n
<head>\n
<meta charset="utf-8" />\n
<script>\n
\n
top.svgEditor.processFile("<?php \n
\n
// This should be safe since SVG edit does its own filtering (e.g., if an SVG file contains scripts)\n
echo $prefix . base64_encode($output);\n
\n
?>", "<?php echo $type; ?>");\n
</script>\n
</head><body></body>\n
</html>\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1096</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
