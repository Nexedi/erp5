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
            <value> <string>gadget_manifest.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_manifest_js</string> </value>
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

/*global window, document, rJS, RSVP, jQuery, console, jQuery, XMLHttpRequest, loopEventListener, URI, location */\n
/*jslint nomen: true, indent: 2, maxerr: 3 */\n
(function (window, document, rJS, RSVP, $, XMLHttpRequest, console, loopEventListener, location) {\n
  "use strict";\n
\n
  var DEFAULT_VIEW_REFERENCE = "view";\n
\n
  /////////////////////////////////////////////////////////////////\n
  // Desactivate jQuery Mobile URL management\n
  /////////////////////////////////////////////////////////////////\n
  $.mobile.ajaxEnabled = false;\n
  $.mobile.linkBindingEnabled = false;\n
  $.mobile.hashListeningEnabled = false;\n
  $.mobile.pushStateEnabled = false;\n
\n
  /////////////////////////////////////////////////////////////////\n
  // Some functions\n
  /////////////////////////////////////////////////////////////////\n
  function mergeSubDict(dict) {\n
    var subkey,\n
      subkey2,\n
      subresult2,\n
      value,\n
      result = {};\n
    for (subkey in dict) {\n
      if (dict.hasOwnProperty(subkey)) {\n
        value = dict[subkey];\n
        if (value instanceof Object) {\n
          subresult2 = mergeSubDict(value);\n
          for (subkey2 in subresult2) {\n
            if (subresult2.hasOwnProperty(subkey2)) {\n
              // XXX key should not have an . inside\n
              if (result.hasOwnProperty(subkey + "." + subkey2)) {\n
                throw new Error("Key " + subkey + "." +\n
                                subkey2 + " already present");\n
              }\n
              result[subkey + "." + subkey2] = subresult2[subkey2];\n
            }\n
          }\n
        } else {\n
          if (result.hasOwnProperty(subkey)) {\n
            throw new Error("Key " + subkey + " already present");\n
          }\n
          result[subkey] = value;\n
        }\n
      }\n
    }\n
    return result;\n
  }\n
\n
  function listenHashChange(gadget) {\n
\n
    function extractHashAndDispatch(evt) {\n
      var hash = (evt.newURL || window.location.toString()).split(\'#\')[1],\n
        subhashes,\n
        subhash,\n
        keyvalue,\n
        index,\n
        options = {};\n
      if (hash === undefined) {\n
        hash = "";\n
      } else {\n
        hash = hash.split(\'?\')[0];\n
      }\n
\n
      function optionalize(key, value, dict) {\n
        var key_list = key.split("."),\n
          kk,\n
          i;\n
        for (i = 0; i < key_list.length; i += 1) {\n
          kk = key_list[i];\n
          if (i === key_list.length - 1) {\n
            dict[kk] = value;\n
          } else {\n
            if (!dict.hasOwnProperty(kk)) {\n
              dict[kk] = {};\n
            }\n
            dict = dict[kk];\n
          }\n
        }\n
      }\n
\n
      subhashes = hash.split(\'&\');\n
      for (index in subhashes) {\n
        if (subhashes.hasOwnProperty(index)) {\n
          subhash = subhashes[index];\n
          if (subhash !== \'\') {\n
            keyvalue = subhash.split(\'=\');\n
            if (keyvalue.length === 2) {\n
\n
              optionalize(decodeURIComponent(keyvalue[0]),\n
                decodeURIComponent(keyvalue[1]),\n
                options);\n
\n
            }\n
          }\n
        }\n
      }\n
\n
      if (gadget.renderXXX !== undefined) {\n
        return gadget.renderXXX(options);\n
      }\n
    }\n
\n
    var result = loopEventListener(window, \'hashchange\', false,\n
                                   extractHashAndDispatch),\n
      event = document.createEvent("Event");\n
\n
    event.initEvent(\'hashchange\', true, true);\n
    event.newURL = window.location.toString();\n
    window.dispatchEvent(event);\n
    return result;\n
  }\n
\n
  function renderPage(gadget, page_name, options) {\n
    return gadget.declareGadget(page_name, {\n
      scope: "pg"\n
    })\n
      .push(function (page_gadget) {\n
        var sub_options = options.pg || {},\n
          key;\n
        delete options.pg;\n
        for (key in options) {\n
          if (options.hasOwnProperty(key)) {\n
            sub_options[key] = options[key];\n
          }\n
        }\n
        return RSVP.all([\n
          page_gadget,\n
          page_gadget.render(sub_options)\n
        ]);\n
      })\n
      .push(function (all_result) {\n
        return all_result[0];\n
      });\n
  }\n
\n
  function displayErrorContent(gadget, error) {\n
    // Do not break the application in case of errors.\n
    // Display it to the user for now, and allow user to go back to the frontpage\n
    var error_text = "";\n
    if ((error.target !== undefined) && (error.target.status === 401)) {\n
      // Redirect to the login view\n
      return gadget.aq_pleasePublishMyState({page: "login"})\n
        .push(gadget.pleaseRedirectMyHash.bind(gadget));\n
    }\n
    if (error instanceof RSVP.CancellationError) {\n
      return;\n
    }\n
\n
    if (error instanceof XMLHttpRequest) {\n
      error_text = error.toString() + " " +\n
        error.status + " " +\n
        error.statusText;\n
    } else if (error instanceof Error) {\n
      error_text = error.toString();\n
    } else {\n
      error_text = JSON.stringify(error);\n
    }\n
\n
    console.error(error);\n
    console.error(error.stack);\n
    // XXX Improve error rendering\n
    gadget.props.article.innerHTML = "<br/><br/><br/><pre></pre>";\n
    gadget.props.article.querySelector(\'pre\').textContent = "Error: " + error_text;\n
  }\n
\n
  function displayError(gadget, error) {\n
    return gadget.getDeclaredGadget("header")\n
      .push(function (g) {\n
        return g.notifyError();\n
      })\n
      .push(function () {\n
        return displayErrorContent(gadget, error);\n
      })\n
      .push(function () {\n
        return gadget.dropGadget("pg")\n
          .push(undefined, function () {\n
            // Do not crash the app if the pg gadget in not defined\n
            // ie, keep the original error on screen\n
            return;\n
          });\n
      });\n
  }\n
\n
  /////////////////////////////////////////////////////////////////\n
  // Gadget behaviour\n
  /////////////////////////////////////////////////////////////////\n
\n
  rJS(window)\n
    /////////////////////////////////////////////////////////////////\n
    // ready\n
    /////////////////////////////////////////////////////////////////\n
    // Init local properties\n
    .ready(function (g) {\n
      g.props = {\n
        translation_lookup: ""\n
      };\n
//      return g.getDeclaredGadget("breadcrumb")\n
//        .push(function (sub_gadget) {\n
//          g.props.breadcrumb_gadget = sub_gadget;\n
//        });\n
    })\n
\n
    .ready(function (g) {\n
      return g.getElement()\n
        .push(function (element) {\n
          g.props.element = element;\n
          g.props.article = element.querySelector("article");\n
\n
          // XXX Will work only if top gadget...\n
          var element_list = document.querySelectorAll("[data-renderjs-configuration]"),\n
            len = element_list.length,\n
            key,\n
            value,\n
            i;\n
\n
          for (i = 0; i < len; i += 1) {\n
            key = element_list[i].getAttribute(\'data-renderjs-configuration\');\n
            value = element_list[i].textContent;\n
            if (value !== "") {\n
              g.props[key] = value;\n
            }\n
          }\n
        });\n
    })\n
\n
    .declareMethod("aq_pleasePublishMyState", function (options) {\n
      var key,\n
        first = true,\n
        hash = "#";\n
      options = mergeSubDict(options);\n
      for (key in options) {\n
        if (options.hasOwnProperty(key)) {\n
          if (!first) {\n
            hash += "&";\n
          }\n
          hash += encodeURIComponent(key) + "=" +\n
            encodeURIComponent(options[key]);\n
          first = false;\n
        }\n
      }\n
      return hash;\n
    })\n
\n
    /////////////////////////////////////////////////////////////////\n
    // handle acquisition\n
    /////////////////////////////////////////////////////////////////\n
    .declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash")\n
\n
    // bridge translation gadget\n
    .allowPublicAcquisition("getTranslationMethod", function () {\n
      var root = (new URI(this.props.hateoas_url)).absoluteTo(location.href).toString();\n
      return root + this.props.translation_lookup;\n
    })\n
    .allowPublicAcquisition("changeLanguage", function (param_list) {\n
      if (this.setLanguage) {\n
        return this.getDeclaredGadget("translate")\n
          .push(function (translation_gadget) {\n
            return translation_gadget.changeLanguage.apply(\n
              translation_gadget,\n
              param_list\n
            );\n
          });\n
      }\n
    })\n
    .allowPublicAcquisition("getLanguageList", function (param_list) {\n
      if (this.setLanguage) {\n
        return this.getDeclaredGadget("translate")\n
          .push(function (translation_gadget) {\n
            return translation_gadget.getLanguageList.apply(\n
              translation_gadget,\n
              param_list\n
            );\n
          });\n
      }\n
      return JSON.stringify([]);\n
    })\n
    .allowPublicAcquisition("translateHtml", function (param_list) {\n
      if (this.setLanguage) {\n
        return this.getDeclaredGadget("translate")\n
          .push(function (translation_gadget) {\n
            return translation_gadget.translateHtml.apply(\n
              translation_gadget,\n
              param_list\n
            );\n
          });\n
      }\n
      return param_list;\n
    })\n
\n
    .allowPublicAcquisition("whoWantToDisplayThis", function (param_list) {\n
      // Hey, I want to display some URL\n
      var options = {\n
        jio_key: param_list[0],\n
        view: DEFAULT_VIEW_REFERENCE\n
      };\n
      if (param_list[1] !== undefined) {\n
        if (param_list[1].editable !== undefined) {\n
          options.editable = param_list[1].editable;\n
        }\n
      }\n
      return this.aq_pleasePublishMyState(options);\n
    })\n
    .allowPublicAcquisition("whoWantToDisplayThisPage", function (param_list) {\n
      // Hey, I want to display some URL\n
      var options = {\n
        jio_key: this.state_parameter_dict.jio_key,\n
        view: param_list[0].name || DEFAULT_VIEW_REFERENCE\n
      };\n
      if (param_list[0].editable !== undefined) {\n
        options.editable = param_list[0].editable;\n
      }\n
      if (param_list[0].page !== undefined) {\n
        options.page = param_list[0].page;\n
      }\n
      return this.aq_pleasePublishMyState(options);\n
    })\n
    .allowPublicAcquisition("whoWantToDisplayThisFrontPage", function (param_list) {\n
      // Hey, I want to display some URL\n
      var options = {\n
        page: param_list[0]\n
      };\n
      return this.aq_pleasePublishMyState(options);\n
    })\n
\n
    .allowPublicAcquisition("renderPageHeader", function (param_list) {\n
      // XXX Sven hack: number of _url determine padding for subheader on ui-content \n
      function hasSubNavigation(my_param_dict) {\n
        var i,\n
          count = 0;\n
        for (i in my_param_dict) {\n
          if (my_param_dict.hasOwnProperty(i) && i.indexOf("_url") > -1) {\n
            count += 1;\n
          }\n
        }\n
        return count;\n
      }\n
\n
      if (hasSubNavigation(param_list[0]) > 2) {\n
        this.props.sub_header_class = "ui-has-subheader";\n
      }\n
      this.props.header_argument_list = param_list;\n
    })\n
\n
    .allowPublicAcquisition(\'reportServiceError\', function (param_list, gadget_scope) {\n
      if (gadget_scope === undefined) {\n
        // don\'t fail in case of dropped subgadget (like previous page)\n
        // only accept errors from header, panel and displayed page\n
        return;\n
      }\n
      return displayError(this, param_list[0]);\n
    })\n
    // XXX translate: while header calls render on ready, this is needed to\n
    // update the header once translations are available\n
    .allowPublicAcquisition(\'notifyUpdate\', function () {\n
      return this.getDeclaredGadget("header")\n
        .push(function (header_gadget) {\n
          return header_gadget.notifyUpdate();\n
        });\n
    })\n
    .allowPublicAcquisition(\'notifySubmitting\', function () {\n
      return this.getDeclaredGadget("header")\n
        .push(function (header_gadget) {\n
          return header_gadget.notifySubmitting();\n
        });\n
    })\n
\n
    .allowPublicAcquisition(\'notifySubmitted\', function () {\n
      return this.getDeclaredGadget("header")\n
        .push(function (header_gadget) {\n
          return header_gadget.notifySubmitted();\n
        });\n
    })\n
    .allowPublicAcquisition(\'notifyChange\', function () {\n
      return this.getDeclaredGadget("header")\n
        .push(function (header_gadget) {\n
          return header_gadget.notifyChange();\n
        });\n
    })\n
    .allowPublicAcquisition(\'triggerSubmit\', function () {\n
      return this.getDeclaredGadget("pg")\n
        .push(function (page_gadget) {\n
          return page_gadget.triggerSubmit();\n
        });\n
    })\n
    .allowPublicAcquisition(\'triggerPanel\', function () {\n
      return this.getDeclaredGadget("panel")\n
        .push(function (panel_gadget) {\n
          return panel_gadget.toggle();\n
        });\n
    })\n
    .allowPublicAcquisition(\'getSiteRoot\', function () {\n
      return this.getSiteRoot();\n
    })\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared methods\n
    /////////////////////////////////////////////////////////////////\n
\n
    // XXX translate: called before ready(), so props is not available.\n
    // Needed to lookup to retrieve HAL to fetch site module/runner languages \n
    .declareMethod(\'getSiteRoot\', function () {\n
      return (new URI(this.props.hateoas_url)).absoluteTo(location.href).toString();\n
    })\n
