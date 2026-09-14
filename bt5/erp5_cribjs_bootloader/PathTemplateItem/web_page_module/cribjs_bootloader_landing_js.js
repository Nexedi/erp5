/*jslint nomen: true, indent: 2, maxerr: 100 */
/*global window, rJS, RSVP, jIO, fetch, Promise, document, console, Blob
, JSZip */
(function (rJS, RSVP, JSZip, jIO) {
  "use strict";

  function getStorageGadget(gadget) {
    var getURL = window.location;
    return new RSVP.Queue()
      .push(function () {
        var url = "crib-enable.html";
        if (gadget.props.storage_gadget_url === url) {
          return gadget.getDeclaredGadget("storage")
            .push(undefined, function () {
              return gadget.declareGadget(
                url,
                {
                  "scope": "storage",
                  "sandbox": "iframe",
                  "element": gadget.props.element
                    .querySelector('.storage-access')
                }
              );
            });
        }
        gadget.props.storage_gadget_url = url;
        return gadget.dropGadget("storage")
          .push(function () {}, function () {})
          .push(function () {
            return gadget.declareGadget(
              url,
              {
                "scope": "storage",
                "sandbox": "iframe",
                "element": gadget.props.element
                  .querySelector('.storage-access')
              }
            );
          });
      })
      .push(undefined, function (e) {
        // Ugly Hack to reload page and make service worker available
        if (e &&
            e.toString()
             .indexOf("Please reload this page to allow Service Worker to control this page") > -1) {
          window.location.reload(false);
          throw e;
        }
        throw e;
      });
  }

  function getParameterDict() {
    var hash = window.location.hash.substring(1),
      params = {};
    hash.split('&').map(hk => {
      let temp = hk.split('=');
      params[temp[0]] = temp[1];
    });
    return params;
  }

  function loadZipIntoCrib(gadget, zip, from_path) {
    var promise_list = [];
    zip.forEach(function (relativePath, zipEntry) {
      var end_url;
      if (zipEntry.dir) {
        return;
      }
      if (!relativePath.startsWith(from_path)) {
        return;
      }
      relativePath = relativePath.substring(from_path.length);
      if (relativePath.startsWith("/")) {
        end_url = relativePath.substring(1);
      } else {
        end_url = relativePath;
      }
      promise_list.push(
        new RSVP.Queue()
          .push(function () {
            return zipEntry.async('blob');
          })
          .push(function (result) {
            if (end_url.endsWith(".js")) {
              // This is a ugly hack as mimetype needs to be correct for JS
              result = result.slice(0, result.size, "application/javascript");
            } else if (end_url.endsWith(".html")) {
              // This is a ugly hack as mimetype needs to be correct for JS
              result = result.slice(0, result.size, "text/html");
            } else if (end_url.endsWith(".css")) {
              // This is a ugly hack as mimetype needs to be correct for JS
              result = result.slice(0, result.size, "text/css");
            }
            return gadget.put(end_url, {blob: result});
          })
      );
    });
    return RSVP.all(promise_list);
  }

  function loadContentFromZIPURL(gadget, options) {
    var path_to_load = options.to_path,
      from_path = options.from_path,
      zip_url = options.zip_url;
    return new RSVP.Queue()
      .push(function () {
        return fetch(zip_url)
          .then(function (response) {                       // 2) filter on 200 OK
            if (response.status === 200 || response.status === 0) {
              return Promise.resolve(response.blob());
            }
            return Promise.reject(new Error(response.statusText));
          });
      })
      .push(JSZip.loadAsync)
      .push(function (zip) {
        return loadZipIntoCrib(gadget, zip, from_path, path_to_load);
      });
  }

  function loadCribJSFromZipUrl(gadget, data) {
    return loadContentFromZIPURL(gadget, {
      path: document.location.href,
      zip_url: data.zip_url,
      from_path: data.from_path,
      to_path: data.to_path,
      application_id: "cribjs"
    })
      .push(function () {
        document.location = data.redirect_url;
      })
      .push(console.log, console.log);
  }

  rJS(window)

    .declareMethod('render', function () {
      var gadget = this,
        getURL = window.location,
        site = getURL.protocol + "//" + getURL.host,
        params = getParameterDict(),
        data = {
          from_path: "cribjs-editor-master/",
          to_path: site,
          zip_url: "https://lab.nexedi.com/cedric.leninivin/cribjs-editor/" +
            "-/archive/master/cribjs-editor-master.zip",
          redirect_url: window.location.href
        };
      if (params.hasOwnProperty("from_path")) {
        data.from_path = params.from_path;
      }
      if (params.hasOwnProperty("to_path")) {
        data.to_path  = params.to_path;
      }
      if (params.hasOwnProperty("zip_url")) {
        data.zip_url = params.zip_url;
      }
      if (params.hasOwnProperty("redirect_url")) {
        data.redirect_url = decodeURIComponent(params.redirect_url);
      }
      return RSVP.Queue()
        .push(function () {
          return loadCribJSFromZipUrl(gadget, data);
        });
    })
    .declareMethod('put', function (url, parameter) {
      var blob, gadget = this;
      if (parameter.blob !== undefined) {
        blob = parameter.blob;
      } else {
        blob = new Blob(
          [parameter.content],
          {type: parameter.type}
        );
      }
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            getStorageGadget(gadget),
            jIO.util.readBlobAsDataURL(blob)
          ]);
        })
        .push(function (result_list) {
          return result_list[0].put(url, result_list[1].target.result);
        })
        .push(console.log, console.log);
    })

    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        })
        .push(function () {
          return getStorageGadget(g);
        })
        .push(function () {
          return g.render({});
        });
    });
}(rJS, RSVP, JSZip, jIO));