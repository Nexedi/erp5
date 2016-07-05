/*global window, rJS, jIO, URI, location, console, document, RSVP, loopEventListener, navigator */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS) {
  "use strict";

  var gadget_klass = rJS(window),
    NAME = "text",
    MAIN_PAGE_PREFIX = "gadget_officejs_",
    DEFAULT_PAGE = NAME + "_list",
    REDIRECT_TIMEOUT = 5000;

  (function () {
    var erp5_query,
      jio_erp5_cache_storage;
    if ('serviceWorker' in navigator) {
      erp5_query = [
        "ooffice/gadget_ooffice.js",
        "ooffice/gadget_ooffice.html",
        "ooffice/apps/require.js",
        "ooffice/apps/css.js",
        "ooffice/apps/underscore.js",
        "ooffice/apps/backbone.js",
        "ooffice/apps/bootstrap.js",
        "ooffice/apps/text.js",
        "ooffice/apps/xregexp-all-min.js",
        "ooffice/apps/jquery.mousewheel.js",
        "ooffice/apps/common/%",
        "ooffice/apps/documenteditor/main/%",
        "ooffice/sdk/Common/%",
        "ooffice/sdk/Word/%"
      ].map(function (currentValue) {
        return 'url_string: "' + currentValue + '"';
      }).join(' OR ');
      erp5_query = '(' + erp5_query + ' OR ' + [
        "gadget_officejs_text_router.html",
        "gadget_officejs_text_router.js",
        "gadget_officejs_text_application_panel.html",
        "gadget_officejs_page_text_list.html",
        "gadget_officejs_page_text_list.js",
        "gadget_officejs_jio_text_view.html",
        "gadget_officejs_jio_spreadsheet_view.js",
        "gadget_officejs_page_add_text.html",
        "gadget_officejs_page_add_text.js",
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
        "gadget_officejs_page_add_text_document.html",
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
        "gadget_officejs_page_add_text_document.js",
        "gadget_officejs_page_jio_configurator.js",
        "gadget_officejs_page_jio_dav_configurator.js",
        "gadget_officejs_page_login.js",
        "gadget_officejs_page_logout.js",
        "gadget_officejs_page_share_webrtc_jio.js",
        "gadget_officejs_page_sync.js",
        "gadget_officejs_text_editor_application_panel.js",
        "gadget_translation.js",
        "gadget_translation_data.js",
        "gadget_officejs_webrtc_jio.js",
        "gadget_officejs_widget_listbox.js",
        "erp5_launcher.js",
        "erp5_launcher.html"
      ].map(function (currentValue) {
        return '(reference: ="' + currentValue + '")';
      }).join(' OR ') + ')';

      jio_erp5_cache_storage = {
        type: "query",
        sub_storage: {
          type: "uuid",
          sub_storage: {
            type: "indexeddb",
            database: 'officejs_' + NAME + '_cache_erp5'
          }
        }
      };

      jio_erp5_cache_storage = jIO.createJIO({
        type: "replicate",
        query: {
          query: '(portal_type: ("Web Style", "Web Page", "Web Script")) AND ' +
            erp5_query,
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
        local_sub_storage: {
          type: "attachasproperty",
          map: {
            text_content: "text_content",
            data: "data"
          },
          sub_storage: jio_erp5_cache_storage
        },
        remote_sub_storage: {
          type: "erp5",
          url: (new URI("hateoasnoauth"))
            .absoluteTo(location.href)
            .toString(),
          default_view_reference: "jio_view"
        }
      });

      jio_erp5_cache_storage.repair().push(function () {
        navigator.serviceWorker.register('gadget_officejs_' + NAME + '_serviceworker.js')
          .then(function (reg) {
            // registration worked
            console.log('Registration succeeded. Scope is ' + reg.scope);
          })
          .then(undefined, function (error) {
            // registration failed
            console.log('Registration failed with ' + error);
          });
      }, console.log);

    }
  }());

  function listenHashChange(gadget) {
    function extractHashAndDispatch(evt) {
      var hash = (evt.newURL || window.location.toString()).split('#')[1],
        subhashes,
        subhash,
        keyvalue,
        index,
        args = {};
      if (hash !== undefined) {
        subhashes = hash.split('&');
        for (index in subhashes) {
          if (subhashes.hasOwnProperty(index)) {
            subhash = subhashes[index];
            if (subhash !== '') {
              keyvalue = subhash.split('=');
              if (keyvalue.length === 2) {
                args[decodeURIComponent(keyvalue[0])] = decodeURIComponent(keyvalue[1]);
              }
            }
          }
        }
      }

      return gadget.renderApplication({
        args: args
      });

    }

    var result = loopEventListener(window, 'hashchange', false,
      extractHashAndDispatch),
      event = document.createEvent("Event");
    event.initEvent('hashchange', true, true);
    event.newURL = window.location.toString();
    window.dispatchEvent(event);
    return result;
  }

  gadget_klass

    .ready(function (gadget) {
      gadget.props = {
        start_deferred: RSVP.defer()
      };
    })

    .declareMethod("getCommandUrlFor", function (options) {
      var prefix = '',
        result,
        key;
      result = "#";
      for (key in options) {
        if (options.hasOwnProperty(key) && options[key] !== undefined) {
          // Don't keep empty values
          result += prefix + encodeURIComponent(key) + "=" + encodeURIComponent(options[key]);
          prefix = '&';
        }
      }
      return result;
    })

    .declareMethod('redirect', function (options) {
      return this.getCommandUrlFor(options)
        .push(function (hash) {
          window.location.replace(hash);
          // prevent returning unexpected response
          // wait for the hash change to occur
          // fail if nothing happens
          return RSVP.timeout(REDIRECT_TIMEOUT);
        });
    })

    .declareMethod('route', function (options) {
      var gadget = this,
        args = options.args;
      gadget.options = options;
      if (args.jio_key === undefined || args.jio_key === '') {
        if (args.page === undefined || args.page === '' || args.page === "document_list") {
          args.page = DEFAULT_PAGE;
        }
        return {
          url: MAIN_PAGE_PREFIX + "page_" + args.page + ".html",
          options: args
        };
      }
      return gadget.jio_get(args.jio_key)
        .push(function (doc) {
          var sub_options = {},
            base_portal_type = doc.portal_type.toLowerCase().replace(/\s/g, "_");
          sub_options = {
            doc: doc,
            jio_key: args.jio_key,
            search: args.search
          };
          if (base_portal_type.search(/_temp$/) >= 0) {
            //Remove "_temp"
            base_portal_type = base_portal_type.substr(
              0,
              base_portal_type.length - 5
            );
          }
          return {
            url: MAIN_PAGE_PREFIX + "jio_"
              + base_portal_type
              + "_" + args.page + ".html",
            options: sub_options
          };
        });
    })

    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('renderApplication', 'renderApplication')
    .declareMethod('start', function () {
      this.props.start_deferred.resolve();
    })
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.start_deferred.promise;
        })
        .push(function () {
          return listenHashChange(gadget);
        });
    });

}(window, rJS));