<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string>REQUEST = context.REQUEST\n
active_process_id = REQUEST.get(\'active_process_id\', None)\n
erp5_site_id = context.getPortalObject().getId()\n
\n
js_string = """\n
    // Initialisation\n
    window.onload = init;\n
\n
    function getNewXMLHTTP() {\n
      try {\n
\t    return new XMLHttpRequest();\n
      } catch(e) {\t\n
  \t    try {\n
  \t      var aObj = new ActiveXObject("Msxml2.XMLHTTP");\n
\t    } catch (e) {\n
\t      try {\n
\t\t    var aObj = new ActiveXObject("Microsoft.XMLHTTP");\n
\t      } catch(e) {\n
\t\t    return false;\n
\t      }\n
        }\n
      }\n
      return aObj;\n
    }\n
\n
    function checkClientInstallation() {\n
       time_out = window.setTimeout( "checkClientInstallation()", 5000 );\n
       var xhr_object = null;\n
       xhr_object = getNewXMLHTTP();\n
       xhr_object.onreadystatechange = function()\n
       {\n
         var status = document.getElementById(\'client_installation_status\');\n
         if(xhr_object.readyState == 4)\n
         {\n
           if(xhr_object.status == 200)\n
           {\n
             status.innerHTML = xhr_object.responseText;\n
           }\n
           else\n
             status.innerHTML = "Error code " + xhr_object.status;\n
         };\n
       }\n
       xhr_object.open( "GET",\n
                        "portal_configurator/getInstallationStatusReport?active_process_id=%s",\n
                        true);\n
       //xhr_object.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");\n
       xhr_object.setRequestHeader("Content-Type", "text/html");  \n
       xhr_object.setRequestHeader("Cache-Control", "no-cache" ) \n
       xhr_object.setRequestHeader("If-Modified-Since", "Sat, 1 Jan 2000 00:00:00 GMT" ) \n
       xhr_object.send(null);\n
    }\n
\n
    function init() {\n
      checkClientInstallation();\n
    }\n
\n
""" %(active_process_id)\n
\n
return js_string\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ConfiguratorTool_generateJavaScript</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Generate JavaScript code which will query wizard to get installation status</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
