/*globals window, document, RSVP, rJS, promiseEventListener*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
(function (window, document, RSVP, rJS, promiseEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////

  function initializeSetting(gadget) {
      return gadget.declareGadget(
        gadget.props.full_url  + "gadget_jio.html",
        {
          scope: "application_storage",
          element: gadget.props.element.querySelector("div"),
          sandbox: "iframe"
        }
      ) 
        .push(function (jio_gadget) {
          jio_gadget.createJio({
            type: "indexeddb",
            database: "setting"
          });
          return jio_gadget.get("setting");
        })
        .push(function (doc) {
          doc.sub_gadget_version[gadget.props.options.app] = gadget.props.options.version;
          gadget.props.gadget_list = doc.sub_gadget_version;
          return gadget.setSetting("gadget_list", gadget.props.gadget_list);
        })
        .push(function () {
          return gadget.setSetting("app_url", gadget.props.full_url);
        });
  };

  function loadData(gadget) {
    var promise_list = [], gadget_url;
    function pushData(data, full_url) {
      if (data.doc.content_type !== "blob") {
        return gadget.jio_get(full_url + data.id)
          .push(undefined, function (error) {
            if (error.status_code === 404) {
              data.doc.url_string = data.id;
              data.doc.gadget_url = full_url;
              return gadget.jio_put(full_url + (data.id === '/' ? '' : data.id), data.doc);
            }
          });
      }
    }
    function loadDataGadget(url, version) {
      var jio_gadget, full_url = url + (url.endsWith('/') || version.startsWith('/') ? '' : '/') + version + (version.endsWith('/') ? '' : '/');
      return gadget.declareGadget(
        full_url + "gadget_jio.html",
        {
          scope: "app_" + full_url,
          element: gadget.props.element.querySelector("div"),
          sandbox: "iframe"
        }
      )
        .push(function (jio_gadget) {
          jio_gadget.createJio({
            type: "indexeddb",
            database: full_url
          });
          return jio_gadget.allDocs({include_docs: true});
        })
        .push(function (result) {
          var promise_list_sync = [], i;
          for (i = 0; i < result.data.total_rows; i += 1) {
            promise_list_sync.push(pushData(result.data.rows[i], full_url))
          }
        return RSVP.all(promise_list_sync);
        });
    }

    for (gadget_url in gadget.props.gadget_list) {
      if (gadget.props.gadget_list.hasOwnProperty(gadget_url)) {
        promise_list.push(loadDataGadget(gadget_url, gadget.props.gadget_list[gadget_url]));
      }
    }
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all(promise_list);
      })
      .push(function () {
        return gadget.setSetting(gadget.props.full_url, true);
      })
      .push(function () {
        return gadget.redirect({"page": "document_list"});
      });
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")

    .declareMethod("render", function (options) {
      var gadget = this,
          url = options.app,
          version = options.version,
          full_url = url + (url.endsWith('/') || version.startsWith('/') ? '' : '/') + version + (version.endsWith('/') ? '' : '/');
      gadget.props.options = options;
      gadget.props.full_url = full_url;
      return gadget.getSetting(gadget.props.full_url, false)
        .push(function (isLoaded) {
          if (isLoaded) {
            return gadget.redirect({"page": "document_list"});
          }
        });
    })
  
    .declareService(function () {
      var gadget = this;
      return initializeSetting(gadget)
        .push(function () {
          return loadData(gadget);
        });                
    });


}(window, document, RSVP, rJS, promiseEventListener));