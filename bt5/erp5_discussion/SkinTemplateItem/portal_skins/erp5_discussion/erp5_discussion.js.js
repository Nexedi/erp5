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
            <value> <string>ts95524491.35</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>erp5_discussion.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

function deleteDiscussionPost(id){\n
  /* this will add respective input box for delete post id (so multiple delete buttons can \n
     safely coexist in one HTML page with one HTML form */\n
  $("form").append(\'<input type="hidden" name="discussion_post_uid" value="\' +id +  \'">\');\n
  clickSaveButton("DiscussionThread_deleteDiscussionPost");\n
}\n
\n
function redirectCreateCitedNewDiscussionPost(id){\n
  /* this will add respective input box for reply post id (so multiple reply buttons can \n
     safely coexist in one HTML page with one HTML form */\n
  $("form").append(\'<input type="hidden" name="discussion_post_uid" value="\' +id +  \'">\');\n
  clickSaveButton("DiscussionThread_redirectCreateNewDiscussionPost");\n
}\n
\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>705</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
