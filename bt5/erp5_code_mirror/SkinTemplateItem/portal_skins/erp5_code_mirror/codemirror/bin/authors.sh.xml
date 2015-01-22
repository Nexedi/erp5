<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="DTMLMethod" module="OFS.DTMLMethod"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>authors.sh</string> </value>
        </item>
        <item>
            <key> <string>_vars</string> </key>
            <value>
              <dictionary/>
            </value>
        </item>
        <item>
            <key> <string>globals</string> </key>
            <value>
              <dictionary/>
            </value>
        </item>
        <item>
            <key> <string>raw</string> </key>
            <value> <string encoding="cdata"><![CDATA[

# Combine existing list of authors with everyone known in git, sort, add header.\n
tail --lines=+3 AUTHORS > AUTHORS.tmp\n
git log --format=\'%aN\' >> AUTHORS.tmp\n
echo -e "List of CodeMirror contributors. Updated before every release.\\n" > AUTHORS\n
sort -u AUTHORS.tmp >> AUTHORS\n
rm -f AUTHORS.tmp\n


]]></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
