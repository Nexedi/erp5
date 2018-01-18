/*global window, rJS, RSVP, DocsAPI, console, document,
 Common, require, jIO, URL, FileReader, atob, ArrayBuffer,
  Uint8Array, XMLHttpRequest, Blob, Rusha, define*/
/*jslint nomen: true, maxlen:80, indent:2*/
"use strict";
if (Common === undefined) {
  var Common = {};
}
var DocsAPI = {DocEditor: {}};
DocsAPI.DocEditor.version = function () {
  return null;
};

(function (rJS, RSVP, require, jIO) {

  var rusha = new Rusha();

  function hexdigest(blob) {
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.readBlobAsArrayBuffer(blob)
          .then(function (evt) {
            return rusha.digest(evt.target.result);
          });
      });
  }

  function display_error(gadget, error) {
    var display_error_element;
    display_error_element = gadget.props.element;
    display_error_element.innerHTML =
      '<br/><p style="color: red"></p><br/><br/>';
    display_error_element.querySelector('p').textContent = error;
    console.error(error);
    throw error;
  }

  function dataURLtoBlob(url) {
    if (url === 'data:') {
      return new Blob();
    }
    var byteString = atob(url.split(',')[1]),
      mimeString = url.split(',')[0].split(':')[1].split(';')[0],
      ab = new ArrayBuffer(byteString.length),
      ia = new Uint8Array(ab),
      i;
    for (i = 0; i < byteString.length; i += 1) {
      ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], {type: mimeString});
  }

  rJS(window)
    .ready(function (g) {
      g.props = {
        save_defer: null,
        handlers: {}
      };
    })
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          return {};
        });
    })
    .declareAcquiredMethod("triggerSubmit", "triggerSubmit")
    .declareAcquiredMethod("triggerMaximize", "triggerMaximize")
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareMethod("jio_getAttachment", function (docId, attId, opt) {
      var g = this,
        queue;
      if (attId === 'body.txt') {
        opt = 'asText';
        if (!docId) {
          docId = '/';
        }
      } else {
        if (!docId) {
          docId = '/media/';
        }
      }
      queue = g.props.value_zip_storage.getAttachment(docId, attId)
        .push(function (blob) {
          var data;
          if (opt === "asText") {
            data = jIO.util.readBlobAsText(blob)
              .then(function (evt) {
                return evt.target.result;
              });
          } else if (opt === "asBlobURL") {
            data = URL.createObjectURL(blob);
          } else if (opt === "asDataURL") {
            data = new RSVP.Promise(function (resolve, reject) {
              var reader = new FileReader();
              reader.addEventListener('load', function () {
                resolve(reader.result);
              });
              reader.addEventListener('error', reject);
              reader.readAsDataURL(blob);
            });
          } else {
            data = blob;
          }
          return data;
        });
      return queue;
    })
    .declareMethod("jio_putAttachment", function (docId, atId, data) {
      var g = this,
        zip = g.props.value_zip_storage,
        queue,
        content_type,
        start = data.slice(0, 5);
      if (!docId) {
        docId = '/media/';
      }
      if (typeof data === 'string' && start === "data:") {
        data = dataURLtoBlob(data);
      }
      if (atId) {
        queue = zip.putAttachment(docId, atId, data)
          .push(undefined, function (error) {
            if (error.status_code === 404) {
              // make dir
              return zip.put(docId, {})
                .push(function () {
                  return zip.putAttachment(docId, atId, data);
                });
            }
            throw error;
          });
      } else {
        queue = hexdigest(data)
          .push(function (digest) {
            content_type = data.type;
            if (!content_type) {
              content_type = "application/binary";
            }
            content_type = content_type.split('/');
            atId = content_type[0] + ',' + digest +
              '.' + content_type[1];
            return zip.allAttachments(docId)
              .push(undefined, function (error) {
                if (error.status_code === 404) {
                  // make dir
                  return zip.put(docId, {});
                }
                throw error;
              })
              .push(function (list) {
                if (list.hasOwnProperty(atId)) {
                  return {};
                }
                return zip.putAttachment(docId, atId, data);
              });
          })
          .push(function () {
            return atId;
          });
      }
      return queue;
    })

    // methods emulating Gateway used for connection with ooffice begin.
    .declareMethod('appReady', function () {
      var g = this;
      console.log('appReady');
      g.props.handlers.init({
        config: {
          lang: 'en',
          canAutosave: false,
          canCoAuthoring: false,
          canBackToFolder: true,
          canCreateNew: false,
          canAnalytics: false,
          customization: {
            about: false,
            feedback: false
          }
        }
      });
      g.props.handlers.opendocument({
        doc: {
          key: g.props.jio_key,
          //title: g.props.doc.title || "",
          //fileType: undefined,
          //vkey: undefined,
          url: "_offline_",
          permissions: {
            edit: true,
            download: true,
            reader: true
          }
        }
      });
    })
    .declareMethod('documentReady', function () {
      console.log();
    })
    .declareMethod('goBack', function (new_window) {
    })
    .declareMethod('requestEditRights', function () {
      var g = this;
      g.props.handlers.applyEditRights({
        allowed: true,
        message: ""
      });
    })
    .declareMethod('requestHistory', function () {
    })
    .declareMethod('requestHistoryData', function (revision) {
    })
    .declareMethod('requestHistoryClose', function () {
    })
    .declareMethod('reportError', function (code, description) {
      console.log(['reportError', code, description]);
    })
    .declareMethod('sendInfo', function (info) {
      console.log(['sendInfo', info]);
    })
    .declareMethod('setDocumentModified', function (modified) {
    })
    .declareMethod('internalMessage', function (event_name, data) {
      console.log(['internalMessage', event_name, data]);
    })
    .declareMethod('updateVersion', function () {
    })
    .declareMethod('on', function (event_name, handler) {
      var g = this;
      g.props.handlers[event_name] = handler;
    })
    // methods emulating Gateway used for connection with ooffice end.

    .declareMethod('render', function (options) {
      console.log('begin render');
      var g = this,
        queue = new RSVP.Queue();
      return queue
        .push(function () {
          return g.getSetting('portal_type');
        })
        .push(undefined, function (error) {
          return "";
        })
        .push(function (portal_type) {
          var value, documentType, magic;
          portal_type = portal_type || options.portal_type;
          g.props.binary_loader = false;
          g.props.jio_key = options.jio_key;
          g.props.key = options.key || "text_content";
          g.props.documentType = portal_type.toLowerCase();
          value = options.value;
          if (value === "data:" ||
            g.props.value === "data:application/octet-stream;base64," ||
            value === undefined) {
            // fix empty value
            value = "";
          }
          if (value) {
            if (value.slice === undefined) {
              throw "not suported type of variable containing the document: " +
                typeof value;
            }
            if (value.slice(0, 5) === "data:") {
              value = atob(value.split(',')[1]);
            }
          }
          if (value) {
            switch (value.slice(0, 4)) {
            case "PK\x03\x04":
            case "PK\x05\x06":
              g.props.value_zip_storage = jIO.createJIO({
                type: "zipfile",
                file: value
              });
              return g.props.value_zip_storage.getAttachment('/', 'body.txt')
                .push(undefined, function (error) {
                  if (error.status_code === 404) {
                    throw 'not supported format of document: body.txt absent "' +
                    value.slice(0, 100) + '"';
                  }
                  throw error;
                })
                .push(jIO.util.readBlobAsText)
                .push(function (evt) {
                  return evt.target.result;
                });
            }
          }
          g.props.value = value;
          if (!g.props.documentType && value === "") {
            throw "can not create empty document " +
            "because portal_type is unknown";
          }
          if (value) {
            magic = g.props.value.slice(0, 4);
            switch (magic) {
            case 'XLSY':
              documentType = "spreadsheet";
              break;
            case 'PPTY':
              documentType = "presentation";
              break;
            case 'DOCY':
              documentType = "text";
              break;
            default:
              throw "can not detect document type by magic: " + magic;
            }
            if (g.props.documentType) {
              if (documentType !== g.props.documentType) {
                throw "editor not fit the document type";
              }
            } else {
              //set editor type by documentType
              g.props.documentType = documentType;
            }
          }
        })
        .push(function () {
          return jIO.util.ajax({
            type: "GET",
            url: "onlyoffice.gadget.appcache"
          });
        })
        .push(function (response) {
          /*configure requeryjs for rename
          view and edit to view_folder and edit_folder
          in dependencies
          */
          var text = response.target.responseText,
            relative_url_list = text.split('\r\n'),
            i,
            new_url,
            old_url,
            config = {};
          if (relative_url_list.length === 1) {
            relative_url_list = text.split('\n');
          }
          if (relative_url_list.length === 1) {
            relative_url_list = text.split('\r');
          }
          for (i = 0; i < relative_url_list.length; i += 1) {
            if (
              relative_url_list[i] !== "" &&
              relative_url_list[i].charAt(0) !== '#' &&
              relative_url_list[i].charAt(0) !== ' ') {
              relative_url_list[i].replace("\r", "");
              new_url = relative_url_list[i]
                .replace('onlyoffice/web-apps/apps/', '')
                .replace(/\.[^.]*$/, '');
              old_url = new_url
                .replace(/(^|\/)view_folder\//g,"$1view/")
                .replace(/(^|\/)edit_folder\//g,"$1edit/");
              if (old_url !== new_url) {
                config[old_url] = [
                    new_url,
                    old_url
                  ];
              }
            }
          }
          require.config({paths: config});
        })
        .push(function () {
          var app_url, sdk_deps = ["promise!sdk_async_loader"];
          if (!g.props.value_zip_storage) {
            g.props.value_zip_storage = jIO.createJIO({type: "zipfile"});
          }
          switch (g.props.documentType) {
          case 'spreadsheet':
            app_url = "web-apps/apps/spreadsheeteditor/main/app.js";
            define("sdk_files", [], function () {
              return "webexcel.json";
            });
            sdk_deps.push('window!Xmla');
            break;
          case 'text':
            app_url = "web-apps/apps/documenteditor/main/app.js";
            define("sdk_files", [], function () {
              return "webword.json";
            });
            break;
          case 'presentation':
            app_url = "web-apps/apps/presentationeditor/main/app.js";
            define("sdk_files", [], function () {
              return "webpowerpoint.json";
            });
            break;
          }

          Common.Gateway = g;

          require.onError = function (error) {
            console.error(error);
          };
          require.config({catchError: true});

          if (g.props.binary_loader) {
            g.props.base_url = "onlyoffice-bin/";
          } else {
            g.props.base_url = "onlyoffice/";
            define("sdk", sdk_deps, function () {
            });
          }
          app_url = g.props.base_url + app_url;

          function loadScript(src) {
            return new RSVP.Promise(function (resolve, reject) {
              var s;
              s = document.createElement('script');
              s.src = src;
              s.onload = resolve;
              s.onerror = reject;
              document.head.appendChild(s);
            });
          }

          return loadScript(app_url);
        })
        .push(undefined, function (error) {
          display_error(g, error);
        });
    })

    .declareMethod('getContent', function () {
      var g = this,
        zip = g.props.value_zip_storage,
        queue = new RSVP.Queue(),
        save_defer = RSVP.defer();
      g.props.save_defer = save_defer;
      g.props.handlers.save();
      return queue.push(function () {
        return save_defer.promise;
      })
        .push(function (data) {
          if (data) {
            var body = data[g.props.key];
            return zip.putAttachment('/', 'body.txt', body);
          }
        })
        .push(function () {
          return zip.getAttachment('/', 'body.txt')
            .push(undefined, function (error) {
              if (error.status_code === 404) {
                return "";
              }
              throw error;
            });
        })
        .push(function (Editor_bin) {
          if (Editor_bin) {
            return zip.getAttachment('/', '/');
          } else {
            return new Blob();
          }
        })
        .push(function (zip_blob) {
          return jIO.util.readBlobAsDataURL(zip_blob);
        })
        .push(function (evt) {
          var data = {};
          data[g.props.key] = evt.target.result;
          return data;
        });
    });
}(rJS, RSVP, require, jIO));