\n
    // Render the page\n
    .declareMethod(\'configure\', function (options) {\n
      var gadget = this,\n
        elements,\n
        div,\n
        key;\n
      for (key in options) {\n
        if (options.hasOwnProperty(key)) {\n
          if (key === "translation_lookup") {\n
            gadget.setLanguage = true;\n
          }\n
          gadget.props[key] = options[key];\n
        }\n
      }\n
      if (gadget.setLanguage) {\n
        elements = gadget.props.element;\n
        div = document.createElement("div");\n
        elements.appendChild(div);\n
        return new RSVP.Queue()\n
          .push(function () {\n
            return gadget.declareGadget("gadget_translate.html",\n
                                        {scope: "translate"});\n
          })\n
          .push(function () {\n
            return gadget.dropGadget("panel");\n
          })\n
          .push(function () {\n
            return gadget.declareGadget(gadget.props.panel_gadget,\n
                                         {scope: "panel",\n
                                          element: div});\n
          })\n
          .push(function () {\n
            return createJio(gadget);\n
          });\n
      }\n
    })\n
\n
    // Render the page\n
    .declareMethod(\'renderXXX\', function (options) {\n
      var gadget = this,\n
        header_gadget,\n
        panel_gadget,\n
        main_gadget;\n
\n
      gadget.props.options = options;\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return RSVP.all([\n
            gadget.getDeclaredGadget("header"),\n
            gadget.getDeclaredGadget("panel")\n
          ]);\n
        })\n
        .push(function (my_gadget_list) {\n
          header_gadget = my_gadget_list[0];\n
          panel_gadget = my_gadget_list[1];\n
          return RSVP.all([\n
            panel_gadget.render({}),\n
            header_gadget.notifyLoading()\n
          ]);\n
        })\n
        .push(function () {\n
          // By default, init the header options to be empty (ERP5 title by default + sidebar)\n
          gadget.props.header_argument_list = [{\n
            panel_action: true,\n
            page_title: gadget.props.application_title || "ERP5"\n
          }];\n
\n
          gadget.state_parameter_dict = {\n
            jio_key: options.jio_key,\n
            view: options.view\n
          };\n
\n
          if ((options.jio_key !== undefined) && (options.page === undefined)) {\n
            options.page = "form";\n
            options.view = options.view || DEFAULT_VIEW_REFERENCE;\n
          }\n
          if (options.page === undefined) {\n
            // Not rendering a jio document and not page requested.\n
            // URL is probably empty: redirect to the frontpage\n
            // Check if a custom frontpage is defined\n
            if (!gadget.props.frontpage_gadget) {\n
              return gadget.aq_pleasePublishMyState({page: \'front\'})\n
                .push(gadget.pleaseRedirectMyHash.bind(gadget));\n
            }\n
            return renderPage(gadget, gadget.props.frontpage_gadget, options);\n
          }\n
\n
          return renderPage(gadget, "gadget_manifest_page_" + options.page + ".html", options);\n
        })\n
\n
        .push(function (result) {\n
          main_gadget = result;\n
\n
          return header_gadget.render.apply(header_gadget, gadget.props.header_argument_list);\n
        })\n
        .push(function () {\n
          // Append loaded gadget in the page\n
          if (main_gadget !== undefined) {\n
            return main_gadget.getElement()\n
              .push(function (fragment) {\n
                var element = gadget.props.article,\n
                  content_container = document.createElement("div");\n
                content_container.className = "ui-content " + (gadget.props.sub_header_class || "");\n
                // reset subheader indicator\n
                delete gadget.props.sub_header_class;\n
\n
                // go to the top of the page\n
                window.scrollTo(0, 0);\n
\n
                // Clear first to DOM, append after to reduce flickering/manip\n
                while (element.firstChild) {\n
                  element.removeChild(element.firstChild);\n
                }\n
                content_container.appendChild(fragment);\n
                element.appendChild(content_container);\n
\n
                $(element).trigger("create");\n
                return header_gadget.notifyLoaded();\n
              });\n
          }\n
        })\n
\n
        .push(undefined, function (error) {\n
          return displayError(gadget, error);\n
        });\n
    })\n
\n
    .declareService(function () {\n
      ////////////////////////////////////\n
      // Form submit listening. Prevent browser to automatically handle the form submit in case of a bug\n
      ////////////////////////////////////\n
      var gadget = this;\n
\n
      function catchFormSubmit() {\n
        return displayError(new Error("Unexpected form submit"));\n
      }\n
\n
      // Listen to form submit\n
      return loopEventListener(\n
        gadget.props.element,\n
        \'submit\',\n
        false,\n
        catchFormSubmit\n
      );\n
    })\n
\n
\n
    .declareService(function () {\n
      return listenHashChange(this);\n
    });\n
\n
}(window, document, rJS, RSVP, jQuery, XMLHttpRequest, console, loopEventListener, location));

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>RenderJS Gadget Manifest JS</string> </value>
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
                        <float>1432218773.4</float>
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
                <value> <string>949.36660.60257.7577</string> </value>
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
                        <float>1456920319.64</float>
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
                        <float>1432218766.19</float>
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
