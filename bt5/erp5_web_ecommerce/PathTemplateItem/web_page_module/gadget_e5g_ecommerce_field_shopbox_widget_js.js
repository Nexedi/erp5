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
            <value> <string>gadget_e5g_ecommerce_field_shopbox_widget.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_e5g_ecommerce_field_shopbox_widget_js</string> </value>
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

/*global window, rJS, RSVP, Handlebars */\n
/*jslint nomen: true, indent: 2 */\n
(function (window, rJS, RSVP, Handlebars) {\n
  "use strict";\n
\n
  // XXX quick hack!\n
\n
  /////////////////////////////////////////////////////////////////\n
  // api handlebars\n
  /////////////////////////////////////////////////////////////////\n
\n
  // shopbbox_widget_header = {\n
  //   item_list: [\n
  //     item_link: [string],\n
  //     item_default_src: [string],\n
  //     item_title: [string],\n
  //     item_description: [string],\n
  //     item_price: [string]\n
  //   ]\n
  // }\n
  // shopbox_widget_search = {}\n
  // shopbox_widget_paginate = {}\n
\n
  /////////////////////////////////////////////////////////////////\n
  // templates\n
  /////////////////////////////////////////////////////////////////\n
  var gadget_klass = rJS(window),\n
    templater = gadget_klass.__template_element,\n
\n
    shopbox_widget_list = Handlebars.compile(\n
      templater.getElementById("shopbox-widget-list").innerHTML\n
    );\n
\n
  /////////////////////////////////////////////////////////////////\n
  // some methods\n
  /////////////////////////////////////////////////////////////////\n
  function digForProperty(my_property, my_document_list) {\n
    var list = my_document_list || [],\n
      property,\n
      j_len,\n
      j;\n
\n
    for (j = 0, j_len = list.length; j < j_len; j += 1) {\n
      property = list[j][my_property];\n
      if (property) {\n
        return property;\n
      }\n
    }\n
  }\n
\n
  gadget_klass\n
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
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")\n
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")\n
    .declareAcquiredMethod("whoWantToDisplayThis", "whoWantToDisplayThis")\n
    .declareAcquiredMethod("translateHtml", "translateHtml")\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared methods\n
    /////////////////////////////////////////////////////////////////\n
    .declareMethod(\'render\', function (my_option_dict) {\n
      var gadget = this,\n
        element = gadget.property_dict.element,\n
        container = element.querySelector(".custom-grid .ui-body-c"),\n
        content = \'\',\n
        search_gadget,\n
        result,\n
        sub_document_list;\n
\n
      // store initial configuration and query\n
      gadget.property_dict.initial_query\n
        = gadget.property_dict.initial_query || my_option_dict.gadget_query;\n
      gadget.property_dict.option_dict =\n
        gadget.property_dict.option_dict || my_option_dict;\n
\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return gadget.declareGadget("gadget_erp5_searchfield.html", {\n
            "scope": "shopbox-search"\n
          });\n
        })\n
        .push(function (my_search_gadget) {\n
          return my_search_gadget.render({});\n
        })\n
        .push(function (my_rendered_gadget) {\n
          search_gadget = my_rendered_gadget;\n
          return gadget.jio_allDocs(my_option_dict.gadget_query);\n
        })\n
        .push(function (my_result) {\n
          var subdocument_list = [],\n
            item,\n
            i_len,\n
            i;\n
\n
          result = my_result;\n
\n
          for (i = 0, i_len = result.data.total_rows; i < i_len; i += 1) {\n
            item = result.data.rows[i];\n
            subdocument_list.push(gadget.jio_getAttachment({\n
              "_id": "erp5",\n
              "_attachment": window.location.href + "hateoas/" +\n
                item.id + "/shopbox_getRelatedDocumentList"\n
            }));\n
          }\n
          return RSVP.all(subdocument_list);\n
        })\n
        .push(function (my_related_document_list) {\n
          var link_list = [],\n
            image_dict = {},\n
            image_url,\n
            item,\n
            sub_document,\n
            i_len,\n
            i;\n
\n
          sub_document_list = my_related_document_list;\n
\n
          for (i = 0, i_len = result.data.total_rows; i < i_len; i += 1) {\n
            item = result.data.rows[i];\n
            sub_document = sub_document_list[i].data.related_document_list;\n
            link_list.push(gadget.whoWantToDisplayThis(item.id));\n
\n
            // XXX:\n
            image_url = digForProperty("default_image_url", sub_document);\n
            if (image_url) {\n
              image_dict[item.id] = window.location.protocol + "//" +\n
                window.location.host + "/" +\n
                  image_url + "?quality=75&display=thumbnail";\n
            }\n
          }\n
\n
          return RSVP.all([\n
            RSVP.all(link_list),\n
            RSVP.hash(image_dict)\n
          ]);\n
        })\n
        .push(function (my_link_list) {\n
          var data = result.data.rows,\n
            href_list = my_link_list[0],\n
            src_dict = my_link_list[1],\n
            item_list = [],\n
            item,\n
            price,\n
            sub_document,\n
            price_formatted,\n
            i_len,\n
            i;\n
\n
          for (i = 0, i_len = href_list.length; i < i_len; i += 1) {\n
            item = data[i];\n
            sub_document = sub_document_list[i].data.related_document_list;\n
            price = digForProperty("price", sub_document);\n
            if (price) {\n
              price_formatted = price.toFixed(2);\n
            }\n
            item_list.push({\n
              item_link: href_list[i],\n
              item_default_src: src_dict[item.id],\n
              item_title: item.value.title,\n
              item_description: item.value.description,\n
              item_price: price_formatted + " \\u20AC"\n
            });\n
          }\n
\n
          content += shopbox_widget_list({"item_list": item_list});\n
          return gadget.translateHtml(content);\n
        })\n
        .push(function (my_translated_html) {\n
          var wrapper,\n
            first_element;\n
\n
          container.innerHTML = my_translated_html;\n
          wrapper = container.querySelector(".ui-shopbox-wrapper");\n
          first_element = wrapper.firstChild;\n
          wrapper.insertBefore(search_gadget.__element, first_element);\n
\n
          return gadget;\n
        });\n
    });\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared service\n
    /////////////////////////////////////////////////////////////////\n
\n
}(window, rJS, RSVP, Handlebars));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Gadget E5G Ecommerce Field Shopbox Widget JS</string> </value>
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
                <value> <string>sven</string> </value>
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
                        <float>1431520190.33</float>
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
                <value> <string>943.10624.40607.24285</string> </value>
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
                        <float>1432198612.22</float>
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
                <value> <string>sven</string> </value>
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
                        <float>1431520152.3</float>
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
