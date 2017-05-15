/*global window, rJS, RSVP, URI, location,
    loopEventListener, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  function setjIODAVConfiguration(gadget) {
    var dav_url = gadget.props.element.querySelector("input[name='dav_url']").value;
    return gadget.getSetting("portal_type")
      .push(function (portal_type) {
        var old_date = new Date(),
          configuration = {};
        // We are looking for documents modified in the past 3 month
        old_date = new Date(old_date.getFullYear(), old_date.getMonth() - 3);
        configuration = {
          type: "replicate",
          // XXX This drop the signature lists...
          query: {
            query: 'portal_type:"' + portal_type + '" ',
            // XX Synchonizing the whole module is too much, here is a way to start quietly
            //+ 'AND local_roles: ("Owner") '
            //+ 'AND validation_state: ("draft", "released_alive", "shared_alive", "published_alive") ',
            limit: [0, 1234567890]
          },
          use_remote_post: false,
          conflict_handling: 2,
          check_local_modification: true,
          check_local_creation: true,
          check_local_deletion: true,
          check_remote_modification: true,
          check_remote_creation: true,
          check_remote_deletion: true,
          local_sub_storage: {
            type: "mapping",
            attachment: {
              'data': {
                get: {uri_template: 'enclosure'},
                put: {uri_template: 'enclosure'}
              }
            },
            sub_storage: {
              type: "query",
              sub_storage: {
                type: "uuid",
                sub_storage: {
                  type: "indexeddb",
                  database: "officejs-dav"
                }
              }
            }
          },
          remote_sub_storage: {
            type: "mapping",
            attachment: {
              'data': {
                get: {uri_template: 'enclosure'},
                put: {uri_template: 'enclosure'}
              }
            },
            sub_storage: {
              type: "query",
              sub_storage: {
                type: "drivetojiomapping",
                sub_storage: {
                  type: "mapping",
                  property: {
                    "portal_type": [
                      "switchPropertyValue",
                      {"PDF":"pdf", "Web Page": "txt"}
                    ]
                  },
                  sub_storage: {
                    type: "dav",
                    url: gadget.props.element.querySelector("input[name='dav_url']").value,
                    basic_login: btoa(gadget.props.element.querySelector("input[name='dav_username']").value
                      + ':' + gadget.props.element.querySelector("input[name='dav_password']").value),
                    with_credentials: true
                  }
                }
              }
            }
          }
        };
        return gadget.setSetting('jio_storage_description', configuration);
      })
      .push(function () {
        return gadget.setSetting('jio_storage_name', "DAV");
      })
      .push(function () {
        return gadget.setGlobalSetting('dav_url', dav_url);
      })
      .push(function () {
        return gadget.setSetting('sync_reload', true);
      })
      .push(function () {
        return gadget.redirect({page: 'sync', auto_repair: 'true'});
      });
  }

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
          return g.getSetting('jio_storage_name');
        })
        .push(function (jio_storage_name) {
          if (jio_storage_name === "DAV") {
            return g.getSetting('jio_storage_description')
              .push(function (jio_storage_description) {
                g.props.element.querySelector("input[name='dav_url']").value =
                  jio_storage_description.remote_sub_storage.sub_storage.sub_storage.url;
              });
          }
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("reload", "reload")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareMethod("getGlobalSetting", function (key) {
      var gadget = this;
      return gadget.getDeclaredGadget("global_setting_gadget")
        .push(function (global_setting_gadget) {
          return global_setting_gadget.getSetting(key);
        });
    })
    .declareMethod("setGlobalSetting", function (key, value) {
      var gadget = this;
      return gadget.getDeclaredGadget("global_setting_gadget")
        .push(function (global_setting_gadget) {
          return global_setting_gadget.setSetting(key, value);
        });
    })
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({
        title: "Connect To DAV Storage",
        back_url: "#page=jio_configurator",
        panel_action: false
      }).push(function () {
        return gadget.props.deferred.resolve();
      });
    })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('form'),
            'submit',
            true,
            function () {
              return setjIODAVConfiguration(gadget);
            }
          );
        });
    })

    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return gadget.getSetting("global_setting_gadget_url");
        })
        .push(function (global_setting_gadget_url) {
          return gadget.declareGadget(
            global_setting_gadget_url,
            {
              scope: "global_setting_gadget",
              sandbox: "iframe",
              element: gadget.props.element.querySelector(".global_setting_gadget")
            }
          );
        })
        .push(function (global_setting_gadget) {
          return global_setting_gadget.getSetting("dav_url");
        })
        .push(function (dav_url) {
          var erp5_url_input =
            gadget.props.element.querySelector("input[name='dav_url']");
          erp5_url_input.value = dav_url || "https://www.example.com";
          erp5_url_input.removeAttribute("disabled");
          erp5_url_input.parentNode.classList.remove('ui-state-disabled');
          erp5_url_input.focus();
        });
    });

}(window, rJS, RSVP));