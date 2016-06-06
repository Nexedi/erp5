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
            <value> <string>ts44314635.31</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>compass_init.rb</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-ruby</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string># This file registers the sencha-touch framework with compass\n
# It\'s a magic name that compass knows how to find.\n
dir = File.dirname(__FILE__)\n
require File.join(dir, \'lib\', \'theme_images.rb\')\n
\n
# Include compass-recipes\n
require File.join(File.dirname(__FILE__), \'vendor\', \'compass-recipes\', \'config\')\n
\n
Compass::BrowserSupport.add_support(\'repeating-linear-gradient\', \'webkit\', \'moz\', \'o\', \'ms\')\n
Compass::Frameworks.register \'sencha-touch\', dir\n
</string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>443</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
