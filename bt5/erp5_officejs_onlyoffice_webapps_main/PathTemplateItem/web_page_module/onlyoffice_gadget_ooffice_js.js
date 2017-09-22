/*global window, rJS, RSVP, DocsAPI, console, document,
 Common, require, jIO, URL, FileReader, atob, ArrayBuffer,
  Uint8Array, XMLHttpRequest, Blob, Rusha*/
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
    .declareMethod('ready', function () {
      var g = this;
      console.log('ready');
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
          var value;
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
                    throw 'not supported format of document: "' +
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
          return value;
        })
        .push(function (value) {
          var magic, documentType,
            sdkPath,
            nameSpace,
            backboneControllers,
            styles;
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
          if (!g.props.value_zip_storage) {
            g.props.value_zip_storage = jIO.createJIO({type: "zipfile"});
          }
          switch (g.props.documentType) {
          case 'spreadsheet':
            sdkPath = 'cell';
            nameSpace = 'SSE';
            backboneControllers = [
              'Viewport',
              'DocumentHolder',
              'CellEditor',
              'FormulaDialog',
              'Print',
              'Toolbar',
              'Statusbar',
              'RightMenu',
              'LeftMenu',
              'Main',
              'Common.Controllers.Fonts',
              'Common.Controllers.Chat',
              'Common.Controllers.Comments',
              'Common.Controllers.Plugins'
            ];
            define("sdk_files", [], function () {
              return [
                "../common/browser.js",
                "../common/commonDefines.js",
                "../common/docscoapicommon.js",
                "../common/docscoapi.js",
                "../common/apiCommon.js",
                "../common/SerializeCommonWordExcel.js",
                "../common/editorscommon.js",
                "../common/HistoryCommon.js",
                "../common/TableId.js",
                "../common/TableIdChanges.js",
                "../common/AdvancedOptions.js",
                "../cell/apiDefines.js",
                "../cell/utils/utils.js",
                "../cell/view/HandlerList.js",
                "../cell/model/CollaborativeEditing.js",
                "../common/apiBase.js",
                "../common/Private/license.js",
                "../word/apiCommon.js",
                "../cell/api.js",
                "../common/Local/license.js",
                "../common/Local/jio.js"
              ];
            });
            styles = [
              'css!../sdkjs/cell/css/main.css',
              'css!spreadsheeteditor/main/resources/css/app.css'
            ];
            break;
          case 'text':
            sdkPath = 'word';
            nameSpace = 'DE';
            backboneControllers = [
              'Viewport',
              'DocumentHolder',
              'Toolbar',
              'Statusbar',
              'RightMenu',
              'LeftMenu',
              'Main',
              'Common.Controllers.Fonts',
              'Common.Controllers.History',
              'Common.Controllers.Chat',
              'Common.Controllers.Comments',
              'Common.Controllers.Plugins',
              'Common.Controllers.ExternalDiagramEditor',
              'Common.Controllers.ExternalMergeEditor',
              'Common.Controllers.ReviewChanges'
            ];
            define("sdk_files", [], function () {
              return [
                "../common/browser.js",
                "../common/commonDefines.js",
                "../common/docscoapicommon.js",
                "../common/docscoapi.js",
                "../common/spellcheckapi.js",
                "../common/spellCheckLanguage.js",
                "../common/spellCheckLanguagesAll.js",
                "../common/apiCommon.js",
                "../common/SerializeCommonWordExcel.js",
                "../common/editorscommon.js",
                "../common/HistoryCommon.js",
                "../common/TableId.js",
                "../common/TableIdChanges.js",
                "../common/AdvancedOptions.js",
                "../word/apiDefines.js",
                "../common/CollaborativeEditingBase.js",
                "../word/Editor/CollaborativeEditing.js",
                "../common/apiBase.js",
                "../common/Private/license.js",
                "../word/apiCommon.js",
                "../word/api.js",
                "../common/Local/license.js",
                "../common/Local/jio.js"
              ];
            });
            styles = [
              'css!documenteditor/main/resources/css/app.css'
            ];
            break;
          case 'presentation':
            sdkPath = 'slide';
            nameSpace = 'PE';
            backboneControllers = [
              'Viewport',
              'DocumentHolder',
              'Toolbar',
              'Statusbar',
              'RightMenu',
              'LeftMenu',
              'Main',
              'Common.Controllers.Fonts',
              'Common.Controllers.Chat',
              'Common.Controllers.Comments',
              'Common.Controllers.Plugins',
              'Common.Controllers.ExternalDiagramEditor'
            ];
            define("sdk_files", [], function () {
              return [
                "../common/browser.js",
                "../common/commonDefines.js",
                "../common/docscoapicommon.js",
                "../common/docscoapi.js",
                "../common/apiCommon.js",
                "../common/SerializeCommonWordExcel.js",
                "../common/editorscommon.js",
                "../common/HistoryCommon.js",
                "../common/TableId.js",
                "../common/TableIdChanges.js",
                "../common/AdvancedOptions.js",
                "../slide/apiDefines.js",
                "../common/CollaborativeEditingBase.js",
                "../slide/Editor/CollaborativeEditing.js",
                "../common/apiBase.js",
                "../common/Private/license.js",
                "../word/apiCommon.js",
                "../slide/api.js",
                "../common/Local/license.js",
                "../common/Local/empty_slide.js",
                "../common/Local/jio.js"
              ];
            });
            styles = [
              'css!presentationeditor/main/resources/css/app.css'
            ];
            break;
          }

          Common.Gateway = g;
          define("sdk", [
            "promise!sdk_async_loader"
          ], function () {
          });
          require.config({
            baseUrl: "apps/",
            waitSeconds: 360,
            paths: {
              jquery: '../vendor/jquery/jquery',
              underscore: '../vendor/underscore/underscore',
              backbone: '../vendor/backbone/backbone',
              bootstrap: '../vendor/bootstrap/dist/js/bootstrap',
              text: '../vendor/requirejs-text/text',
              promise: '../vendor/requirejs-promise/requirejs-promise',
              perfectscrollbar: 'common/main/lib/mods/perfect-scrollbar',
              jmousewheel: '../vendor/perfect-scrollbar/src/jquery.mousewheel',
              xregexp: '../vendor/xregexp/xregexp-all-min',
              sockjs: '../vendor/sockjs/sockjs.min',
              jsziputils: '../vendor/jszip-utils/jszip-utils.min',
              jsrsasign: '../vendor/jsrsasign/jsrsasign-latest-all-min',
              allfonts: '../fonts/AllFonts',
              api: 'api/documents/api',
              core: 'common/main/lib/core/application',
              notification: 'common/main/lib/core/NotificationCenter',
              keymaster: 'common/main/lib/core/keymaster',
              tip: 'common/main/lib/util/Tip',
              localstorage: 'common/main/lib/util/LocalStorage',
              analytics: 'common/Analytics',
              locale: 'common/locale',
              irregularstack: 'common/IrregularStack'
            },
            shim: {
              underscore: {
                exports: "_"
              },
              backbone: {
                deps: [
                  "underscore",
                  "jquery"
                ],
                exports: "Backbone"
              },
              bootstrap: {
                deps: [
                  'jquery'
                ]
              },
              perfectscrollbar: {
                deps: [
                  'jmousewheel'
                ]
              },
              notification: {
                deps: [
                  'backbone'
                ]
              },
              core: {
                deps: [
                  'backbone',
                  'notification',
                  'irregularstack'
                ]
              }
            }
          });
          require([
            'backbone',
            'bootstrap',
            'core',
            'analytics',
            'locale'
          ].concat(styles), function (Backbone) {
            Backbone.history.start();
            var app = new Backbone.Application({
              nameSpace: nameSpace,
              autoCreate: false,
              controllers: backboneControllers
            });
            Common.Locale.apply();
            switch (g.props.documentType) {
            case 'spreadsheet':
              require([
                'spreadsheeteditor/main/app/controller/Viewport',
                'spreadsheeteditor/main/app/controller/DocumentHolder',
                'spreadsheeteditor/main/app/controller/CellEditor',
                'spreadsheeteditor/main/app/controller/Toolbar',
                'spreadsheeteditor/main/app/controller/Statusbar',
                'spreadsheeteditor/main/app/controller/RightMenu',
                'spreadsheeteditor/main/app/controller/LeftMenu',
                'spreadsheeteditor/main/app/controller/Main',
                'spreadsheeteditor/main/app/controller/Print',
                'spreadsheeteditor/main/app/view/ParagraphSettings',
                'spreadsheeteditor/main/app/view/ImageSettings',
                'spreadsheeteditor/main/app/view/ChartSettings',
                'spreadsheeteditor/main/app/view/ShapeSettings',
                'spreadsheeteditor/main/app/view/TextArtSettings',
                'common/main/lib/util/utils',
                'common/main/lib/util/LocalStorage',
                'common/main/lib/controller/Fonts',
                'common/main/lib/controller/Comments',
                'common/main/lib/controller/Chat',
                'common/main/lib/controller/Plugins'
              ], function () {
                app.start();
              });
              break;
            case 'text':
              require([
                'documenteditor/main/app/controller/Viewport',
                'documenteditor/main/app/controller/DocumentHolder',
                'documenteditor/main/app/controller/Toolbar',
                'documenteditor/main/app/controller/Statusbar',
                'documenteditor/main/app/controller/RightMenu',
                'documenteditor/main/app/controller/LeftMenu',
                'documenteditor/main/app/controller/Main',
                'documenteditor/main/app/view/ParagraphSettings',
                'documenteditor/main/app/view/HeaderFooterSettings',
                'documenteditor/main/app/view/ImageSettings',
                'documenteditor/main/app/view/TableSettings',
                'documenteditor/main/app/view/ShapeSettings',
                'common/main/lib/util/utils',
                'common/main/lib/util/LocalStorage',
                'common/main/lib/controller/Fonts',
                'common/main/lib/controller/History',
                'common/main/lib/controller/Comments',
                'common/main/lib/controller/Chat',
                'common/main/lib/controller/Plugins',
                'documenteditor/main/app/view/ChartSettings',
                'common/main/lib/controller/ExternalDiagramEditor',
                'common/main/lib/controller/ExternalMergeEditor',
                'common/main/lib/controller/ReviewChanges'
              ], function () {
                app.start();
              });
              break;
            case 'presentation':
              require([
                'presentationeditor/main/app/controller/Viewport',
                'presentationeditor/main/app/controller/DocumentHolder',
                'presentationeditor/main/app/controller/Toolbar',
                'presentationeditor/main/app/controller/Statusbar',
                'presentationeditor/main/app/controller/RightMenu',
                'presentationeditor/main/app/controller/LeftMenu',
                'presentationeditor/main/app/controller/Main',
                'presentationeditor/main/app/view/ParagraphSettings',
                'presentationeditor/main/app/view/ImageSettings',
                'presentationeditor/main/app/view/ShapeSettings',
                'presentationeditor/main/app/view/SlideSettings',
                'presentationeditor/main/app/view/TableSettings',
                'presentationeditor/main/app/view/TextArtSettings',
                'common/main/lib/util/utils',
                'common/main/lib/util/LocalStorage',
                'common/main/lib/controller/Fonts',
                'common/main/lib/controller/Comments',
                'common/main/lib/controller/Chat',
                'presentationeditor/main/app/view/ChartSettings',
                'common/main/lib/controller/ExternalDiagramEditor'
              ], function () {
                window.compareVersions = true;
                app.start();
              });
              break;
            }
          }, function (err) {
            throw err;
          });
          return {};
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
          return zip.getAttachment('/', '/');
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