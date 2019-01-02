/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          return gadget.setSetting('car', content.car);
        })
        .push(function () {
          return RSVP.all([
            gadget.notifySubmitted('Data Updated')
          ]);
        })
        .push(function () {
          // Workaround, find a way to open document without break gadget.
          return gadget.redirect({"command": "change", "options": {"page": "drive_app_add_document"}});
        });
    })
    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function () {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('form_view'),
            gadget.getSetting('car'),
          ]);
        })
        .push(function (result) {
          var item_list = [["Car1", "1#Car1"], ["Car2", "2#Car2"], ["Car3", "3#Car3"]];
          return result[0].render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_car": {
                  "description": "",
                  "title": "Car",
                  "default": result[1] || "",
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "car",
                  "hidden": 0,
                  "items": [["", ""]].concat(item_list),
                  "type": "ListField"
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
                "left",
                [["my_car"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.getSetting('document_title');
        })
        .push(function (document_title) {
          return gadget.updateHeader({
            page_title: document_title,
            save_action: true
          });
        });
    });
}(window, rJS, RSVP));