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
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getSetting", "getSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("generateJsonRenderForm", function (gadget) {
      //hardcoded form_definition (this should come from erp5 form)
      var form_definition = {
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
        _links: {}
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
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('form_list'),
            gadget.generateJsonRenderForm(gadget)
          ]);
        })
        .push(function (result) {
          return result[0].render(result[1]);
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: "change", options: {"page": "ojs_add_post"}}),
            gadget.getSetting('document_title_plural'),
            gadget.getSetting('upload_dict', false)
          ]);
        })
        .push(function (result) {
          var header = {
            page_title: result[1],
            filter_action: true,
            add_url: result[0]
          };
          if (result[3]) {
            header.upload_url = result[2];
          }
          return gadget.updateHeader(header);
        });
    });
}(window, rJS, RSVP));