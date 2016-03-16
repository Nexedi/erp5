/*global window, rJS, RSVP, URI, location,
    loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  function setERP5Configuration(gadget) {
    var old_date = new Date(),
      configuration = {};
    // We are looking for documents modified in the past 3 month
    old_date = new Date(old_date.getFullYear(), old_date.getMonth() - 3);
    configuration = {
      type: "replicate",
      // XXX This drop the signature lists...
      query: {
        query: 'portal_type:"Web Page" '
        // XX Synchonizing the whole module is too much, here is a way to start quietly
        // Supsended until modification_date is handled for synchronization
          + ' AND modification_date:>="'
          + old_date.toISOString() + '" ',
        limit: [0, 1234567890]
      },
      use_remote_post: true,
      conflict_handling: 1,
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
        type: "erp5",
        url: (new URI("hateoas"))
          .absoluteTo(location.href)
          .toString(),
        default_view_reference: "jio_view"
      }
    };
    return gadget.setSetting('jio_storage_description', configuration)
      .push(function () {
        return gadget.setSetting('jio_storage_name', "ERP5");
      })
      .push(function () {
        return gadget.reload();
      });
  }

  function setLocalConfiguration(gadget) {
    var configuration = {
      type: "query",
      sub_storage: {
        type: "uuid",
        sub_storage: {
          type: "indexeddb",
          database: "officejs"
        }
      }
    };
    return gadget.setSetting('jio_storage_description', configuration)
      .push(function () {
        return gadget.reload();
      });
  }

  function setDAVConfiguration(gadget) {
    return gadget.redirect({page: 'jio_dav_configurator'});
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
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("reload", "reload")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({
        title: "Storage Configuration"
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
          return RSVP.all([
            loopEventListener(
              gadget.props.element.querySelector('form.select-erp5-form'),
              'submit',
              true,
              function () {
                return setERP5Configuration(gadget);
              }
            ),
            loopEventListener(
              gadget.props.element.querySelector('form.select-local-form'),
              'submit',
              true,
              function () {
                return setLocalConfiguration(gadget);
              }
            ),
            loopEventListener(
              gadget.props.element.querySelector('form.select-dav-form'),
              'submit',
              true,
              function () {
                return setDAVConfiguration(gadget);
              }
            )
          ]);
        });
    });


}(window, rJS, RSVP));