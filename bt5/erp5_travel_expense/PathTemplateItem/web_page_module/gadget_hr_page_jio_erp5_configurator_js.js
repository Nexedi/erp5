/*global window, rJS, RSVP, URI, location,
    loopEventListener, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  function setjIOERP5Configuration(gadget) {
    var erp5_url = gadget.props.element.querySelector("input[name='erp5_url']").value;
    return gadget.setSetting("me", '')
      .push(function () {
        var configuration = {
          type: "replicate",
          query: {
            query: '(portal_type: "Expense Record" AND (simulation_state:"draft" OR simulation_state:"sent" OR simulation_state:"stopped")) ' +
                   'OR (portal_type: "Travel Request Record" AND (simulation_state:"draft" OR simulation_state:"sent" OR simulation_state:"stopped")) ' +
                   'OR (portal_type: "Leave Report Record" AND simulation_state:"stopped") ' +
                   'OR (portal_type: "Leave Request Record" AND (simulation_state:"draft" OR simulation_state:"sent" OR simulation_state:"stopped")) ' +
                   'OR (portal_type: "Localisation Record" AND (simulation_state:"draft" OR simulation_state:"stopped")) ' +
                   'OR (portal_type: "Expense Sheet" AND (reference: "expense_sheet")) ' +
                   'OR (portal_type: "Currency" AND validation_state:"validated") ' +
                   'OR (portal_type: "Service" AND validation_state:"validated") ',
            limit: [0, 1234567890]
          },
          use_remote_post: true,
          conflict_handling: 2,
          check_local_modification: false,
          check_local_creation: true,
          check_local_deletion: false,
          check_remote_modification: false,
          check_remote_creation: true,
          check_remote_deletion: true,
          local_sub_storage: {
            type: "query",
            sub_storage: {
              type: "uuid",
              sub_storage: {
                type: "indexeddb",
                database: "officejs-erp5-hr"
              }
            }
          },
          remote_sub_storage:  {
            type: "erp5",
            url: (new URI("hateoas"))
                  .absoluteTo(erp5_url)
                  .toString(),
            default_view_reference: "jio_view"
          },
          signature_sub_storage: {
            type: "query",
            sub_storage: {
              type: "indexeddb",
              database: "expense-hash-list"
            }
          }
        };
        return gadget.setSetting('jio_storage_description', configuration);
      })
      .push(function () {
        return gadget.setSetting('jio_storage_name', "ERP5");
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
          return gadget.declareGadget(
            'gadget_officejs_setting.html',
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
          erp5_url_input.value = erp5_url || "https://nexedijs.erp5.net";
          erp5_url_input.removeAttribute("disabled");
          erp5_url_input.parentNode.classList.remove('ui-state-disabled');
          erp5_url_input.focus();
        });
    });

}(window, rJS, RSVP));