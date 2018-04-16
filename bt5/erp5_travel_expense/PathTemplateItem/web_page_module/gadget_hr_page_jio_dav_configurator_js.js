/*global window, rJS, RSVP, URI, location,
    loopEventListener, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  function setjIODAVConfiguration(gadget) {
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
             query: '(portal_type: "Expense Record" AND (simulation_state:"draft" OR simulation_state:"sent" OR simulation_state:"stopped")) ' +
                          'OR (portal_type: "Travel Request Record" AND (simulation_state:"draft" OR simulation_state:"sent" OR simulation_state:"stopped")) ' +
                          'OR (portal_type: "Leave Report Record" AND simulation_state:"stopped") ' +
                          'OR (portal_type: "Leave Request Record" AND (simulation_state:"draft" OR simulation_state:"sent" OR simulation_state:"stopped")) ' +
                          'OR (portal_type: "Localisation Record" AND (simulation_state:"draft" OR simulation_state:"stopped")) ' +
                          'OR (portal_type: "Expense Sheet" AND (reference: "expense_sheet")) ' +
                          'OR (portal_type: "Currency" AND validation_state:"validated") ' +
                          'OR (portal_type: "Service" AND validation_state:"validated") ',
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
            type: "query",
            sub_storage: {
              type: "uuid",
              sub_storage: {
                type: "indexeddb",
                database: "officejs-dav"
              }
            }
          },
          remote_sub_storage: {
            type: "query",
            sub_storage: {
              type: "drivetojiomapping",
              sub_storage: {
                type: "dav",
                url: gadget.props.element.querySelector("input[name='dav_url']").value,
                basic_login: btoa(gadget.props.element.querySelector("input[name='dav_username']").value
                  + ':' + gadget.props.element.querySelector("input[name='dav_password']").value),
                with_credentials: true
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
    });


}(window, rJS, RSVP));