/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS) {
  "use strict";

  rJS(window)
    .setState({
      erp5_url_list: "https://panel.rapid.space/hateoas/"
    })
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("setSetting", "setSetting")

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this, i,
        master_url_list;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          master_url_list = content.erp5_url_list.split(/\r?\n|\r|\n/g);
          for (i = 0; i < master_url_list.length; i += 1) {
            master_url_list[i] = master_url_list[i].trim();
          }
          return gadget.redirect({command: "display", options: {
            page: "ojsm_import_export",
            auto_sync: "erp5",
            url_list: master_url_list
          }});
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function () {
      var gadget = this;

      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          //TODO replace textarea by N stringfield inputs
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_erp5_url_list": {
                  "description": "",
                  "title": "Connection Url List",
                  "default": gadget.state.erp5_url_list,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "erp5_url_list",
                  "hidden": 0,
                  "type": "TextAreaField"
                }
              }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "top",
                [["my_erp5_url_list"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.getUrlFor({command: 'display', options: {page: 'ojsm_import_export'}});
        })
        .push(function (url) {
          return gadget.updateHeader({
            page_title: "Connect To ERP5 Storage",
            back_url: url,
            submit_action: true,
            panel_action: false
          });
        });
    });
}(window, rJS));
