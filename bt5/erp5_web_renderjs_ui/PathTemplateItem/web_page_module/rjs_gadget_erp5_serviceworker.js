/*jslint indent: 2*/
/*global self, caches, fetch, Promise, URL, location, Response*/
(function (self, caches, fetch, Promise, URL, location, Response) {
  "use strict";

  var prefix = location.toString() + '_',
    // CLIENT_CACHE_MAPPING_NAME must not start with `prefix`
    // else it may be used as a normal content cache.
    CLIENT_CACHE_MAPPING_NAME = '__erp5js_' + location.toString(),
    CACHE_NAME = prefix + '_0001',
    CACHE_MAP = {},
    // Files required to make this app work offline
    REQUIRED_FILES = [
      'favicon.ico',
      'font-awesome/font-awesome-webfont.eot',
      'font-awesome/font-awesome-webfont.woff',
      'font-awesome/font-awesome-webfont.woff2',
      'font-awesome/font-awesome-webfont.ttf',
      'font-awesome/font-awesome-webfont.svg',
      'gadget_erp5_worklist_empty.svg?format=svg',
      'erp5_launcher_nojqm.js',
      'gadget_erp5_nojqm.css',
      'gadget_erp5_configure_editor.html',
      'gadget_erp5_configure_editor.js',
      'gadget_erp5_editor_panel.html',
      'gadget_erp5_editor_panel.js',
      'gadget_erp5_field_checkbox.html',
      'gadget_erp5_field_checkbox.js',
      'gadget_erp5_field_datetime.html',
      'gadget_erp5_field_datetime.js',
      'gadget_erp5_field_editor.html',
      'gadget_erp5_field_editor.js',
      'gadget_erp5_field_email.html',
      'gadget_erp5_field_email.js',
      'gadget_erp5_field_file.html',
      'gadget_erp5_field_file.js',
      'gadget_erp5_field_float.html',
      'gadget_erp5_field_float.js',
      'gadget_erp5_field_formbox.html',
      'gadget_erp5_field_formbox.js',
      'gadget_erp5_field_gadget.html',
      'gadget_erp5_field_gadget.js',
      'gadget_erp5_field_image.html',
      'gadget_erp5_field_image.js',
      'gadget_erp5_field_integer.html',
      'gadget_erp5_field_integer.js',
      'gadget_erp5_field_list.html',
      'gadget_erp5_field_list.js',
      'gadget_erp5_field_lines.html',
      'gadget_erp5_field_lines.js',
      'gadget_erp5_field_listbox.html',
      'gadget_erp5_field_listbox.js',
      'gadget_erp5_field_matrixbox.html',
      'gadget_erp5_field_matrixbox.js',
      'gadget_erp5_field_multicheckbox.html',
      'gadget_erp5_field_multicheckbox.js',
      'gadget_erp5_field_multilist.html',
      'gadget_erp5_field_multilist.js',
      'gadget_erp5_field_multirelationstring.html',
      'gadget_erp5_field_multirelationstring.js',
      'gadget_erp5_field_radio.html',
      'gadget_erp5_field_radio.js',
      'gadget_erp5_field_readonly.html',
      'gadget_erp5_field_readonly.js',
      'gadget_erp5_field_relationstring.html',
      'gadget_erp5_field_relationstring.js',
      'gadget_erp5_field_string.html',
      'gadget_erp5_field_string.js',
      'gadget_erp5_field_password.html',
      'gadget_erp5_field_password.js',
      'gadget_erp5_field_textarea.html',
      'gadget_erp5_field_textarea.js',
      'gadget_erp5_form.html',
      'gadget_erp5_form.js',
      'gadget_erp5_header.html',
      'gadget_erp5_header.js',
      'gadget_erp5_jio.html',
      'gadget_erp5_jio.js',
      'gadget_erp5_label_field.html',
      'gadget_erp5_label_field.js',
      'gadget_erp5_notification.html',
      'gadget_erp5_notification.js',
      'gadget_erp5_page_action.html',
      'gadget_erp5_page_action.js',
      'gadget_erp5_page_export.html',
      'gadget_erp5_page_export.js',
      'gadget_erp5_page_form.html',
      'gadget_erp5_page_form.js',
      'gadget_erp5_page_front.html',
      'gadget_erp5_page_front.js',
      'gadget_erp5_page_history.html',
      'gadget_erp5_page_history.js',
      'gadget_erp5_page_jump.html',
      'gadget_erp5_page_jump.js',
      'gadget_erp5_page_language.html',
      'gadget_erp5_page_language.js',
      'gadget_erp5_page_logout.html',
      'gadget_erp5_page_logout.js',
      'gadget_erp5_page_preference.html',
      'gadget_erp5_page_preference.js',
      'gadget_erp5_page_relation_search.html',
      'gadget_erp5_page_relation_search.js',
      'gadget_erp5_page_search.html',
      'gadget_erp5_page_search.js',
      'gadget_erp5_page_tab.html',
      'gadget_erp5_page_tab.js',
      'gadget_erp5_page_worklist.html',
      'gadget_erp5_page_worklist.js',
      'gadget_erp5_panel.html',
      'gadget_erp5_panel.js',
      'gadget_erp5_panel.png?format=png',
      'gadget_erp5_pt_embedded_form_render.html',
      'gadget_erp5_pt_embedded_form_render.js',
      'gadget_erp5_pt_form_dialog.html',
      'gadget_erp5_pt_form_dialog.js',
      'gadget_erp5_pt_form_list.html',
      'gadget_erp5_pt_form_list.js',
      'gadget_erp5_pt_form_view.html',
      'gadget_erp5_pt_form_view.js',
      'gadget_erp5_pt_form_view_editable.html',
      'gadget_erp5_pt_form_view_editable.js',
      'gadget_erp5_pt_report_view.html',
      'gadget_erp5_pt_report_view.js',
      'gadget_erp5_router.html',
      'gadget_erp5_router.js',
      'gadget_erp5_relation_input.html',
      'gadget_erp5_relation_input.js',
      'gadget_erp5_search_editor.html',
      'gadget_erp5_search_editor.js',
      'gadget_erp5_searchfield.html',
      'gadget_erp5_searchfield.js',
      'gadget_erp5_sort_editor.html',
      'gadget_erp5_sort_editor.js',
      'gadget_global.js',
      'gadget_html5_element.html',
      'gadget_html5_element.js',
      'gadget_html5_input.html',
      'gadget_html5_input.js',
      'gadget_html5_textarea.html',
      'gadget_html5_textarea.js',
      'gadget_html5_select.html',
      'gadget_html5_select.js',
      'gadget_erp5_global.js',
      'gadget_jio.html',
      'gadget_jio.js',
      'gadget_translation.html',
      'gadget_translation.js',
      'gadget_translation_data.js',
      'gadget_editor.html',
      'gadget_editor.js',
      'gadget_button_maximize.html',
      'gadget_button_maximize.js',
      'handlebars.js',
      'jiodev.js',
      'renderjs.js',
      'rsvp.js',
      './'
    ],
    required_url_list = [],
    i,
    len = REQUIRED_FILES.length;

  for (i = 0; i < len; i += 1) {
    required_url_list.push(
      new URL(REQUIRED_FILES[i], location.toString()).toString()
    );
  }
  self.addEventListener('install', function (event) {
    // Perform install step:  loading each required file into cache
    event.waitUntil(
      // We create cache only if it does not exist. That is because
      // we do not want to override an existing cache by mistake.
      // Code consistency is very important. We must not mix different
      // versions of code.
      // (For example, developer change service worker code and forget
      // to increase the cache version.)
      caches.has(CACHE_NAME)
        .then(function (result) {
          if (!result) {
            caches.open(CACHE_NAME)
              .then(function (cache) {
                // Add all offline dependencies to the cache
                return Promise.all(
                  REQUIRED_FILES
                    .map(function (url) {
                      /* Return a promise that's fulfilled
                         when each url is cached.
                      */
                      // Use cache.add because safari does not support cache.addAll.
                      console.log("Install " + CACHE_NAME + " = " + url);
                      return cache.add(url);
                    })
                );
              })
              .then(function () {
                return caches.keys();
              })
              .then(function (keys) {
                keys = keys.filter(function (key) {return key.startsWith(prefix); });
                if (keys.length === 1) {
                  // When user accesses ERP5JS web site first time, service worker is
                  // installed but it is not activated yet, service worker is activated
                  // when the page is refreshed or when a new tab opens the site again.
                  // If user does not refresh the page and continue to use the site,
                  // user can't use cache, so everything becomes slow. We must avoid this
                  // situation.
                  // So, we want to activate the new service worker immediately if it was
                  // the first one. (We must not activate the new service worker by
                  // skipWaiting if there is already an active service worker because it
                  // causes code inconsistency by loading code from a different version of
                  // cache.
                  // If there is only one cache, it means that this is the first service worker,
                  // thus we can do skipWaiting. And self.registration is unreliable on
                  // Firefox, we can't use self.registration.active
                  return self.skipWaiting();
                }
              })
              .catch(function (error) {
                // Since we do not allow to override existing cache, if cache installation
                // failed, we need to delete the cache completely.
                caches.delete(CACHE_NAME);
                // Explicitly unregister service worker else it may not be done.
                self.registration.unregister();
                throw error;
              });
          }
        })
    );
  });

  self.addEventListener('fetch', function (event) {
    /* When a new service worker is installed, it adds a new Cache
       to Cache Storage. When a new client started using this
       service worker, the new client uses the latest Cache at
       that time by comparing with Cache keys. And once the client
       is associated with a Cache key, it keeps using the same Cache
       key, it must not use different Caches. Since service worker
       is stateless, to maintain the mapping of client and Cache key,
       we use Cache Storage as a persistent data store. The key of
       this special Cache is CLIENT_CACHE_MAPPING_NAME.
    */
    var url = new URL(event.request.url),
      client_id = event.clientId.toString(),
      // CACHE_MAP is a temprary data store.
      // This should be kept until service worker stops.
      CACHE_KEY = CACHE_MAP[client_id],
      ERP5JS_CACHE;
    url.hash = '';
    console.log("Client Id = " + client_id);

    if (CACHE_KEY) {
      console.log("CACHE_KEY from CACHE_MAP " + CACHE_KEY);
    }

    if (!client_id) {
      // If Client is not supported by web browser,
      // use the CACHE_NAME that is defined in this service worker.
      // It means that even if there is a new Cache, but web browser
      // uses the Cache that was installed by this service worker.
      CACHE_KEY = CACHE_NAME;
      CACHE_MAP[client_id] = CACHE_KEY;
      console.log("CACHE_KEY from Service Worker " + CACHE_KEY);
    }
    if ((event.request.method !== 'GET') ||
        (required_url_list.indexOf(url.toString()) === -1)) {
      // Try not to use the untrustable fetch function
      // It can only be skip synchronously
      return;
    }
    return event.respondWith(
      Promise.resolve()
        .then(function () {
          if (!CACHE_KEY) {
            // CLIENT_CACHE_MAPPING_NAME stores CACHE_KEY of each client.
            return caches.open(CLIENT_CACHE_MAPPING_NAME);
          }
        })
        .then(function (erp5js_cache) {
          if (erp5js_cache) {
            // Service worker forget everything when it stops. So, when it started
            // again, CACHE_MAP is empty, get the associated CACHE_KEY from the
            // special Cache named CLIENT_CACHE_MAPPING_NAME.
            ERP5JS_CACHE = erp5js_cache;
            return erp5js_cache.match(client_id);
          }
        })
        .then(function (response) {
          if (response) {
            // We use Cache Storage as a persistent database.
            CACHE_KEY = response.statusText;
            CACHE_MAP[client_id] = CACHE_KEY;
            console.log("CACHE_KEY from Cache Storage " + CACHE_KEY);
          }
        })
        .then(function () {
          if (CACHE_KEY) {
            return [];
          }
          // If associated CACHE_KEY is not found, it means this client is a new one.
          // Let's find the latest Cache.
          return caches.keys();
        })
        .then(function (keys) {
          if (!CACHE_KEY) {
            keys = keys.filter(function (key) {return key.startsWith(prefix); });
            console.log("KEYS = " + keys);
            if (keys.length) {
              CACHE_KEY = keys.sort().reverse()[0];
              CACHE_MAP[client_id] = CACHE_KEY;
            } else {
              CACHE_KEY = CACHE_NAME;
              CACHE_MAP[client_id] = CACHE_NAME;
            }
            // Save the associated CACHE_KEY in a persistent database because service
            // worker forget everything when it stops.
            ERP5JS_CACHE.put(client_id, new Response(null, {"statusText": CACHE_KEY}));
          }
        })
        .then(function () {
          // Finally we have the associated CACHE_KEY. Let's find a cached response.
          return caches.open(CACHE_KEY);
        })
        .then(function (cache) {
          // Don't give request object itself. Firefox's Cache Storage
          // does not work properly when VARY contains Accept-Language.
          // Give URL string instead, then cache.match works on both Firefox and Chrome.
          return cache.match(event.request.url);
        })
        .then(function (response) {
          // Cache hit - return the response from the cached version
          if (response) {
            return response;
          }
          // Not in cache - return the result from the live server
          // `fetch` is essentially a "fallback"
          console.log("MISS " + CACHE_KEY + " " + url);
          return fetch(event.request);
        })
    );
  });

  self.addEventListener("activate", function (event) {
    /* Just like with the install event, event.waitUntil blocks activate on a promise.
     Activation will fail unless the promise is fulfilled.
    */
    event.waitUntil(
      caches
        /* This method returns a promise which will resolve to an array of available
           cache keys.
        */
        .keys()
        .then(function (keys) {
          keys = keys
            .filter(function (key) {
              // Filter by keys that don't start with the latest version prefix.
              return key.startsWith(prefix);
            })
            .sort();
          keys = keys.slice(0, keys.findIndex(function (element) {return element === CACHE_NAME; }));
          // We return a promise that settles when all outdated caches are deleted.
          return Promise.all(
            keys
              .map(function (key) {
                /* Return a promise that's fulfilled
                   when each outdated cache is deleted.
                */
                return caches.delete(key);
              })
          );
        })
        .then(function () {
          // If new service worker becomes active, it means that all clients
          // (tabs, windows, etc) were already closed. Thus we can remove the
          // client cache mapping.
          caches.delete(CLIENT_CACHE_MAPPING_NAME);
        })
    );
  });

}(self, caches, fetch, Promise, URL, location, Response));