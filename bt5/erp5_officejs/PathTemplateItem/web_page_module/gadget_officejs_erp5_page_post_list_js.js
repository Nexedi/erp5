/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("isDesktopMedia", "isDesktopMedia")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getSetting", "getSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("generateJsonRenderForm", function (gadget) {
      //this will be the id of the thread that contains this post list
      var fake_thread_uid = "thread-" + ("0000" + ((Math.random() * Math.pow(36, 4)) | 0).toString(36)).slice(-4),
        // get these (portal_type, etc) from getSettings
        action_info = {
          page: "handle_action",
          action: "new",
          action_type: "object_jio_js_script",
          portal_type: "HTML Post",
          parent_portal_type: "Post Module",
          my_source_reference: fake_thread_uid
        },
        //hardcoded form_definition (this should come from erp5 form)
        form_definition = {
          _debug: "traverse",
          pt: "form_view",
          title: "Post",
          group_list: [[
            "bottom",
            [["my_listbox"]]
          ]],
          //this field_info is totally made up, but somewhere in the definition there must be
          //information about the fields. So, foreach field: key->info
          field_info_dict: {
            "my_listbox": {
              "column_list": [['title', 'Title'], ['modification_date', 'Modification Date']],
              "show_anchor": 0,
              "default_params": {},
              "editable": 1,
              "editable_column_list": [],
              "key": "field_listbox",
              "lines": 30,
              "list_method": "portal_catalog",
              // is this correct? the query should come from the form definition, right?
              "query": "urn:jio:allDocs?query=portal_type%3A%22HTML Post%22",
              "portal_type": [],
              "search_column_list": [['title', 'Title'], ['modification_date', 'Modification Date']],
              "sort_column_list": [['title', 'Title'], ['modification_date', 'Modification Date']],
              "sort": [['modification_date', 'descending']],
              "title": "Posts",
              "type": "ListBox"
            }
          },
          action: "Base_edit",
          update_action: "",
          _links: { "type": { name: "" }, "action_object_new_content_action": action_info }
        },
        form_json = {
          erp5_document: {
            "_embedded": {"_view": {}},
            "_links": {}
          },
          form_definition: form_definition
        };
      for (var i = 0; i < form_definition.group_list.length; i++) {
        var fields = form_definition.group_list[i][1];
        for (var j = 0; j < fields.length; j++) {
          var my_element = fields[j][0], element_id;
          if (my_element.startsWith("my_")) {
            element_id = my_element.replace("my_", "");
          }
          var field_info = form_definition.field_info_dict[my_element];
          if (gadget.state.hasOwnProperty("doc") && gadget.state.doc.hasOwnProperty(element_id)) {
            field_info["default"] = gadget.state.doc[element_id];
          }
          form_json.erp5_document._embedded._view[my_element] = field_info;
          form_json.erp5_document._links = form_definition._links;
        }
      }
      return form_json;
    })

    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_list')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })

    .declareMethod("render", function () {
      var gadget = this,
          erp5_document;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('form_list'),
            gadget.generateJsonRenderForm(gadget)
          ]);
        })
        .push(function (result) {
          erp5_document = result[1].erp5_document;
          return result[0].render(result[1]);
        })
        // render the header
        .push(function () {
          var url_for_parameter_list = [
            {command: 'change', options: {page: "tab"}},
            {command: 'change', options: {page: "action"}},
            {command: 'history_previous'},
            {command: 'selection_previous'},
            {command: 'selection_next'},
            {command: 'change', options: {page: "export"}},
            {command: 'display', options: {}}
          ];
          if (erp5_document._links && erp5_document._links.action_object_new_content_action) {
            url_for_parameter_list.push({command: 'change', options: erp5_document._links.action_object_new_content_action});
          }
          return RSVP.all([
            gadget.getUrlForList(url_for_parameter_list),
            gadget.isDesktopMedia(),
            gadget.getSetting('document_title_plural'),
            gadget.getSetting('upload_dict', false)
          ]);
        })
        .push(function (result_list) {
          var is_form_list = true, //TODO: configuration must indicate if is a form or list view
            url_list = result_list[0], header_dict;
          if (is_form_list) {
            header_dict = {
              panel_action: true,
              jump_url: "",
              fast_input_url: "",
              filter_action: true,
              page_title: result_list[2]
            };
            if (result_list[4]) {
              header_dict.upload_url = result_list[3];
            }
          } else {
            header_dict = {
              selection_url: url_list[2],
              previous_url: url_list[3],
              next_url: url_list[4],
              page_title: gadget.state.doc.title
            };
            if (false) { //TODO: configuration must indicate if there are more views
              header_dict.tab_url = url_list[0];
            }
            if (gadget.state.editable === "true") {
              header_dict.save_action = true;
            }
          }
          if (false) { //TODO: configuration must indicate if there are more actions
            header_dict.actions_url = url_list[1];
          }
          if (url_list[7]) {
            header_dict.add_url = url_list[7];
          }
          if (result_list[1]) {
            header_dict.export_url = (
              erp5_document._links.action_object_jio_report ||
              erp5_document._links.action_object_jio_exchange ||
              erp5_document._links.action_object_jio_print
            ) ? url_list[5] : '';
          }
          return gadget.updateHeader(header_dict);
        });
    });
}(window, rJS, RSVP));