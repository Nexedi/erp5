/*global window, rJS, jIO, URI, location, console, document, RSVP, loopEventListener, navigator, XMLHttpRequest, ProgressEvent*/
/*jslint nomen: true, indent: 2*/
(function (window, rJS, jIO) {
  "use strict";

  function this_func_link(name) {
    return function (opt) {
      return this[name].apply(this, opt);
    };
  }

  var gadget_klass = rJS(window),
    SCOPE = "main",
    SETTING_STORAGE = jIO.createJIO({
      type: "indexeddb",
      database: "setting"
    });

  function get_jio_cache_storage(name) {
    return {
      type: "uuid",
      sub_storage: {
        type: "indexeddb",
        database: 'officejs_' + name + '_cache_erp5'
      }
    };
  }

  function get_jio_replicate_storage(name, modification_date) {
    var erp5_query,
      sdk_name;
    erp5_query = [
      "ooffice/apps/common/%",
      "ooffice/vendor/%",
      "ooffice/sdkjs/common/%"
    ];
    switch (name) {
    case "spreadsheet":
      sdk_name = "cell";
      erp5_query.push("ooffice/apps/" + name + "editor/main/%");
      erp5_query.push("ooffice/sdkjs/word/%");
      break;
    case "text":
      sdk_name = "word";
      erp5_query.push("ooffice/apps/documenteditor/main/%");
      erp5_query.push("ooffice/sdkjs/cell/model/%");
      erp5_query.push("ooffice/sdkjs/cell/utils/%");
      break;
    case "presentation":
      sdk_name = "slide";
      erp5_query.push("ooffice/apps/" + name + "editor/main/%");
      erp5_query.push("ooffice/sdkjs/word/%");
      erp5_query.push("ooffice/sdkjs/cell/%");
      break;
    }
    erp5_query.push("ooffice/sdkjs/" + sdk_name + "/%");

    erp5_query = erp5_query.map(function (currentValue) {
      return 'url_string: "' + currentValue + '"';
    }).join(' OR ');
    erp5_query = erp5_query + ' OR ' + [
      "ooffice/gadget_ooffice.js",
      "ooffice/gadget_ooffice.html",
      "ooffice/apps/require.js",
      "ooffice/apps/css.js",
      "ooffice/apps/underscore.js",
      "ooffice/apps/backbone.js",
      "ooffice/apps/bootstrap.js",
      "ooffice/apps/text.js",
      "ooffice/apps/xregexp-all-min.js",
      "ooffice/apps/jquery.mousewheel.js"
    ].map(function (currentValue) {
      return 'url_string: ="' + currentValue + '"';
    }).join(' OR ');
    erp5_query = erp5_query + ' OR ' + [
      "gadget_officejs_" + name + "_router.html",
      "gadget_officejs_router.js",
      "gadget_officejs_page_document_list.html",
      "gadget_officejs_page_document_list.js",
      "gadget_officejs_jio_" + name + "_view.html",
      "gadget_officejs_jio_onlyoffice_view.js",
      "gadget_officejs_page_add_document.html",
      "gadget_officejs_page_add_document.js",
      "gadget_erp5_editor_panel.html",
      "gadget_erp5_editor_panel.js",
      "URI.js",
      "dygraph.js",
      "gadget_erp5.css",
      "gadget_global.js",
      "gadget_jio.html",
      "gadget_jio.js",
      "gadget_translate.html",
      "gadget_translate.js",
      "i18next.js",
      "jiodev.js",
      "jquery.js",
      "jquerymobile.css",
      "jquerymobile.js",
      "renderjs.js",
      "rsvp.js",
      "gadget_officejs_header.html",
      "gadget_officejs_jio.html",
      "gadget_officejs_page_add_document.html",
      "gadget_officejs_page_jio_configurator.html",
      "gadget_officejs_page_jio_dav_configurator.html",
      "gadget_officejs_page_login.html",
      "gadget_officejs_page_logout.html",
      "gadget_officejs_page_share_webrtc_jio.html",
      "gadget_officejs_page_sync.html",
      "gadget_translation.html",
      "gadget_officejs_webrtc_jio.html",
      "gadget_officejs_widget_listbox.html",
      "gadget_officejs_header.js",
      "gadget_officejs_jio.js",
      "gadget_officejs_page_add_document.js",
      "gadget_officejs_page_jio_configurator.js",
      "gadget_officejs_page_jio_dav_configurator.js",
      "gadget_officejs_page_login.js",
      "gadget_officejs_page_logout.js",
      "gadget_officejs_page_share_webrtc_jio.js",
      "gadget_officejs_page_sync.js",
      "gadget_officejs_application_panel.html",
      "gadget_officejs_application_panel.js",
      "gadget_translation.js",
      "gadget_translation_data.js",
      "gadget_officejs_webrtc_jio.js",
      "gadget_officejs_widget_listbox.js",
      "erp5_launcher.js",
      "erp5_launcher.html"
    ].map(function (currentValue) {
      return '(reference: ="' + currentValue + '")';
    }).join(' OR ');

    erp5_query = "(" + erp5_query + ")";

    if (modification_date) {
      modification_date = ' AND modification_date:>="'
        + modification_date + '" ';
    } else {
      modification_date = "";
    }

    return jIO.createJIO({
      type: "replicate",
      query: {
        query: 'reference: "%" AND (portal_type: ("Web Style", "Web Page", "Web Script")) AND ' +
          erp5_query + modification_date,
        select_list: ["url_string"],
        limit: [0, 1234567890]
      },
      use_remote_post: true,
      conflict_handling: 2,
      check_local_modification: false,
      check_local_creation: false,
      check_local_deletion: false,
      check_remote_modification: true,
      check_remote_creation: true,
      check_remote_deletion: true,
      use_bulk_get: true,
      use_bulk: true,
      attachment_list: [],
      signature_storage: get_jio_cache_storage(name + "_hash"),
      local_sub_storage: {
        type: "mapping",
        map_all_property: true,
        map_id: ["equalSubProperty", "relative_url"],
        mapping_dict: {
          "url_string": ["equalSubId"]
        },
        sub_storage: {
          type: "query",
          sub_storage: get_jio_cache_storage(name)
        }
      },
      remote_sub_storage: {
        type: "erp5",
        url: (new URI("hateoasnoauth"))
          .absoluteTo(location.href)
          .toString(),
        default_view_reference: "jio_view"
      }
    });
  }




  gadget_klass

    .ready(function (gadget) {
      gadget.props = {};
      return gadget.getElement()
        .push(function (element) {
          var element_list =
              element.querySelectorAll("[data-renderjs-configuration]"),
            len = element_list.length,
            key,
            value,
            i;
          gadget.props.element = element;
          gadget.props.configuration = {};
          for (i = 0; i < len; i += 1) {
            key = element_list[i].getAttribute('data-renderjs-configuration');
            value = element_list[i].textContent;
            gadget.props.configuration[key] = value;
          }
        })
        .push(function () {
          var NAME = gadget.props.configuration.portal_type.toLowerCase(),
            jio_store;
          if (navigator.serviceWorker !== undefined) {
            return new RSVP.Queue()
              .push(function () {
                return RSVP.all([
                  gadget.getSetting('jio_' + NAME + '_modification_date'),
                  gadget.getSetting('jio_' + NAME + '_cache_description')
                ]);
              })
              .push(function (result) {
                var modification_date = result[0],
                  query = result[1],
                  queue;
                jio_store = get_jio_replicate_storage(NAME);
                if (jio_store.__storage._query_options.query === query && modification_date) {
                  queue = get_jio_replicate_storage(NAME, modification_date).repair();
                } else {
                  queue = jio_store.repair();
                }
                return queue;
              })
              .push(undefined, function (error) {
                // fix offline mode bypass network errors
                if (!(error instanceof ProgressEvent &&
                  error.srcElement instanceof XMLHttpRequest &&
                  error.type === "error")) {
                  throw error;
                }
              })
              .push(function () {
                gadget.setSetting(
                  'jio_' + NAME + '_cache_description',
                  jio_store.__storage._query_options.query
                );
                jIO.createJIO(get_jio_cache_storage(NAME)).allDocs({
                  query: '',
                  sort_on: [
                    ['modification_date', 'descending']
                  ],
                  limit: [0, 1],
                  select_list: ['modification_date']
                })
                  .push(function (data) {
                    if (data.data.total_rows === 1) {
                      return gadget.setSetting('jio_' + NAME + '_modification_date',
                        data.data.rows[0].value.modification_date);
                    }
                  });
                return new RSVP.Promise(function (resolve, reject) {
                  console.log("Will register SW");
                  navigator.serviceWorker.register('gadget_officejs_' + NAME + '_serviceworker.js')
                    .then(function (reg) {
                      // registration worked
                      console.log('Registration succeeded. Scope is ' + reg.scope);
                      resolve();
                    })
                    .then(undefined, reject);
                });
              });
          }
          throw "Your browser do not support service workers";
        })
        .push(function () {
          // Resources are now ready
          // Modify base to provides same base as gadget
          var base = document.createElement('base'),
            child_gadget_url = gadget.props.configuration["child-gadget"];
          base.href = new URI(child_gadget_url + '/../').normalize()
            .toString();
          document.head.appendChild(base);
          return gadget.declareGadget(
            child_gadget_url,
            {
              scope: SCOPE
            }
          );
        })
        .push(function (child_gadget) {
          return child_gadget.getElement();
        })
        .push(function (child_element) {
          gadget.props.element.appendChild(child_element);
        });
    })
    .declareMethod('getSetting', function (key, default_value) {
      var from_html = this.props.configuration[key];
      if (from_html) {
        return from_html;
      }
      return SETTING_STORAGE.get("setting")
        .push(function (doc) {
          return doc[key] || default_value;
        }, function (error) {
          if (error.status_code === 404) {
            return default_value;
          }
          throw error;
        });
    })
    .allowPublicAcquisition('getSetting', this_func_link('getSetting'))
    .declareMethod('setSetting', function (key, value) {
      return SETTING_STORAGE.get("setting")
        .push(undefined, function (error) {
          if (error.status_code === 404) {
            return {};
          }
          throw error;
        })
        .push(function (doc) {
          doc[key] = value;
          return SETTING_STORAGE.put('setting', doc);
        });
    })
    .allowPublicAcquisition('setSetting', this_func_link('setSetting'))
    .declareAcquiredMethod("triggerSubmit", "triggerSubmit")
    .allowPublicAcquisition('triggerSubmit', this_func_link('triggerMaximize'))
    .declareAcquiredMethod("triggerMaximize", "triggerMaximize")
    .allowPublicAcquisition('triggerMaximize', this_func_link('triggerMaximize'))
    .declareAcquiredMethod("setFillStyle", "setFillStyle")
    .allowPublicAcquisition('setFillStyle', this_func_link('setFillStyle'))
    .declareMethod('render', function (options) {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget(SCOPE);
        })
        .push(function (child_gadget) {
          return child_gadget.render(options);
        });
    })
    .declareMethod('getContent', function () {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget(SCOPE);
        })
        .push(function (child_gadget) {
          return child_gadget.getContent();
        });
    });

}(window, rJS, jIO));