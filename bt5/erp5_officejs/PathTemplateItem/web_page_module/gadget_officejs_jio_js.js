/*global window, rJS, jIO, FormData, UriTemplate, Rusha */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO) {
  "use strict";

  var rusha = new Rusha();

  // jIO call wrapper for redirection to authentication page if needed
  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage;
    if (storage === undefined) {
      return gadget.redirect({page: "jio_configurator"});
    }
    return storage[method_name].apply(storage, argument_list)
      .push(undefined, function (error) {
        if ((error.target !== undefined) && (error.target.status === 401)) {
          var regexp,
            site,
            auth_page;
          if (gadget.state_parameter_dict.jio_storage_name === "ERP5") {
            regexp = /^X-Delegate uri=\"(http[s]?:\/\/[\/\-\[\]{}()*+=:?&.,\\\^$|#\s\w%]+)\"$/;
            auth_page = error.target.getResponseHeader('WWW-Authenticate');
            if (regexp.test(auth_page)) {
              site = UriTemplate.parse(
                regexp.exec(auth_page)[1]
              ).expand({
                came_from: window.location.href,
                cors_origin: window.location.origin,
                });
            }
          }
          if (gadget.state_parameter_dict.jio_storage_name === "DAV") {
            regexp = /^Nayookie login_url=(http[s]?:\/\/[\/\-\[\]{}()*+=:?&.,\\\^$|#\s\w%]+)$/;
            auth_page = error.target.getResponseHeader('WWW-Authenticate');
            if (regexp.test(auth_page)) {
              site = UriTemplate.parse(
                regexp.exec(auth_page)[1]
              ).expand({
                back_url: window.location.href,
                origin: window.location.origin,
                });
            }
          }
          if (site) {
            return gadget.redirect({ toExternal: true, url: site});
          }
        }
        throw error;
      });
  }

  rJS(window)

    .ready(function (gadget) {
      // Initialize the gadget local parameters
      gadget.state_parameter_dict = {};
    })

    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")

    .declareMethod('createJio', function (jio_options) {
      var gadget = this;
      if (jio_options === undefined) {
        return;
      }
      this.state_parameter_dict.jio_storage = jIO.createJIO(jio_options);
      return this.getSetting("jio_storage_name")
        .push(function (jio_storage_name) {
          gadget.state_parameter_dict.jio_storage_name = jio_storage_name;
        });
    })
    .declareMethod('allDocs', function () {
      return wrapJioCall(this, 'allDocs', arguments);
    })
    .declareMethod('allAttachments', function () {
      return wrapJioCall(this, 'allAttachments', arguments);
    })
    .declareMethod('get', function () {
      return wrapJioCall(this, 'get', arguments);
    })
    .declareMethod('put', function () {
      return wrapJioCall(this, 'put', arguments);
    })
    .declareMethod('post', function () {
      return wrapJioCall(this, 'post', arguments);
    })
    .declareMethod('remove', function () {
      return wrapJioCall(this, 'remove', arguments);
    })
    .declareMethod('getAttachment', function (docId, atId, opt) {
      return wrapJioCall(this, 'getAttachment', [docId, atId])
      .push(function (blob) {
        var data;
        if (opt === "asBlobURL") {
          data = URL.createObjectURL(blob);
        } else if (opt === "asDataURL") {
          data = new RSVP.Promise(function (resolve, reject) {
            var reader = new FileReader();
            reader.addEventListener('load', function () {
              resolve(reader.result);
            });
            reader.readAsDataURL(blob);
          });
        } else {
          data = blob;
        }
        return data;
      });
    })
    .declareMethod('putAttachment', function (docId, atId, data) {
      var start = data.slice(0, 5),
          gadget = this,
          queue = new RSVP.Queue();
      if (start === "data:") {
        queue.push(function () {
          var byteString = atob(data.split(',')[1]);

          // separate out the mime component
          var mimeString = data.split(',')[0].split(':')[1].split(';')[0];

          // write the bytes of the string to an ArrayBuffer
          var ab = new ArrayBuffer(byteString.length);
          var ia = new Uint8Array(ab);
          for (var i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
          }
          return [ab, mimeString];
        });
      } else if (start === "blob:") {
        queue.push(function () {
          return new Promise(function (resolve, reject) {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', data, true);
            xhr.responseType = 'arraybuffer';
            xhr.onload = function (e) {
              if (this.status == 200) {
                resolve([this.response, this.getResponseHeader("Content-Type")]);
              }
            };
            xhr.send();
          });
        });
      }
      return queue.push(function (result) {
        var ab = result[0],
            mimeString = result[1];
        if (!atId) {
          atId = mimeString + ',' + rusha.digestFromArrayBuffer(ab);
        }
        return wrapJioCall(gadget, 'allAttachments', [docId])
          .push(function (list) {
            var blob;
            if (list.hasOwnProperty(atId)) {
              return {};
            } else {
              blob = new Blob([ab], {type: mimeString});
              return wrapJioCall(gadget, 'putAttachment', [docId, atId, blob]);
            }
          });
      })
      .push(function () {
        return atId;
      });
    })
    .declareMethod('removeAttachment', function () {
      return wrapJioCall(this, 'removeAttachment', arguments);
    })
    .declareMethod('repair', function () {
      return wrapJioCall(this, 'repair', arguments);
    });

}(window, rJS, jIO));