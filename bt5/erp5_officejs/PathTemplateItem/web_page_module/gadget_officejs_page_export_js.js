/*globals window, RSVP, rJS, jIO, loopEventListener, URL, document */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */

(function (window, RSVP, rJS, jIO, URL) {
  "use strict";

  var origin_url = (window.location.origin + window.location.pathname)
    .replace("officejs_export/", ""),
    application_dict = {
      "Text Editor": {
        "url": "officejs_text_editor/",
        "cache": "gadget_officejs_text_editor.appcache"
      },
      "Smart Assistant": {
        "url": "officejs_smart_assistant/",
        "cache": "gadget_smart_assistant.appcache"
      },
      "Media Player": {
        "url": "officejs_media_player/",
        "cache": "gadget_officejs_media_player.appcache"
      },
      "Notebook": {
        "url": "officejs_notebook/",
        "cache": "gadget_officejs_notebook.appcache"
      },
      "Illustration Editor": {
        "url": "officejs_svg_editor/",
        "cache": "gadget_officejs_illustration.appcache"
      },
      "PDF Viewer": {
        "url": "officejs_pdf_viewer/",
        "cache": "gadget_officejs_pdf_viewer.appcache"
      },
      "Cribjs": {
        "url": "officejs_cribjs/",
        "cache": "gadget_officejs_crib.appcache"
      },
      "Bookmark Manager": {
        "url": "officejs_bookmark_manager/",
        "cache" : "gadget_officejs_bookmark_manager.appcache"
      },
      "Onlyoffice Text": {
        "url": "ooffice_text/",
        "cache": "gadget_ooffice_text.appcache"
      },
      "Onlyoffice Spreadsheet": {
        "url": "ooffice_spreadsheet/",
        "cache": "gadget_ooffice_spreadsheet.appcache"
      },
      "Onlyoffice Presentation": {
        "url": "ooffice_presentation/",
        "cache": "gadget_ooffice_presentation.appcache"
      },
      "Web Table Editor": {
        "url": "officejs_web_table_editor/",
        "cache": "gadget_officejs_web_table.appcache"
      },
      "Image Editor": {
        "url": "officejs_image_editor/",
        "cache": "gadget_officejs_image_editor.appcache"
      },
      "Awesome Free Software Publisher List": {
        "url": "afs/",
        "cache": "gadget_erp5_afs.appcache",
        "no_installer": true
      },
      "Jabber Client": {
        "url": "jabber_client/",
        "cache": "gadget_jabberclient.appcache",
        "no_installer": true
      },
      "Monitoring App": {
        "url": "officejs_monitoring/",
        "cache" : "gadget_officejs_monitoring.appcache"
      },
      "App Store": {
        "url": "officejs_appstore/",
        "cache": "officejs_store.appcache",
        "no_installer": true
      },
      "MediaPlayer": {
        "url": "officejs_audioplayer/",
        "cache": "gadget_officejs_audioplayer.appcache",
        "no_installer": true
      },
      "Trade Application": {
        "url": "osp-9/",
        "cache": "gadget_trade_application.appcache",
        "no_installer": true
      },
      "Todomvc": {
        "url": "officejs_todomvc/",
        "cache": "officejs_todomvc.appcache",
        "no_installer": true
      },
      "Wall Search": {
        "url": "officejs_wallsearch/",
        "cache": "gadget_erp5_page_ojs_wallsearch.appcache"
      },
      "Drive App": {
        "url": "officejs_drive_app/",
        "cache": "gadget_officejs_drive_app.appcache"
      },
      "Travel Expense": {
        "url": "officejs_hr/",
        "cache": "gadget_officejs_hr.appcache",
        "no_installer": true
      }
    };

  function exportZip(gadget, event) {
    var j,
      zip_name,
      form_result = {},
      len = event.target.length,
      app;

    for (j = 0; j < len; j += 1) {
      form_result[event.target[j].name] = event.target[j].value;
    }
    app = application_dict[form_result.web_site];
    zip_name = form_result.filename;

    return gadget.fillZip(app.cache, origin_url + app.url, app.no_installer)
      .push(function (zip_file) {
        var element = gadget.element,
          a = document.createElement("a"),
          url = URL.createObjectURL(zip_file),
          default_name = form_result.web_site.toLocaleLowerCase()
            .replace(' ', '_');
        element.appendChild(a);
        a.style = "display: none";
        a.href = url;
        a.download = zip_name || default_name + ".zip";
        a.click();
        element.removeChild(a);
        URL.revokeObjectURL(url);
      });
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })
    .declareMethod("fillZip", function (cache_file, site_url, no_installer) {
      var file_storage = jIO.createJIO({
          type: "replicate",
          conflict_handling: 2,
          check_remote_attachment_creation: true,
          check_local_creation: false,
          check_local_modification: false,
          check_local_deletion: false,
          check_remote_deletion: false,
          check_remote_modification: false,
          remote_sub_storage: {
            type: "filesystem",
            document: site_url,
            sub_storage: {
              type: "appcache",
              take_installer: no_installer === undefined,
              manifest: cache_file,
              origin_url: site_url,
              prefix: './'
            }
          },
          signature_sub_storage: {
            type: "query",
            sub_storage: {
              type: "memory"
            }
          },
          local_sub_storage: {
            type: "zipfile"
          }
        });
      return file_storage.repair()
        .push(function () {
          return file_storage.getAttachment('/', '/');
        });
    })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return loopEventListener(
            gadget.element.querySelector('form.export-form'),
            'submit',
            true,
            function (event) {
              return exportZip(gadget, event);
            }
          );
        });
    });

}(window, RSVP, rJS, jIO, URL));
