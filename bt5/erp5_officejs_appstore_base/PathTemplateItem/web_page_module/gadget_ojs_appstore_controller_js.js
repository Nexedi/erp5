/*global document, window, rJS, RSVP, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS, RSVP, jIO) {
  "use strict";

  function setSelectionUrl(gadget, options) {
    return gadget.getSetting('hateoas_url')
      .push(function (url) {
        return jIO.util.ajax({
          type: 'GET',
          url: url + gadget.state.options.jio_key +
          '/SoftwarePublication_getRelatedSoftwareProduct'
        });
      })
      .push(function (result) {
        return gadget.getUrlFor({command: 'display', options: {jio_key: result.target.response}});
      })
      .push(function (url) {
        options.selection_url = url;
      });
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    /////////////////////////////////////////////////////////////////
    // Overload Public Acquisition methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function (param_list) {
      var gadget = this, options = param_list[0];
      return gadget.getUrlFor({
        command: 'display',
        options: {
          page: 'front_ojs_appstore'
        }
      })
        .push(function (url) {
          if (gadget.state.is_software_product && options.selection_url) {
            options.selection_url = url;
          }
          if (options.cancel_url &&
              gadget.state.options.jio_key === 'software_product_module') {
            options.cancel_url = url;
          }
          delete options.actions_url;
          delete options.next_url;
          delete options.previous_url;
          delete options.tab_url;
          delete options.export_url;
          if (gadget.state.is_software_product && options.add_url) {
            return gadget.getUrlFor({
              command: 'display_erp5_action',
              options: {
                page: 'update_application',
                jio_key: gadget.state.options.jio_key
              }
            })
              .push(function (url) {
                options.add_url = url;
              });
          } else {
            delete options.add_url;
          }
          if (options.selection_url &&
              gadget.state.options.jio_key.indexOf('software_publication_module/') !== -1) {
            return setSelectionUrl(gadget, options);
          }
        })
        .push(function () {
          return gadget.updateHeader(options);
        });
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })

    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (g) {
          return g.triggerSubmit();
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      options.editable = true;
      return gadget.changeState({
        child_gadget_url: 'gadget_erp5_page_form.html',
        options: options,
        is_software_product:
          options.jio_key.indexOf('software_product_module/') === 0
      });
    })
    .onStateChange(function (modification_dict) {
      var fragment = document.createElement('div'),
        gadget = this;
      return new RSVP.Queue()
        .push(function () {
          if (!modification_dict.hasOwnProperty('child_gadget_url')) {
            return gadget.getDeclaredGadget('fg')
              .push(function (child_gadget) {
                return child_gadget.render(gadget.state.options);
              });
          }
          // Clear first to DOM, append after to reduce flickering/manip
          while (gadget.element.firstChild) {
            gadget.element.removeChild(gadget.element.firstChild);
          }
          gadget.element.appendChild(fragment);

          return gadget.declareGadget(gadget.state.child_gadget_url, {element: fragment,
                                                                      scope: 'fg'})
            .push(function (form_gadget) {
              return form_gadget.render(gadget.state.options);
            });
        });
    });

}(document, window, rJS, RSVP, jIO));