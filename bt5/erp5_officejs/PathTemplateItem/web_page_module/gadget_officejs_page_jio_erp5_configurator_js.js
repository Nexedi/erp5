/*global window, rJS, RSVP, URI, location,
    loopEventListener, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  function setjIOERP5Configuration(gadget) {
    var erp5_url = gadget.props.element.querySelector("input[name='erp5_url']").value;
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all([
          gadget.getSetting("portal_type"),
          gadget.getSetting("erp5_attachment_synchro", undefined),
          gadget.getSetting("default_view_reference", "jio_view")
        ]);
      })
      .push(function (result) {
        var configuration = {},
          portal_type = result[0],
          attachment_synchro = result[1] !== undefined,
          extended_attachment_url = result[1];

        configuration = {
          type: "replicate",
          // XXX This drop the signature lists...
          query: {
            query: 'portal_type:"' + portal_type + '"',
            limit: [0, 30],
            sort_on: [["modification_date", "descending"]]
          },
          use_remote_post: true,
          conflict_handling: 1,
          check_local_attachment_modification: attachment_synchro,
          check_local_attachment_creation: attachment_synchro,
          check_remote_attachment_modification: attachment_synchro,
          check_remote_attachment_creation: attachment_synchro,
          check_remote_attachment_deletion: attachment_synchro,
          check_local_modification: true,
          check_local_creation: true,
          check_local_deletion: false,
          check_remote_modification: true,
          check_remote_creation: true,
          check_remote_deletion: true,
          local_sub_storage: {
            type: "query",
            sub_storage: {
              type: "uuid",
              sub_storage: {
                type: "indexeddb",
                database: "officejs-erp5"
              }
            }
          },
          remote_sub_storage: {
            type: "mapping",
            attachment_list: ["data"],
            attachment: {
              "data": {
                "get": {
                  "uri_template": (new URI("hateoas"))
                                 .absoluteTo(erp5_url)
                                 .toString() + extended_attachment_url
                },
                "put": {
                  "erp5_put_template": (new URI("hateoas")).absoluteTo(erp5_url)
                      .toString() + "/{+id}/Base_edit"
                }
              }
            },
            sub_storage: {
              type: "erp5",
              url: (new URI("hateoas"))
                  .absoluteTo(erp5_url)
                  .toString(),
              default_view_reference: result[2]
            }
          }
        };
                // This is only for onlyoffice
        if (extended_attachment_url === "/{+id}/Document_downloadForOnlyOfficeApp") {
          configuration = {
            type: "fix_local",
            sub_storage: configuration
          };
        }
        return gadget.setSetting('jio_storage_description', configuration);
      })
      .push(function () {
        return gadget.setSetting('jio_storage_name', "ERP5");
      })
      .push(function () {
        return gadget.setSetting('storage_attachment_issue', true);
      })
      .push(function () {
        return gadget.setGlobalSetting('erp5_url', erp5_url);
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
        title: "Connect To ERP5 Storage",
        back_url: "#page=jio_configurator",
        panel_action: false
      })
        .push(function () {
          return gadget.getSetting('jio_storage_name');
        })
        .push(function (jio_storage_name) {
          if (!jio_storage_name) {
            gadget.props.element.querySelector(".document-access").setAttribute("style", "display: none;");
          }
        })
        .push(function () {
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
              return setjIOERP5Configuration(gadget);
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
          return global_setting_gadget.getSetting("erp5_url");
        })
        .push(function (erp5_url) {
          var erp5_url_input =
            gadget.props.element.querySelector("input[name='erp5_url']");
          erp5_url_input.value = erp5_url || "https://www.example.org";
          erp5_url_input.removeAttribute("disabled");
          erp5_url_input.parentNode.classList.remove('ui-state-disabled');
          erp5_url_input.focus();
        });
    });

}(window, rJS, RSVP));