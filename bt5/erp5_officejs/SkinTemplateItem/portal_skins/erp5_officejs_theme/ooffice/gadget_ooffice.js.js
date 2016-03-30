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
        });
    })
    .declareAcquiredMethod("triggerSubmit", "triggerSubmit")
    .declareAcquiredMethod("triggerMaximize", "triggerMaximize")
    .declareAcquiredMethod("setFillStyle", "setFillStyle")

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
          customization: {
            about: false,
            feedback: false
          }
        }
      });
      g.props.handlers.opendocument({
        doc: {
          title: g.props.title,
          //fileType: undefined,
          //vkey: undefined,
          data: g.props.value,
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
    .declareMethod('save', function (url) {
      var g = this,
        result = {};
      if (g.props.save_defer === null) {
        g.triggerSubmit();
      } else {
        result[g.props.key] = url;;
        g.props.save_defer.resolve(result);
        g.props.save_defer = null;
      }
      return true;
      // if you want to async save process return false
      // and call api.processSaveResult when ready
      // g.props.docEditor.processSaveResult();
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
      console.log(['reportError', code, description])
    })
    .declareMethod('setDocumentModified', function (modified) {

    })
    .declareMethod('internalMessage', function (event_name, data) {
      console.log(['internalMessage', event_name, data])
    })
    .declareMethod('updateVersion', function () {

    })
    .declareMethod('on', function (event_name, handler) {
      var g = this;
      g.props.handlers[event_name] = handler;
    })
    // methods emulating Gateway used for connection with ooffice end.

    .declareMethod('render', function (options) {
      var g = this,
        documentType,
        magic_to_format_map = {
          'DOCY;': 'text',
          'XLSY;': 'spreadsheet',
          'PPTY;': 'presentation'
        };
      if (options.value === undefined) {
        documentType = options.portal_type;
        g.props.value = '';
      } else {
        documentType = magic_to_format_map[options.value.substring(0, 5)];
        if (documentType === undefined) {
          g.props
            .element
            .getElementsByClassName(placeholder)[0]
            .textContent = options.value;
          return {};
        }
        g.props.value = options.value;
      }
      g.props.title = options.title;
      g.props.key = options.key || "text_content";

      return g.setFillStyle()
        .push(function (size) {
          var element = g.props.element,
            sdkPath,
            nameSpace,
            backboneControllers,
            styles;
          element.style.height = size.height;
          element.style.width = size.width;
          // g.fullscreen();
          switch (documentType) {
            case 'spreadsheet':
              sdkPath = 'Excel';
              nameSpace = "SSE";
              backboneControllers = [
                "Viewport",
                "DocumentHolder",
                "CellEditor",
                "FormulaDialog",
                "Print",
                "Toolbar",
                "Statusbar",
                "RightMenu",
                "LeftMenu",
                "Main",
                "Common.Controllers.Fonts",
                "Common.Controllers.Chat",
                "Common.Controllers.Comments"
              ];
              styles = [
                // sdk changed to sdk/Excel/sdk-all
                "css!sdk/../css/main.css",
                "css!spreadsheeteditor/main/resources/css/app.css"
              ];
              break;
            case 'text':
              sdkPath = 'Word';
              nameSpace = "DE";
              backboneControllers = [
                "Viewport",
                "DocumentHolder",
                "Toolbar",
                "Statusbar",
                "RightMenu",
                "LeftMenu",
                "Main",
                "Common.Controllers.Fonts",
                "Common.Controllers.History",
                "Common.Controllers.Chat",
                "Common.Controllers.Comments",
                "Common.Controllers.ExternalDiagramEditor"
              ];
              styles = [
                "css!documenteditor/main/resources/css/app.css"
              ];
              break;
            case 'presentation':
              sdkPath = 'PowerPoint';
              nameSpace = "PE";
              backboneControllers = [
                "Viewport",
                "DocumentHolder",
                "Toolbar",
                "Statusbar",
                "RightMenu",
                "LeftMenu",
                "Main",
                "Common.Controllers.Fonts",
                "Common.Controllers.Chat",
                "Common.Controllers.Comments",
                "Common.Controllers.ExternalDiagramEditor"
              ];
              styles = [
                "css!presentationeditor/main/resources/css/app.css"
              ];
              break;
          }

          Common.Gateway = g;
          require.config({
            baseUrl: "apps/",
            waitSeconds: 360,
            paths: {
              perfectscrollbar: "common/main/lib/mods/perfect-scrollbar",
              jmousewheel: "jquery.mousewheel",
              xregexp: "xregexp-all-min",
              allfonts: "../sdk/Common/AllFonts",
              sdk: "../sdk/" + sdkPath + "/sdk-all",
              core: "common/main/lib/core/application",
              notification: "common/main/lib/core/NotificationCenter",
              keymaster: "common/main/lib/core/keymaster",
              tip: "common/main/lib/util/Tip",
              analytics: "common/Analytics",
              locale: "common/locale",
              irregularstack: "common/IrregularStack"
            },
            shim: {
              underscore: {
                exports: "_"
              },
              backbone: {
                deps: ["underscore", "jquery"],
                exports: "Backbone"
              },
              bootstrap: {
                deps: ["jquery"]
              },
              perfectscrollbar: {
                deps: ["jmousewheel"]
              },
              notification: {
                deps: ["backbone"]
              },
              core: {
                deps: ["backbone", "notification", "irregularstack"]
              },
              sdk: {
                deps: [
                  "jquery",
                  "underscore",
                  "allfonts",
                  "xregexp"
                ]
              },
              analytics: {
                deps: ["jquery"]
              }
            }
          });
          require([
            "backbone",
            "bootstrap",
            "core",
            "locale"
          ].concat(styles), function (Backbone) {
            Backbone.history.start();
            var app = new Backbone.Application({
              nameSpace: nameSpace,
              autoCreate: false,
              controllers: backboneControllers
            });
            Common.Locale.apply();
            switch (documentType) {
              case 'spreadsheet':
                require([
                  "spreadsheeteditor/main/app/controller/Viewport",
                  "spreadsheeteditor/main/app/controller/DocumentHolder",
                  "spreadsheeteditor/main/app/controller/CellEditor",
                  "spreadsheeteditor/main/app/controller/Toolbar",
                  "spreadsheeteditor/main/app/controller/Statusbar",
                  "spreadsheeteditor/main/app/controller/RightMenu",
                  "spreadsheeteditor/main/app/controller/LeftMenu",
                  "spreadsheeteditor/main/app/controller/Main",
                  "spreadsheeteditor/main/app/controller/Print",
                  "spreadsheeteditor/main/app/view/ParagraphSettings",
                  "spreadsheeteditor/main/app/view/ImageSettings",
                  "spreadsheeteditor/main/app/view/ChartSettings",
                  "spreadsheeteditor/main/app/view/ShapeSettings",
                  "common/main/lib/util/utils",
                  "common/main/lib/controller/Fonts",
                  "common/main/lib/controller/Comments",
                  "common/main/lib/controller/Chat"
                ], function () {
                  app.start();
                });
                break;
              case 'text':
                require([
                  "documenteditor/main/app/controller/Viewport",
                  "documenteditor/main/app/controller/DocumentHolder",
                  "documenteditor/main/app/controller/Toolbar",
                  "documenteditor/main/app/controller/Statusbar",
                  "documenteditor/main/app/controller/RightMenu",
                  "documenteditor/main/app/controller/LeftMenu",
                  "documenteditor/main/app/controller/Main",
                  "documenteditor/main/app/view/ParagraphSettings",
                  "documenteditor/main/app/view/HeaderFooterSettings",
                  "documenteditor/main/app/view/ImageSettings",
                  "documenteditor/main/app/view/TableSettings",
                  "documenteditor/main/app/view/ShapeSettings",
                  "common/main/lib/util/utils",
                  "common/main/lib/controller/Fonts",
                  "common/main/lib/controller/History",
                  "common/main/lib/controller/Comments",
                  "common/main/lib/controller/Chat",
                  "documenteditor/main/app/view/ChartSettings",
                  "common/main/lib/controller/ExternalDiagramEditor"
                ], function () {
                  app.start();
                });
                break;
              case 'presentation':
                require([
                  "presentationeditor/main/app/controller/Viewport",
                  "presentationeditor/main/app/controller/DocumentHolder",
                  "presentationeditor/main/app/controller/Toolbar",
                  "presentationeditor/main/app/controller/Statusbar",
                  "presentationeditor/main/app/controller/RightMenu",
                  "presentationeditor/main/app/controller/LeftMenu",
                  "presentationeditor/main/app/controller/Main",
                  "presentationeditor/main/app/view/ParagraphSettings",
                  "presentationeditor/main/app/view/ImageSettings",
                  "presentationeditor/main/app/view/ShapeSettings",
                  "presentationeditor/main/app/view/SlideSettings",
                  "presentationeditor/main/app/view/TableSettings",
                  "common/main/lib/util/utils",
                  "common/main/lib/controller/Fonts",
                  "common/main/lib/controller/Comments",
                  "common/main/lib/controller/Chat",
                  "presentationeditor/main/app/view/ChartSettings",
                  "common/main/lib/controller/ExternalDiagramEditor"
                ], function () {
                  app.start();
                });
                break;
            }
          });
          return {};
        });
    })

    .declareMethod('getContent', function () {
      var g = this;
      g.props.save_defer = RSVP.defer();
      g.props.handlers.save();
      return g.props.save_defer.promise;
    });

}(rJS, RSVP, require));