/*global window, rJS, RSVP, DocsAPI, console, document*/
/*jslint nomen: true, maxlen:80, indent:2*/
if (Common === undefined) {
  var Common = {};
}
(function (rJS, RSVP, require) {
  "use strict";

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
    .declareAcquiredMethod("setFillStyle", "setFillStyle")
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")


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
      var g = this;
      g.triggerMaximize()
        .push(function (size) {
          var iframe = g.props.element.querySelector('iframe');
          iframe.style.height = size.height;
          iframe.style.width = size.width;
        });
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
      var g = this;
      g.props.jio_key = options.jio_key;
      return new RSVP.Queue()
        .push(function () {
          return g.getSetting('portal_type');
        })
        .push(function (portal_type) {
          g.props.documentType = portal_type.toLowerCase();
          g.props.key = options.key || "text_content";
          return g.setFillStyle();
        })
        .push(function (size) {
          var element = g.props.element,
            sdkPath,
            nameSpace,
            backboneControllers,
            styles;
          element.style.height = size.height;
          element.style.width = size.width;
          // g.fullscreen();
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
              styles = [
                // sdk changed to sdk/Excel/sdk-all
                'css!sdk/../css/main.css',
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
                'Common.Controllers.ExternalDiagramEditor'
              ];
              styles = [
                'css!presentationeditor/main/resources/css/app.css'
              ];
              break;
          }

          Common.Gateway = g;
          require.config({
            baseUrl: "apps/",
            waitSeconds: 360,
            paths: {
              jquery: '../vendor/jquery/jquery',
              underscore: '../vendor/underscore/underscore',
              backbone: '../vendor/backbone/backbone',
              bootstrap: '../vendor/bootstrap/dist/js/bootstrap',
              text: '../vendor/requirejs-text/text',
              perfectscrollbar: 'common/main/lib/mods/perfect-scrollbar',
              jmousewheel: '../vendor/perfect-scrollbar/src/jquery.mousewheel',
              xregexp: '../vendor/xregexp/xregexp-all-min',
              sockjs: '../vendor/sockjs/sockjs.min',
              jsziputils: '../vendor/jszip-utils/jszip-utils.min',
              jsrsasign: '../vendor/jsrsasign/jsrsasign-latest-all-min',
              allfonts: '../sdkjs/common/AllFonts',
              sdk: '../sdkjs/' + sdkPath + '/sdk-all-min',
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
              },
              sdk: {
                deps: [
                  'jquery',
                  'underscore',
                  'allfonts',
                  'xregexp',
                  'sockjs',
                  'jsziputils',
                  'jsrsasign'
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
          console.log('gadget_ooffice.js redner error:' + error);
        });
    })

    .declareMethod('getContent', function () {
      var g = this,
        save_defer;
      save_defer = RSVP.defer();
      g.props.save_defer = save_defer;
      g.props.handlers.save();
      return save_defer.promise;
    });

}(rJS, RSVP, require));