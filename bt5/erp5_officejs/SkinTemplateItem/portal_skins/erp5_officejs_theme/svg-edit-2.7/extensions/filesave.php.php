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
            <value> <string>filesave.php</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-php</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<?php\n
/*\n
 * filesave.php\n
 * To be used with ext-server_opensave.js for SVG-edit\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 *\n
 */\n
\n
function encodeRFC5987ValueChars ($str) {\n
\t// See http://tools.ietf.org/html/rfc5987#section-3.2.1\n
\t// For better readability within headers, add back the characters escaped by rawurlencode but still allowable\n
\t// Although RFC3986 reserves "!" (%21), RFC5987 does not\n
\treturn preg_replace_callback(\'@%(2[1346B]|5E|60|7C)@\', function ($matches) {\n
\t\treturn chr(\'0x\' . $matches[1]);\n
\t}, rawurlencode($str));\n
}\n
\n
require(\'allowedMimeTypes.php\');\n
\n
$mime = !isset($_POST[\'mime\']) || !in_array($_POST[\'mime\'], $allowedMimeTypesBySuffix) ? \'image/svg+xml;charset=UTF-8\' : $_POST[\'mime\'];\n
 \n
if (!isset($_POST[\'output_svg\']) && !isset($_POST[\'output_img\'])) {\n
\tdie(\'post fail\');\n
}\n
\n
$file = \'\';\n
\n
$suffix = \'.\' . array_search($mime, $allowedMimeTypesBySuffix);\n
\n
if (isset($_POST[\'filename\']) && strlen($_POST[\'filename\']) > 0) {\n
\t$file = $_POST[\'filename\'] . $suffix;\n
} else {\n
\t$file = \'image\' . $suffix;\n
}\n
\n
if ($suffix == \'.svg\') {\n
\t$contents = $_POST[\'output_svg\'];\n
} else {\n
\t$contents = $_POST[\'output_img\'];\n
\t$pos = (strpos($contents, \'base64,\') + 7);\n
\t$contents = base64_decode(substr($contents, $pos));\n
}\n
\n
header("Cache-Control: public");\n
header("Content-Description: File Transfer");\n
\n
// See http://tools.ietf.org/html/rfc6266#section-4.1\n
header("Content-Disposition: attachment; filename*=UTF-8\'\'" . encodeRFC5987ValueChars(\n
\t// preg_replace(\'@[\\\\\\\\/:*?"<>|]@\', \'\', $file) // If we wanted to strip Windows-disallowed characters server-side (but not a security issue, so we can strip client-side instead)\n
\t$file\n
));\n
header("Content-Type: " .  $mime);\n
header("Content-Transfer-Encoding: binary");\n
\n
echo $contents;\n
 \n
?>

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1775</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
