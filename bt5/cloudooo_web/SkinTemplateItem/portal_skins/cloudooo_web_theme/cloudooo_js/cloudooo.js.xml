<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="DTMLDocument" module="OFS.DTMLDocument"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>cloudooo.js</string> </value>
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

$.extend({\n
  getUrlVars: function(){\n
    var vars = [], hash;\n
    var hashes = window.location.href.slice(window.location.href.indexOf(\'?\') + 1).split(\'&\');\n
    for(var i = 0; i < hashes.length; i++)\n
    {\n
      hash = hashes[i].split(\'=\');\n
      vars.push(hash[0]);\n
      vars[hash[0]] = hash[1];\n
    }\n
    return vars;\n
  },\n
  getUrlVar: function(name){\n
    return $.getUrlVars()[name];\n
  }\n
});\n
\n
var checkState_call_count = 0\n
function checkState(message){\n
  checkState_call_count += 1\n
  var checkState_call_str = ["",".","..","..."]\n
  $("#transition-message").html(message+checkState_call_str[checkState_call_count%4])\n
  $.get("Document_getPropertiesAsJSON", {}, function(data, textStatus, XMLHttpRequest){\n
    if (textStatus == "timeout" || textStatus == "error" || textStatus == "parsererror"){\n
      $("title").html("Error during conversion");\n
      $("#transition-message").html("An error occurs during the process. Please resend your file");\n
    }\n
    else {\n
      //TextStatus is "notmodified","success"\n
      json = jQuery.parseJSON( data );\n
      if ((json.processing == "converted") || (json.processing == "conversion_failed") || (json.processing == "empty")){\n
        $("title").html("Finish");\n
        $("#transition-message").html("The conversion process is finish. You will be redirect in 3 seconds.");\n
        setTimeout("$(location).attr(\'href\',\'"+json.permanent_url+"\')", 3000);\n
      }\n
      else {\n
        if (json.processing == "process_error") {\n
          $("title").html("Error during conversion");\n
          $("#transition-message").html("An error occurs during the process. Please resend your file");\n
        }\n
        else {\n
          setTimeout("checkState(\'"+message+"\')", 500);\n
        }\n
      }\n
    }\n
  });\n
}\n
\n
function createBookmark(title,url) {\n
  if ($.browser.mozilla == true) {\n
    window.sidebar.addPanel(title, url, "");\n
  } \n
  else {\n
    if($.browser.msie == true) {\n
      window.external.AddFavorite( url, title);\n
    }\n
    else {\n
      alert(\'Please use CTRL + D to bookmark this website.\'); \n
    }\n
  }\n
}\n
 \n
function generateLink(id, title, url){\n
  var link_title ;\n
  if ($.browser.msie == true) {\n
    link_title = "Add to Favorites";\n
  } else  if ($.browser.mozilla == true) {\n
    link_title = "Bookmark Page";\n
  } else if ($.browser.opera== true) { \n
    link_title = "Add Bookmark" ;\n
  } else {\n
    link_title = "Add to favorites";\n
  }\n
  \n
  var link = $(id);\n
  link.attr("title",link_title);\n
  link.html(link_title);\n
  link.attr("href","javascript:createBookmark(\\""+title+"\\",\\""+url+"\\");");\n
}\n
\n
function contentMaximise(){\n
  $("#content").removeClass("twocolumns");\n
  $("#sidebar").hide();\n
}\n
\n
function contentMinimise(){\n
  $("#content").addClass("twocolumns");\n
  $("#sidebar").show();\n
}

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
