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
                <string>Assignee</string>
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
                <string>Assignee</string>
                <string>Assignor</string>
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
            <key> <string>categories</string> </key>
            <value>
              <tuple>
                <string>contributor/person_module/1</string>
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
            <value> <string>gadget_officejs_drive_page_browse.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_drive_officejs_page_browse_js</string> </value>
        </item>
        <item>
            <key> <string>language</string> </key>
            <value>
              <none/>
            </value>
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

/*globals window, rJS, RSVP, jIO, loopEventListener, document */\n
/*jslint indent: 2, nomen: true, maxlen: 80*/\n
(function (window, rJS, RSVP, jIO, loopEventListener, document) {\n
  "use strict";\n
\n
  var gadget_klass = rJS(window);\n
\n
  gadget_klass\n
    .ready(function (g) {\n
      g.props = {};\n
      return g.getElement()\n
        .push(function (element) {\n
          g.props.element = element;\n
        });\n
    })\n
\n
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")\n
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")\n
\n
    .declareAcquiredMethod("redirect", "redirect")\n
\n
    .declareMethod("parse", function (text) {\n
      //XXX use jison here instead of parsing manually\n
      var command,\n
        args = text.split(\' \'),\n
        index;\n
      // command is the first token\n
      command = args.shift();\n
\n
      /* begin from the end because removing some values from the list\n
         while looping */\n
      for (index = args.length ; index > 0 ; index --) {\n
        // remove emply strings from argument list\n
        if (args[index] === \'\') {\n
          args.splice(index, 1);\n
        }\n
      }\n
      return {command: command, args: args};\n
    })\n
\n
    .declareMethod("browse", function (command, args) {\n
      var gadget = this,\n
        requireSingleArgError = new Error(\n
          \'This command requires one argument.\'\n
        );\n
\n
      function absolutePosition(current, requested) {\n
        var pos;\n
        if (requested.startsWith(\'/\')) {\n
          pos = \'/\' + requested;\n
        } else {\n
          pos = current + \'/\' + requested;\n
        }\n
        return pos.replace(/\\/+/g, \'/\');\n
      }\n
      // if command given: proceed\n
\n
      if (command) {\n
        try {\n
          switch (command) {\n
          case \'cd\':\n
            if (args.length === 1) {\n
              return gadget.redirect({\n
                position: absolutePosition(gadget.props.currentPosition,\n
                                           args[0] + \'/\')\n
              });\n
            }\n
            throw requireSingleArgError;\n
\n
          case \'vim\':\n
          case \'vi\':\n
            if (args.length === 1) {\n
              return gadget.redirect({\n
                page: \'edit\',\n
                resource: absolutePosition(gadget.props.currentPosition,\n
                                           args[0]),\n
                back: gadget.props.currentPosition\n
              });\n
            }\n
            throw requireSingleArgError;\n
          case \'share\':\n
            if (args.length === 1) {\n
              return gadget.jio_getAttachment(absolutePosition(\n
                gadget.props.currentPosition,\n
                args[0]\n
              ), \'enclosure\')\n
                .push(function (resp) {\n
                  return jIO.util.readBlobAsDataURL(resp);\n
                })\n
                .push(function (e) {\n
                  gadget.props.element.querySelector(\'.output\').textContent = e.target.result;\n
                });\n
            }\n
            throw requireSingleArgError;\n
          default:\n
            throw new Error(\'Unknown command: \' + command);\n
          }\n
        } catch (e) {\n
          gadget.props.element.querySelector(\'.error\').textContent = e.name +\n
                                                                     ": " +\n
                                                                     e.message;\n
        }\n
      }\n
    })\n
\n
    .declareMethod("render", function (options) {\n
      var gadget = this,\n
        ul = gadget.props.element.querySelector(\'ul\');\n
\n
      // redirect to root if no position given\n
      if (!options.position) {\n
        return gadget.redirect({\n
          position: \'/\'\n
        });\n
      }\n
      gadget.props.currentPosition = options.position;\n
      gadget.props.element.querySelector(\'input\').value = \'\';\n
\n
      // clean previous ul children\n
      while (ul.hasChildNodes()) {\n
        ul.removeChild(ul.firstChild);\n
      }\n
      return gadget.jio_allDocs({id: options.position})\n
        .push(function (all) {\n
          var key,\n
            li,\n
            id,\n
            liContent,\n
            resourceName;\n
          for (key in all.data.rows) {\n
            if (all.data.rows.hasOwnProperty(key)) {\n
              id = all.data.rows[key].value.id;\n
              li = document.createElement(\'li\');\n
              resourceName = document.createTextNode(id);\n
\n
              if (id.endsWith(\'.txt\') || id.endsWith(\'.js\') ||\n
                  id.endsWith(\'.html\') || id.endsWith(\'.py\') ||\n
                  id.endsWith(\'_js\')) {\n
                liContent = document.createElement(\'a\');\n
\n
                liContent.setAttribute(\'href\', \'#page=edit&resource=\' +\n
                                       [options.position, id].join(\'/\') +\n
                                       \'&back=\' + options.position);\n
                liContent.appendChild(resourceName);\n
              } else {\n
                liContent = resourceName;\n
              }\n
              li.appendChild(liContent);\n
              ul.appendChild(li);\n
            }\n
          }\n
        });\n
    })\n
\n
    .declareService(function () {\n
      var gadget = this;\n
\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return loopEventListener(\n
            gadget.props.element.querySelector(\'form\'),\n
            \'submit\',\n
            true,\n
            function () {\n
              var input = gadget.props.element.querySelector(\'input\');\n
              return gadget.parse(input.value)\n
                .push(function (fullCommand) {\n
                  var args = fullCommand.args,\n
                    command = fullCommand.command;\n
                  gadget.browse(command, args);\n
                });\n
            }\n
          );\n
        });\n
    });\n
\n
}(window, rJS, RSVP, jIO, loopEventListener, document));

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>OfficeJS Drive Page Browse JS</string> </value>
        </item>
        <item>
            <key> <string>version</string> </key>
            <value>
              <none/>
            </value>
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
                <value> <string>publish_alive</string> </value>
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
                        <float>1451484012.13</float>
                        <string>UTC</string>
                      </tuple>
                    </state>
                  </object>
                </value>
            </item>
            <item>
                <key> <string>validation_state</string> </key>
                <value> <string>published_alive</string> </value>
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
                <value> <string>949.20889.54493.42188</string> </value>
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
                        <float>1456146835.69</float>
                        <string>UTC</string>
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
                        <float>1451482803.15</float>
                        <string>UTC</string>
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
