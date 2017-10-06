/*globals window, RSVP, rJS, loopEventListener, URL, document
  FileReader, console, navigator */
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, navigator, RSVP, rJS, jIO, URL) {
  "use strict";

  var origin_url = (window.location.origin + window.location.pathname).replace(
    "officejs_export/", ""),
    application_dict = {
    "Text Editor": {
      "url": "officejs_text_editor/",
      "cache": "gadget_officejs_text_editor.appcache",
      "sub_gadget": ["officejs_ckeditor_gadget", "officejs_setting_gadget"]
    },
    "Illustration Editor": {
      "url": "officejs_svg_editor/",
      "cache": "gadget_officejs_illustration.appcache",
      "sub_gadget": ["officejs_svg_editor_gadget", "officejs_setting_gadget"]
    },
    "PDF Viewer": {
      "url": "officejs_pdf_viewer/",
      "cache": "gadget_officejs_pdf_viewer.appcache",
      "sub_gadget": ["officejs_pdf_viewer_gadget", "officejs_setting_gadget"]
    },
    "Cribjs": {
      "url": "officejs_cribjs/",
      "cache": "gadget_officejs_crib.appcache",
      "sub_gadget": ["officejs_codemirror", "officejs_setting_gadget"]
    },
    "Bookmark Manager": {
      "url": "officejs_bookmark_manager/",
      "cache" : "gadget_officejs_bookmark_manager.appcache",
      "sub_gadget": ["officejs_setting_gadget"]
    },
    "Onlyoffice Text": {
      "url": "ooffice_text/",
      "cache": "gadget_ooffice_text.appcache",
      "sub_gadget": ["ooffice_text_gadget", "officejs_setting_gadget"]
    },
    "Onlyoffice Spreadsheet": {
      "url": "ooffice_spreadsheet/",
      "cache": "gadget_ooffice_spreadsheet.appcache",
      "sub_gadget": ["ooffice_spreadsheet_gadget", "officejs_setting_gadget"]
    },
    "Onlyoffice Presentation": {
      "url": "ooffice_presentation/",
      "cache": "gadget_ooffice_presentation.appcache",
      "sub_gadget": ["ooffice_presentation_gadget", "officejs_setting_gadget"]
    },
    "Web Table Editor": {
      "url": "officejs_web_table_editor/",
      "cache": "gadget_officejs_web_table.appcache",
      "sub_gadget": [
        "officejs_web_table_editor_gadget",
        "officejs_setting_gadget"
      ]
    },
    "Image Editor": {
      "url": "officejs_image_editor/",
      "cache": "gadget_officejs_image_editor.appcache",
      "sub_gadget": [
        "officejs_image_editor_gadget",
        "officejs_setting_gadget"
      ]
    },
    "Awesome Free Software Publisher List": {
      "url": "afs/",
      "cache": "gadget_erp5_afs.appcache",
      "no_installer": true,
      "sub_gadget": []
    },
    "Jabber Client": {
      "url": "jabber_client/",
      "cache": "gadget_jabberclient.appcache",
      "no_installer": true,
      "sub_gadget": ["connection"]
    },
    "Monitoring App": {
      "url": "monitoring_render_js/",
      "cache" : "gadget_monitoring.appcache",
      "sub_gadget": []
    },
    "App Store": {
      "url": "officejsoldv1/",
      "cache": "officejs_store.appcache",
      "no_installer": true,
      "sub_gadget": []
    },
    "MediaPlayer": {
      "url": "officejs_audioplayer/",
      "cache": "gadget_officejs_audioplayer.appcache",
      "no_installer": true,
      "sub_gadget": []
    },
    "Trade Application": {
      "url": "osp-9/",
      "cache": "gadget_trade_application.appcache",
      "no_installer": true,
      "sub_gadget": []
    },
    "Todomvc": {
      "url": "officejs_todomvc/",
      "cache": "officejs_todomvc.appcache",
      "no_installer": true,
      "sub_gadget": []
    },
    "connection": {
      "cache": "gadget_jabberconnection.appcache",
      "no_installer": true
    },
    "officejs_ckeditor_gadget": {
      "cache": "gadget_ckeditor.appcache"
    },
    "officejs_setting_gadget": {
      "cache": "gadget_officejs_setting.appcache"
    },
    "officejs_svg_editor_gadget": {
      "cache": "gadget_officejs_svg_editor.appcache"
    },
    "officejs_pdf_viewer_gadget": {
      "cache": "gadget_officejs_pdf_viewer_gadget.appcache"
    },
    "officejs_codemirror": {
      "cache": "gadget_officejs_codemirror.appcache"
    },
    "ooffice_text_gadget": {
      "cache": "gadget_ooffice_text_gadget.appcache"
    },
    "ooffice_spreadsheet_gadget": {
      "cache": "gadget_ooffice_spreadsheet_gadget.appcache"
    },
    "ooffice_presentation_gadget": {
      "cache": "gadget_ooffice_presentation_gadget.appcache"
    },
    "officejs_web_table_editor_gadget": {
      "cache": "gadget_officejs_web_table_editor.appcache"
    },
    "officejs_image_editor_gadget": {
      "cache": "gadget_officejs_image_editor_gadget.appcache"
    }
  };

  function exportZip(gadget, event) {
    var j,
      zip_name,
      i = 0,
      form_result = {},
      len = event.target.length,
      app;

    for (j = 0; j < len; j += 1) {
      form_result[event.target[j].name] = event.target[j].value;
    }
    app = application_dict[form_result.web_site];
    zip_name = form_result.filename;
    len = app.sub_gadget.length;

    function fill(zip_file) {
      if (i < len) {
        var sub_app = app.sub_gadget[i];
        return gadget.fillZip(
          application_dict[sub_app].cache,
          origin_url + app.url,
          application_dict[sub_app].no_installer,
          zip_file,
          sub_app + "/"
        )
          .push(function (zip_file) {
            i += 1;
            return fill(zip_file);
          });
      }
      return zip_file;
    }

    return gadget.fillZip(app.cache, origin_url + app.url, app.no_installer)
      .push(function (zip_file) {
        return fill(zip_file);
      })
      .push(function (zip_file) {
        var element = gadget.props.element,
          a = document.createElement("a"),
          url = URL.createObjectURL(zip_file),
          default_name = form_result.web_site.toLocaleLowerCase()
            .replace(' ', '_');
        element.appendChild(a);
        a.style = "display: none";
        a.href = url;
        a.download = zip_name ? zip_name : default_name + ".zip";
        a.click();
        element.removeChild(a);
        URL.revokeObjectURL(url);
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
    .declareMethod("fillZip", function (cache_file, site_url, no_installer,
                                         zip_file, prefix) {
      var gadget = this,
        file_storage = jIO.createJIO({
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
            prefix: prefix || ""
          }
        },
        signature_sub_storage: {
          type: "query",
          sub_storage: {
            type: "memory"
          }
        },
        local_sub_storage: {
          type: "zipfile",
          file: zip_file
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
            gadget.props.element.querySelector('form.export-form'),
            'submit',
            true,
            function (event) {
              return exportZip(gadget, event);
            }
          );
        });
    });

}(window, navigator, RSVP, rJS, jIO, URL));
