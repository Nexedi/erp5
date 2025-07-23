/*jslint indent: 2*/
/*global self, caches, fetch*/
(function (self, caches, fetch) {
  "use strict";

  var CACHE_NAME = 'Thu, 12 July 2016 12:00:02 GMT',
    // Files required to make this app work offline
    REQUIRED_FILES = [
      './',
      'gadget_erp5_nojqm.css',
      'erp5_launcher_nojqm.js',
      'gadget_jio.html',
      'gadget_erp5_router.html',
      'gadget_erp5_header.html',
      'gadget_erp5_notification.html',
      'gadget_erp5_custom_jio.html',
      'gadget_translation.html',
      'gadget_erp5_editor_panel.html',
      'gadget_erp5_panel.html',
      'jiodev.js',
      'rsvp.js',
      'renderjs.js',
      'gadget_jio.js',
      'handlebars.js',
      'gadget_global.js',
      'gadget_erp5_router.js',
      'gadget_erp5_notification.js',
      'gadget_translation_data.js',
      'gadget_erp5_header.js',
      'gadget_erp5_custom_jio.js',
      'gadget_erp5_editor_panel.js',
      'URI.js',
      'erp5_launcher.js',
      'gadget_erp5.css',
      'gadget_erp5_editor_panel.html',
      'gadget_erp5_editor_panel.js',
      'gadget_erp5_field_checkbox.html',
      'gadget_erp5_field_checkbox.js',
      'gadget_erp5_field_datetime.html',
      'gadget_erp5_field_datetime.js',
      'gadget_erp5_field_email.html',
      'gadget_erp5_field_email.js',
      'gadget_erp5_field_file.html',
      'gadget_erp5_field_file.js',
      'gadget_erp5_field_float.html',
      'gadget_erp5_field_float.js',
      'gadget_erp5_field_gadget.html',
      'gadget_erp5_field_gadget.js',
      'gadget_erp5_field_image.html',
      'gadget_erp5_field_image.js',
      'gadget_erp5_field_integer.html',
      'gadget_erp5_field_integer.js',
      'gadget_erp5_field_list.html',
      'gadget_erp5_field_list.js',
      'gadget_erp5_field_listbox.html',
      'gadget_erp5_field_listbox.js',
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
      'gadget_erp5_page_action.html',
      'gadget_erp5_page_action.js',
      'gadget_erp5_page_form.html',
      'gadget_erp5_page_form.js',
      'gadget_erp5_page_front.html',
      'gadget_erp5_page_front.js',
      'gadget_erp5_page_history.html',
      'gadget_erp5_page_history.js',
      'gadget_erp5_page_jump.html',
      'gadget_erp5_page_jump.js',
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
      'gadget_erp5_global.js',
      'gadget_jio.html',
      'gadget_jio.js',
      'gadget_translation.html',
      'gadget_translation.js',
      'gadget_translation_data.js',
      //other needed gadgets
      'gadget_erp5_pt_form_list.html',
      'gadget_erp5_global.js',
      'gadget_erp5_pt_form_list.html',
      'gadget_erp5_searchfield.html',
      'gadget_erp5_form.html',
      'gadget_erp5_form.js',
      'gadget_erp5_searchfield.js',
      'gadget_html5_input.html',
      'gadget_html5_input.js',
      'gadget_erp5_label_field.html',
      'gadget_erp5_label_field.js',
      'gadget_erp5_field_listbox.html',
      'gadget_erp5_field_listbox.js',
      //my gadgets for fifrunner
      'gadget_erp5_page_fifdata.html',
      'gadget_erp5_page_fifdata.js',
      'gadget_fif_page_list_dataset.html',
      'gadget_fif_page_list_dataset.js',
      'gadget_fif_page_list_file.html',
      'gadget_fif_page_list_file.js',
      'gadget_erp5_page_file_fif.html',
      'gadget_erp5_page_file_fif.js',
      'gadget_html5_element.html',
      'gadget_html5_element.js',
      'fif_gadget_erp5_panel.html',
      'fif_gadget_erp5_panel.js',
      'fif_gadget_erp5_header.html',
      'fif_gadget_erp5_header.js',
      'gadget_erp5_page_data_set.html',
      'gadget_erp5_page_data_set.js',
      'gadget_erp5_download_access.html',
      'gadget_erp5_download_access.js'
      //'gadget_erp5_ingestion_access.html',
      //'gadget_erp5_ingestion_access.js'
    ];

  self.addEventListener('install', function (event) {
    // Perform install step:  loading each required file into cache
    event.waitUntil(
      caches.open(CACHE_NAME)
        .then(function (cache) {
          // Add all offline dependencies to the cache
          return cache.addAll(REQUIRED_FILES);
        })
        .then(function () {
          // At this point everything has been cached
          return self.skipWaiting();
        })
    );
  });

  self.addEventListener('fetch', function (event) {
    event.respondWith(
      caches.match(event.request)
        .then(function (response) {
          // Cache hit - return the response from the cached version
          if (response) {
            return response;
          }

          // Not in cache - return the result from the live server
          // `fetch` is essentially a "fallback"
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
          // We return a promise that settles when all outdated caches are deleted.
          return Promise.all(
            keys
              .filter(function (key) {
                // Filter by keys that don't start with the latest version prefix.
                // return !key.startsWith(version);
                return key !== CACHE_NAME;
              })
              .map(function (key) {
                /* Return a promise that's fulfilled
                   when each outdated cache is deleted.
                */
                return caches.delete(key);
              })
          );
        })
        .then(function () {
          self.clients.claim();
        })
    );
  });



}(self, caches, fetch));
