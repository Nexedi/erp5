/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80, unparam: true */
/*global window, rJS, RSVP*/
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function (param_list) {
      var gadget = this;
      return gadget.getUrlFor({command: 'history_previous'})
        .push(function (back_url) {
          return gadget.updateHeader({
            page_title: param_list[0].page_title,
            back_url: back_url,
            filter_action: true
          });
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.jio_getAttachment(options.url, options.view),
            gadget.getDeclaredGadget('form_list'),
            gadget.getDeclaredGadget('field_list')
          ]);
        })
        .push(function (result_list) {
          var listbox = result_list[0]._embedded._view.listbox,
            proxy_form_id = result_list[0]._embedded._view.proxy_form_id_list;
          listbox.command = "history_previous";
          listbox.line_icon = true;
          listbox.editable = 0;

          proxy_form_id.editable = 1;
          proxy_form_id.hidden = (proxy_form_id.items.length < 2);

          return RSVP.all([
            result_list[2].render({
              field_json: proxy_form_id,
              field_type: proxy_form_id.type,
              label: true
            }),
            result_list[1].render({
              erp5_document: {"_embedded": {"_view": {
                "listbox": listbox
              }},
                "title": result_list[0].title,
                "_links": result_list[0]._links
                },
              form_definition: {
                group_list: [[
                  "bottom",
                  [["listbox"]]
                ]]
              }
            })
          ]);
        });

    })

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_list')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })

    .allowPublicAcquisition('notifyChange', function (ignore, scope) {
      var gadget = this;
      if (scope === 'field_list') {
        return gadget.getDeclaredGadget(scope)
          .push(function (result) {
            return result.getContent();
          })
          .push(function (result) {
            return gadget.redirect({
              command: 'change',
              options: {
                view: result.proxy_form_id_list
              }
            });
          });
      }
    });

}(window, rJS, RSVP));