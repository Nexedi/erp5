/*global window, rJS, jIO, URI, location, console, document, RSVP, loopEventListener, navigator */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS) {
  "use strict";

  var gadget_klass = rJS(window),
    NAME,
    MAIN_PAGE_PREFIX = "gadget_officejs_",
    DEFAULT_PAGE = "document_list",
    REDIRECT_TIMEOUT = 5000;

  function get_jio_cache_storage(name) {
    return {
      type: "query",
      sub_storage: {
        type: "uuid",
        sub_storage: {
          type: "indexeddb",
          database: 'officejs_' + name + '_cache_erp5'
        }
      }
    };
  }

  function get_jio_replicate_storage(name, modification_date) {
    var erp5_query,
      sdk_name;


    if (modification_date) {
      modification_date = ' AND modification_date:>="'
        + modification_date + '" ';
    } else {
      modification_date = "";
    }

    return jIO.createJIO({
      type: "replicate",
      query: {
        query: '(portal_type: ("Web Style", "Web Page", "Web Script"))' + modification_date,
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
      use_bulk: false,
      local_sub_storage: get_jio_cache_storage(name),
      remote_sub_storage: {
        type: "mapping",
        sub_storage: {
          type: "erp5",
          url: (new URI("hateoasnoauth"))
            .absoluteTo(location.href)
            .toString(),
          default_view_reference: "jio_view"
        },
        query: {"query": 'version: OSP-5-dev'},
        mapping_dict: {"id": {"equal": "reference"}},
        map_all_property: true
      }
    });
  }

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
      return gadget.getElement()
        .push(function (element) {
          gadget.props.element = element;
        });
    })

    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('setSetting', 'setSetting')
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
      if (options !== undefined && options.toExternal) {
        window.location.replace(options.url);
        return RSVP.timeout(REDIRECT_TIMEOUT); // timeout if not redirected
      }
      else {
        return this.getCommandUrlFor(options)
          .push(function (hash) {
            window.location.replace(hash);
            // prevent returning unexpected response
            // wait for the hash change to occur
            // fail if nothing happens
            return RSVP.timeout(REDIRECT_TIMEOUT);
          });
      }
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
      var gadget = this,
        element_list =
          gadget.props.element.querySelectorAll("[data-renderjs-configuration]"),
        len = element_list.length,
        key,
        value,
        i,
        queue = new RSVP.Queue();

      function push(a, b) {
        queue.push(function () {
          if (a == "portal_type") {
            NAME = b.toLowerCase();
          }
          return gadget.setSetting(a, b);
        });
      }

      for (i = 0; i < len; i += 1) {
        key = element_list[i].getAttribute('data-renderjs-configuration');
        value = element_list[i].textContent;
        push(key, value);
      }
      this.props.start_deferred.resolve();
    })
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.start_deferred.promise;
        })
        .push(function () {
          if (('serviceWorker' in navigator) && (NAME != "web page")) {
            return jIO.createJIO(get_jio_cache_storage(NAME)).allDocs({
                query: '',
                sort_on: [
                  ['modification_date', 'descending']
                ],
                limit: [0, 1],
                select_list: ['modification_date']
              })
              .push(function (data) {
                var modification_date,
                  jio_store;
                if (data.data.total_rows == 1) {
                  modification_date = data.data.rows[0].value.modification_date;
                }
                jio_store = get_jio_replicate_storage(NAME);
                return gadget.getSetting('jio_' + NAME + '_cache_description')
                  .push(function (query) {
                    if (jio_store.__storage._query_options.query == query) {
                      return get_jio_replicate_storage(NAME, modification_date).repair();
                    } else {
                      return gadget.setSetting(
                          'jio_' + NAME + '_cache_description', jio_store.__storage._query_options.query
                        )
                        .push(function () {
                          return jio_store.repair();
                        });
                    }
                  })
                  .push(undefined, function (error) {
                    // fix offline mode bypass network errors
                    if (error instanceof ProgressEvent &&
                        error.srcElement instanceof XMLHttpRequest &&
                        error.type === "error") {
                      return {};
                    } else {
                      throw error;
                    }
                  })
                  .push(function () {
                    navigator.serviceWorker.register('gadget_officejs_' + NAME + '_serviceworker.js')
                      .then(function (reg) {
                        // registration worked
                        console.log('Registration succeeded. Scope is ' + reg.scope);
                      })
                      .then(undefined, function (error) {
                        // registration failed
                        console.log('Registration failed with ' + error);
                      });
                    return {}
                  });
              });
          } else {
            return {};
          }
        })
        .push(function () {
          return listenHashChange(gadget);
        });
    });

}(window, rJS));