/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, RSVP, rJS, jIO, document) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    .allowPublicAcquisition("getPromiseDocument", function (param_list) {
      var gadget = this,
        source = param_list[0],
        url_suffix = param_list[1];

      return gadget.jio_allDocs({
        // select_list: [],
        query: 'portal_type:promise AND source:"' + source + '" AND channel:' +
          gadget.state.instance.specialise_title
      })
        .push(function (result) {
          if (result.data.rows.length !== 1) {
            throw new Error('Unexpected number of promise ' +
                            result.data.rows.length);
          }
          return gadget.jio_get(result.data.rows[0].id);
        })
        .push(function (result) {
          return jIO.util.ajax({
            type: "GET",
            url: result.link + url_suffix,
            dataType: "text",
            headers: {
              authorization: "Basic " + gadget.state.basic_login
            },
            xhrFields: {
              withCredentials: false
            }
          });
        })
        .push(function (evt) {
          return evt.target.responseText;
        });
    })

    .onEvent('submit', function () {
      // ON submit, refresh page
      return this.redirect({command: 'reload'});
    })
    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareJob("loadCustomGadget", function () {
      var gadget = this,
          container;

      container = gadget.element.querySelector('.container');
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.declareGadget(
            //gadget.state.gadget_url,
            "https://softinst141426.host.vifib.net/share/public/html/software.cfg.html",
            {
              element: container,
              scope: "custom_gadget",
              sandbox: "iframe"
            });
        })
        .push(function (custom_gadget) {
          return new RSVP.Queue()
            .push(function () {
              return custom_gadget.render({
                //channel: gadget.state.instance_tree.title,
                //url: gadget.state.opml.url,
                //username: gadget.state.opml.username,
                //password: gadget.state.opml.password,
                //basic_login: gadget.state.opml.basic_login
              })
              .push(function () {
                return gadget.notifySubmitted({
                  message: "Gadget loaded.",
                  status: "success"
                });
              });
            })
            .push(undefined, function (error) {
              // render does not exist or failed
              console.error(error);
              return gadget.notifySubmitted({
                message: "Failed to render the gadget!",
                status: "error"
              });
            });
        }, function (error) {
          // Failed to load the gadget. Probably not found!
          console.error(error);
          return gadget.notifySubmitted({
            message: "Could not load gadget!",
            status: "error"
          });
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.jio_get(options.key)
        .push(function (instance_doc) {
          return gadget.changeState({instance: instance_doc});
        })
        .push(function () {
          return gadget.jio_get(options.opml_url);
        }).push(function (opml) {
          return gadget.changeState({
            basic_login: opml.basic_login,
            gadget_url: gadget.state.instance.software_release + ".html"
          });
        })
        .push(function () {
          return gadget.getUrlFor({command: 'history_previous'});
        })
        .push(function (previous_url) {
          var options = {
              page_title: "Software Instance: " + gadget.state.instance.title,
              selection_url: previous_url,
              refresh_action: true
            };
          return gadget.updateHeader(options);
        });

    })
    .onStateChange(function (modification_dict) {
      var gadget = this;

      if (!modification_dict.hasOwnProperty('gadget_url')) {
        return;
      }
      return gadget.loadCustomGadget();
    });
}(window, RSVP, rJS, jIO, document));
