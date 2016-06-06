<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="Web Script" module="erp5.portal_type"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Access_contents_information_Permission</string> </key>
            <value>
              <tuple>
                <string>Anonymous</string>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Associate</string>
                <string>Auditor</string>
                <string>Manager</string>
                <string>Owner</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>_Add_portal_content_Permission</string> </key>
            <value>
              <tuple>
                <string>Assignor</string>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>_Change_local_roles_Permission</string> </key>
            <value>
              <tuple>
                <string>Assignor</string>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>_Modify_portal_content_Permission</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>_View_Permission</string> </key>
            <value>
              <tuple>
                <string>Anonymous</string>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Associate</string>
                <string>Auditor</string>
                <string>Manager</string>
                <string>Owner</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>content_md5</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>default_reference</string> </key>
            <value> <string>gadget_manifest_page_components.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_manifest_page_components_js</string> </value>
        </item>
        <item>
            <key> <string>language</string> </key>
            <value> <string>en</string> </value>
        </item>
        <item>
            <key> <string>portal_type</string> </key>
            <value> <string>Web Script</string> </value>
        </item>
        <item>
            <key> <string>short_title</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>text_content</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*global window, rJS, RSVP */\n
/*jslint nomen: true, indent: 2, maxerr: 3 */\n
(function (window, rJS, RSVP) {\n
  "use strict";\n
\n
  /////////////////////////////////////////////////////////////////\n
  // api\n
  /////////////////////////////////////////////////////////////////\n
\n
  /////////////////////////////////////////////////////////////////\n
  // some methods\n
  /////////////////////////////////////////////////////////////////\n
\n
  /////////////////////////////////////////////////////////////////\n
  // RJS\n
  /////////////////////////////////////////////////////////////////\n
\n
  rJS(window)\n
\n
    /////////////////////////////////////////////////////////////////\n
    // ready\n
    /////////////////////////////////////////////////////////////////\n
    .ready(function (my_gadget) {\n
      my_gadget.property_dict = {};\n
    })\n
\n
    .ready(function (my_gadget) {\n
      return my_gadget.getElement()\n
        .push(function (my_element) {\n
          my_gadget.property_dict.element = my_element;\n
        });\n
    })\n
\n
    /////////////////////////////////////////////////////////////////\n
    // published methods\n
    /////////////////////////////////////////////////////////////////\n
\n
    /////////////////////////////////////////////////////////////////\n
    // acquired methods\n
    /////////////////////////////////////////////////////////////////\n
\n
    /////////////////////////////////////////////////////////////////\n
    // published methods\n
    /////////////////////////////////////////////////////////////////\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared methods\n
    /////////////////////////////////////////////////////////////////\n
    // thx https://github.com/jsbin/jsbin/blob/master/docs/embedding.md\n
    .declareMethod("renderIframe", function (my_form) {\n
      var relevant_link_list = [my_form],\n
        className = \'\',\n
        innerText,\n
        i,\n
        len;\n
\n
      function findCodeInParent(my_element) {\n
        var match = my_element;\n
      \n
        while (match = match.previousSibling) {\n
          if (match.nodeName === \'PRE\') {\n
            break;\n
          }\n
          if (match.getElementsByTagName) {\n
            match = match.getElementsByTagName(\'pre\');\n
            if (match.length) {\n
              match = match[0]; // only grabs the first\n
              break;\n
            }\n
          }\n
        }\n
      \n
        if (match) {\n
          return match;\n
        }\n
      \n
        match = my_element.parentNode.getElementsByTagName(\'pre\');\n
      \n
        if (!match.length) {\n
          if (my_element.parentNode) {\n
            return findCodeInParent(my_element.parentNode);\n
          } else {\n
            return null;\n
          }\n
        }\n
      \n
        return match[0];\n
      }\n
\n
      function getQuery(my_querystring) {\n
        var query = {};\n
      \n
        var pairs = my_querystring.split(\'&\'),\n
            length = pairs.length,\n
            keyval = [],\n
            i = 0;\n
      \n
        for (; i < length; i++) {\n
          keyval = pairs[i].split(\'=\', 2);\n
          try {\n
            keyval[0] = decodeURIComponent(keyval[0]); // key\n
            keyval[1] = decodeURIComponent(keyval[1]); // value\n
          } catch (e) {}\n
      \n
          if (query[keyval[0]] === undefined) {\n
            query[keyval[0]] = keyval[1];\n
          } else {\n
            query[keyval[0]] += \',\' + keyval[1];\n
          }\n
        }\n
      \n
        return query;\n
      }\n
\n
      function findCode(my_link) {\n
        var rel = my_link.rel,\n
          query = my_link.search.substring(1),\n
          element,\n
          code;\n
      \n
        if (rel && (element = document.getElementById(rel.substring(1)))) {\n
          code = element[innerText];\n
        } else {\n
          // go looking through it\'s parents\n
          element = findCodeInParent(my_link);\n
          if (element) {\n
            code = element[innerText];\n
          }\n
        }\n
      \n
        return code;\n
      }\n
      \n
      function detectLanguage(my_code) {\n
        var htmlcount = (my_code.split("<").length - 1),\n
          csscount = (my_code.split("{").length - 1),\n
          jscount = (my_code.split(".").length - 1);\n
      \n
        if (htmlcount > csscount && htmlcount > jscount) {\n
          return \'html\';\n
        } else if (csscount > htmlcount && csscount > jscount) {\n
          return \'css\';\n
        } else {\n
          return \'javascript\';\n
        }\n
      }\n
      \n
      function scoop(my_link) {\n
        var code = findCode(my_link),\n
          language = detectLanguage(code),\n
          query = my_link.search.substring(1);\n
      \n
        if (language === \'html\' && code.toLowerCase().indexOf(\'<html\') === -1) {\n
          // assume HTML fragment - so try to insert in the %code% position\n
          language = \'code\';\n
        }\n
      \n
        if (query.indexOf(language) === -1) {\n
          query += \',\' + language + \'=\' + encodeURIComponent(code);\n
        } else {\n
          query = query.replace(\n
            language,\n
            language + \'=\' + encodeURIComponent(code)\n
          );\n
        }\n
      \n
        my_link.search = \'?\' + query;\n
      }\n
      \n
      function embed(my_link) {\n
        var iframe = document.createElement(\'iframe\'),\n
          resize = document.createElement(\'div\'),\n
          url = my_link.action.replace(/edit/, \'embed\'),\n
          query,\n
          onmessage;\n
\n
        iframe.src = url.split(\'&\')[0];\n
        iframe._src = url.split(\'&\')[0]; // support for google slide embed\n
        iframe.className = my_link.className; // inherit all classes from link\n
        iframe.id = my_link.id; // also inherit, give more style control to user\n
        iframe.style.border = \'1px solid #aaa\';\n
      \n
        //query = getQuery(my_link.search);\n
        query = {};\n
        iframe.style.width = query.width || \'100%\';\n
        iframe.style.minHeight = query.height || \'300px\';\n
\n
        if (query.height) {\n
          iframe.style.maxHeight = query.height;\n
        }\n
        my_link.parentNode.replaceChild(iframe, my_link);\n
\n
        onmessage = function (event) {\n
          event || (event = window.event);\n
          // * 1 to coerse to number, and + 2 to compensate for border\n
          iframe.style.height = (event.data.height * 1 + 2) + \'px\';\n
        };\n
      \n
        if (window.addEventListener) {\n
          window.addEventListener(\'message\', onmessage, false);\n
        } else {\n
          window.attachEvent(\'onmessage\', onmessage);\n
        }\n
      }\n
      \n
      // start\n
      if (document.createElement(\'i\').innerText === undefined) {\n
        innerText = \'textContent\';\n
      } else {\n
        innerText = \'innerText\';\n
      }\n
\n
      for (i = 0, len = relevant_link_list.length; i < len; i += 1) {\n
        className = \' \' + relevant_link_list[i].className + \' \';\n
        \n
        if (className.indexOf(\' jsbin-scoop \') !== -1) {\n
          scoop(relevant_link_list[i]);\n
        } else if (className.indexOf(\' jsbin-embed \') !== -1) {\n
          embed(relevant_link_list[i]);\n
        }\n
      }\n
      \n
      return {};\n
    })\n
\n
    .declareMethod("render", function (option_dict) {\n
      return this;\n
    })\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared service\n
    /////////////////////////////////////////////////////////////////\n
    .declareService(function () {\n
      var gadget = this,\n
        element = gadget.property_dict.element,\n
        form_list = element.querySelectorAll(\'form\'),\n
        loop_list = [],\n
        i,\n
        len;\n
\n
      function formSubmit(e) {\n
        e.preventDefault();\n
        gadget.renderIframe(e.target);\n
        return false;\n
      }\n
\n
      // Listen to form submit\n
      for (i = 0, len = form_list.length; i < len; i += 1) {\n
        loop_list.push(\n
          loopEventListener(form_list[i], \'submit\', false, formSubmit)\n
        );\n
      }\n
      \n
      return RSVP.all(loop_list);\n
    });\n
\n
}(window, rJS, RSVP));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Gadget Manifest Page Components JS</string> </value>
        </item>
        <item>
            <key> <string>version</string> </key>
            <value> <string>001</string> </value>
        </item>
        <item>
            <key> <string>workflow_history</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAI=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="2" aka="AAAAAAAAAAI=">
    <pickle>
      <global name="PersistentMapping" module="Persistence.mapping"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value>
              <dictionary>
                <item>
                    <key> <string>document_publication_workflow</string> </key>
                    <value>
                      <persistent> <string encoding="base64">AAAAAAAAAAM=</string> </persistent>
                    </value>
                </item>
                <item>
                    <key> <string>edit_workflow</string> </key>
                    <value>
                      <persistent> <string encoding="base64">AAAAAAAAAAQ=</string> </persistent>
                    </value>
                </item>
                <item>
                    <key> <string>processing_status_workflow</string> </key>
                    <value>
                      <persistent> <string encoding="base64">AAAAAAAAAAU=</string> </persistent>
                    </value>
                </item>
              </dictionary>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="3" aka="AAAAAAAAAAM=">
    <pickle>
      <global name="WorkflowHistoryList" module="Products.ERP5Type.patches.WorkflowTool"/>
    </pickle>
    <pickle>
      <tuple>
        <none/>
        <list>
          <dictionary>
            <item>
                <key> <string>action</string> </key>
                <value> <string>publish</string> </value>
            </item>
            <item>
                <key> <string>actor</string> </key>
                <value> <string>zope</string> </value>
            </item>
            <item>
                <key> <string>comment</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>error_message</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>time</string> </key>
                <value>
                  <object>
                    <klass>
                      <global name="DateTime" module="DateTime.DateTime"/>
                    </klass>
                    <tuple>
                      <none/>
                    </tuple>
                    <state>
                      <tuple>
                        <float>1432215606.07</float>
                        <string>GMT</string>
                      </tuple>
                    </state>
                  </object>
                </value>
            </item>
            <item>
                <key> <string>validation_state</string> </key>
                <value> <string>published</string> </value>
            </item>
          </dictionary>
        </list>
      </tuple>
    </pickle>
  </record>
  <record id="4" aka="AAAAAAAAAAQ=">
    <pickle>
      <global name="WorkflowHistoryList" module="Products.ERP5Type.patches.WorkflowTool"/>
    </pickle>
    <pickle>
      <tuple>
        <none/>
        <list>
          <dictionary>
            <item>
                <key> <string>action</string> </key>
                <value> <string>edit</string> </value>
            </item>
            <item>
                <key> <string>actor</string> </key>
                <value> <string>zope</string> </value>
            </item>
            <item>
                <key> <string>comment</string> </key>
                <value>
                  <none/>
                </value>
            </item>
            <item>
                <key> <string>error_message</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>serial</string> </key>
                <value> <string>943.10945.22885.62037</string> </value>
            </item>
            <item>
                <key> <string>state</string> </key>
                <value> <string>current</string> </value>
            </item>
            <item>
                <key> <string>time</string> </key>
                <value>
                  <object>
                    <klass>
                      <global name="DateTime" module="DateTime.DateTime"/>
                    </klass>
                    <tuple>
                      <none/>
                    </tuple>
                    <state>
                      <tuple>
                        <float>1432216457.85</float>
                        <string>GMT</string>
                      </tuple>
                    </state>
                  </object>
                </value>
            </item>
          </dictionary>
        </list>
      </tuple>
    </pickle>
  </record>
  <record id="5" aka="AAAAAAAAAAU=">
    <pickle>
      <global name="WorkflowHistoryList" module="Products.ERP5Type.patches.WorkflowTool"/>
    </pickle>
    <pickle>
      <tuple>
        <none/>
        <list>
          <dictionary>
            <item>
                <key> <string>action</string> </key>
                <value> <string>detect_converted_file</string> </value>
            </item>
            <item>
                <key> <string>actor</string> </key>
                <value> <string>zope</string> </value>
            </item>
            <item>
                <key> <string>comment</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>error_message</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>external_processing_state</string> </key>
                <value> <string>converted</string> </value>
            </item>
            <item>
                <key> <string>serial</string> </key>
                <value> <string>0.0.0.0</string> </value>
            </item>
            <item>
                <key> <string>time</string> </key>
                <value>
                  <object>
                    <klass>
                      <global name="DateTime" module="DateTime.DateTime"/>
                    </klass>
                    <tuple>
                      <none/>
                    </tuple>
                    <state>
                      <tuple>
                        <float>1432215589.04</float>
                        <string>GMT</string>
                      </tuple>
                    </state>
                  </object>
                </value>
            </item>
          </dictionary>
        </list>
      </tuple>
    </pickle>
  </record>
</ZopeData>
