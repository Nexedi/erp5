 /*global window, document, rJS, RSVP, URI, location, Handlebars
    loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("storage-selection")
                         .innerHTML,
    storage_selection = Handlebars.compile(source),
    storage_list = {
    "erp5": {
      "setConfiguration": function (gadget) {
        return gadget.redirect({command: "display", options: {page: 'ojs_erp5_configurator'}});
      },
      "name": "Erp5"
    },
    "local": {
      "setConfiguration": function (gadget) {
        var configuration = {
          type: "query",
          sub_storage: {
            type: "uuid",
            sub_storage: {
              type: "indexeddb",
              database: "local_default"
            }
          }
        };
        return gadget.setSettingList({'jio_storage_description': configuration,
                                      'jio_storage_name': 'LOCAL',
                                      'sync_reload': true})
          .push(function () {
            return gadget.redirect({command: "display", options: {page: 'ojs_sync', auto_repair: 'true'}});
          });
      },
      "name": "Local is Enough"
    },
    "dav": {
      "setConfiguration": function (gadget) {
        return gadget.redirect({command: "display", options: {page: 'ojs_dav_configurator'}});
      },
      "name": "Dav Storage"
    },
    "dropbox": {
      "setConfiguration": function (gadget) {
        return new RSVP.Queue()
          .push(function () {
            return gadget.getSetting('dropbox_app_key');
          })
          .push(function (app_key) {
            window.location = 'https://www.dropbox.com/1/oauth2/authorize?client_id=' +
                              encodeURIComponent(app_key) +
                              '&response_type=token&redirect_uri=' +
                              encodeURIComponent(window.location.origin);
          });
      },
      "name": "Dropbox"
    },
    "linshare": {
      "name": "Linshare",
      "setConfiguration": function (gadget) {
        return gadget.redirect({command: "change", options: {page: 'ojs_linshare_configurator'}});
      }
    }
  };

  function getUrlParameter(gadget, name) {
    return gadget.getUrlFor({command: "display", options: {page: "ojs_configurator", type: name}})
      .push(function (url) {
        return {
          "link": url,
          "title": storage_list[name].name
        };
      });
  }

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
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSettingList", "setSettingList")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.updateHeader({page_title: "Storage Configuration"})
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget("access"),
            gadget.getSetting("jio_storage_name", "")
          ]);
        })
        .push(function (result) {
          return result[0].render(result[1]);
        })
        .push(function () {
          return gadget.changeState({
            type: options.type || "",
            url: options.url
          });
        });
    })
    .onStateChange(function () {
      var gadget = this;
      if (storage_list.hasOwnProperty(gadget.state.type)) {
        return storage_list[gadget.state.type].setConfiguration(gadget);
      }
      return new RSVP.Queue()
        .push(function () {
          var promise_list = [], name;
          for (name in storage_list) {
            if (storage_list.hasOwnProperty(name)) {
              promise_list.push(getUrlParameter(gadget, name));
            }
          }
          return RSVP.all(promise_list);
        })
        .push(function (result) {
          gadget.element.querySelector('.storage-selection').innerHTML = storage_selection({
            documentlist: result
          });
        });
    });


}(window, rJS, RSVP, Handlebars));
