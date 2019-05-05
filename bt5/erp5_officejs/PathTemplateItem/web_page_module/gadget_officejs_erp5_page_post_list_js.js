/*global window, document, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP) {
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

    //HARDCODED UNTIL form_def is stored in local storage
    .declareMethod("getFormDefinition", function (gadget) {
      var fake_thread_uid = "thread-" + ("0000" + ((Math.random() * Math.pow(36, 4)) | 0).toString(36)).slice(-4),
        action_info = {
          page: "handle_action",
          action: "new",
          portal_type: "HTML Post",
          parent_portal_type: "Post Module",
          my_source_reference: fake_thread_uid
        },
        form_definition = {
          _debug: "traverse",
          pt: "form_view",
          title: "Post",
          group_list: [[
            "bottom",
            [["my_listbox"]]
          ]],
          //this fields_raw_properties is totally made up, but somewhere in the definition there must be
          //information about the fields. So, foreach field: key->info
          fields_raw_properties: {
            "my_listbox": {
              "type": "ListBox",
              "key": "field_listbox", // or my_listbox ??
              "values": {
                "column_list": [['title', 'Title'], ['modification_date', 'Modification Date']],
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "lines": 30,
                "list_method": "portal_catalog",
                // is this correct? the query should come from the form definition, right?
                "query": "urn:jio:allDocs?query=portal_type%3A%22HTML Post%22",
                "portal_type": [],
                "search_column_list": [['title', 'Title'], ['modification_date', 'Modification Date']],
                "sort_column_list": [['title', 'Title'], ['modification_date', 'Modification Date']],
                "sort": [['modification_date', 'descending']],
                "title": "Posts"
              },
              "tales": {},
              "overrides": {},
              "message_values": {}
            }
          },
          action: "Base_edit",
          update_action: "",
          _links: { "type": { name: "" }, "action_object_new_content_action": action_info }
        };
      return form_definition;
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        default_view = "jio_view",
        common_utils_gadget_url = "gadget_officejs_common_utils.html",
        child_gadget_url = 'gadget_erp5_pt_form_list.html';
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('parent_portal_type'),
            gadget.declareGadget("gadget_officejs_common_utils.html")
          ]);
        })
        .push(function (result) {
            return gadget.getFormDefinition();
            //return result[1].getFormDefinition(result[0], default_view);
          })
          .push(function (form_definition) {
            return gadget.changeState({
              jio_key: options.jio_key,
              child_gadget_url: child_gadget_url,
              form_definition: form_definition,
              form_type: 'list',
              editable: false,
              view: default_view,
              front_page: true,
              has_more_views: false, //this should come from form_def
              has_more_actions: false //this should come from form_def
            });
          });
    })

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this,
        options;
      while (this.element.firstChild) {
        this.element.removeChild(this.element.firstChild);
      }
      this.element.appendChild(fragment);
      return gadget.declareGadget("gadget_officejs_form_view.html", {element: fragment,
                                                                     scope: 'form_view'})
        .push(function (form_view_gadget) {
          return form_view_gadget.render(gadget.state);
        });
    })

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_view')
        .push(function (view_gadget) {
          return view_gadget.getDeclaredGadget('fg');
        })
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    });

}(window, document, rJS, RSVP));