/*global window, rJS, RSVP, loopEventListener */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, loopEventListener) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .allowPublicAcquisition("getListboxInfo", function () {
      return this.getDeclaredGadget("erp5_form")
        .push(function(form_gadget) {
          return form_gadget.getListboxInfo();
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var gadget = this,
        form_options = options.erp5_form || {},
        search_options = {};

      form_options.erp5_document = options.erp5_document;
      form_options.form_definition = options.form_definition;
      form_options.view = options.view;

      return new RSVP.Queue()
        .push(function () {
          return gadget.getUrlParameter('extended_search');
        })
        .push(function (extended_search) {
          // XXX not generic, fix later
          if (extended_search) {
            form_options.form_definition.extended_search = extended_search;
            search_options.extended_search = extended_search;
          }
          // XXX Hardcoded for listbox's hide functionality
          form_options.form_definition.hide_enabled = true;
          var new_content_action = options.erp5_document._links.action_object_new_content_action;
          if (new_content_action !== undefined) {
            new_content_action = gadget.getUrlFor({command: 'change', options: {view: new_content_action.href, editable: true}});
          } else {
            new_content_action = "";
          }

          return RSVP.all([
            gadget.getDeclaredGadget("erp5_searchfield"),
            gadget.getDeclaredGadget("erp5_form"),
            new_content_action,
            gadget.getUrlFor({command: 'change', options: {page: "action"}}),
            gadget.getUrlFor({command: 'display', options: {}})
          ]);
        })
        .push(function (all_gadget) {
          return RSVP.all([
            all_gadget[0].render(search_options),
            all_gadget[1].render(form_options),
            gadget.updateHeader({
              panel_action: true,
              jump_url: "",
              cut_url: "",
              add_url: all_gadget[2],
              actions_url: all_gadget[3],
              export_url: "",
              page_title: options.erp5_document.title,
              front_url: all_gadget[4]
            })

          ]);
        });

    })

    .declareService(function () {
      var gadget = this;

      function formSubmit() {
        return gadget.getDeclaredGadget("erp5_searchfield")
          .push(function (search_gadget) {
            return search_gadget.getContent();
          })
          .push(function (data) {
            var options = {
              begin_from: undefined,
              // XXX Hardcoded
              field_listbox_begin_from: undefined
            };
            if (data.search) {
              options.extended_search = data.search;
            } else {
              options.extended_search = undefined;
            }
            return gadget.redirect({command: 'store_and_change', options: options});
          });
      }
      // Listen to form submit
      return loopEventListener(
        gadget.props.element.querySelector('form'),
        'submit',
        false,
        formSubmit
      );
    });

}(window, rJS, RSVP, loopEventListener));