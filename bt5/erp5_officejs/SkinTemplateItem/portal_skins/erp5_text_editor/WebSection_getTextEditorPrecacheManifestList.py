# TODO: abstract common officejs elements between different apps into a single precache manifest
url_list = [
  "favicon.ico",
  "font-awesome/font-awesome.css",
  "URI.js",
  "dygraph.js",
  "handlebars.js",
  "gadget_officejs_router.js",
  "gadget_translate.html",
  "gadget_translate.js",
  "jio_ojs_storage.js",
  "gadget_erp5_page_ojs_configurator.html",
  "gadget_erp5_page_ojs_configurator.js",
  "gadget_erp5_page_ojs_dav_configurator.html",
  "gadget_erp5_page_ojs_dav_configurator.js",
  "gadget_erp5_page_ojs_erp5_configurator.html",
  "gadget_erp5_page_ojs_erp5_configurator.js",
  "gadget_erp5_page_ojs_dropbox_configurator.html",
  "gadget_erp5_page_ojs_dropbox_configurator.js",
  "gadget_erp5_page_ojs_sync.html",
  "gadget_erp5_page_ojs_sync.js",
  "gadget_erp5_page_ojs_linshare_configurator.html",
  "gadget_erp5_page_ojs_linshare_configurator.js",
  "gadget_ojs_configurator_access.html",
  "gadget_ojs_configurator_access.js",
  "gadget_officejs_setting.js",
  "gadget_officejs_setting.html",
  "gadget_ojs_local_jio.html",
  "gadget_ojs_local_jio.js",
  "gadget_erp5_page_action_officejs.html",
  "gadget_erp5_page_action_officejs.js",
  "gadget_erp5_page_ojs_local_controller.html",
  "gadget_erp5_page_ojs_local_controller.js",
  "gadget_officejs_form_view.html",
  "gadget_officejs_form_view.js",
  "gadget_erp5_page_handle_action.html",
  "gadget_erp5_page_handle_action.js",
  "gadget_officejs_common_util.html",
  "gadget_officejs_common_util.js",
  "gadget_erp5_page_create_document.html",
  "gadget_erp5_page_create_document.js",

  #needed for appcachestorage sync
  "/",
  "app/",
  "gadget_officejs_bootloader.js",
  "gadget_officejs_bootloader_presentation.html",
  "gadget_officejs_bootloader_presentation.js",
  "gadget_officejs_bootloader_presentation.css",
  "gadget_officejs_bootloader_serviceworker.js",
  "officejs_logo.png",
  "jio_appcachestorage.js",
  "jio_configuration_storage.js",

  #text editor specific
  "gadget_officejs_text_editor.configuration",
  "gadget_officejs_text_editor.json",
  "officejs_logo_text_editor.png",
  "gadget_officejs_text_editor_router.html",

  #app custom actions
  "action_texteditor_clone.html",
  "action_texteditor_clone.js",

  #app_configuration_resources
  #CONFIGURATION ELEMENTS generated on Fri Dec 13 14:45:53 2019. Same as in configuration manifest
  "hateoas_appcache/definition_view/cG9ydGFsX3R5cGVzL1dlYiBQYWdlIE1vZHVsZQ==",
  "hateoas_appcache/definition_view/cG9ydGFsX3R5cGVzL1dlYiBQYWdlIE1vZHVsZS90ZXh0X2VkaXRvcl92aWV3",
  "hateoas_appcache/definition_view/cG9ydGFsX3NraW5zL2VycDVfdGV4dF9lZGl0b3IvV2ViUGFnZU1vZHVsZV92aWV3V2ViUGFnZUxpc3RBc0ppb0ZvclRleHRFZGl0b3I=",
  "hateoas_appcache/definition_view/cG9ydGFsX3R5cGVzL1dlYiBQYWdl",
  "hateoas_appcache/definition_view/cG9ydGFsX3R5cGVzL1dlYiBQYWdlL3RleHRfZWRpdG9yX3ZpZXc=",
  "hateoas_appcache/definition_view/cG9ydGFsX3NraW5zL2VycDVfdGV4dF9lZGl0b3IvV2ViUGFnZV92aWV3QXNUZXh0RG9jdW1lbnRGb3JUZXh0RWRpdG9y",
  "hateoas_appcache/definition_view/cG9ydGFsX3R5cGVzL1dlYiBQYWdlL3RleHRfZWRpdG9yX2Nsb25l",
  "hateoas_appcache/definition_view/cG9ydGFsX3NraW5zL2VycDVfdGV4dF9lZGl0b3IvQmFzZV9jbG9uZURvY3VtZW50Rm9yVGV4dEVkaXRvcg==",
  #/app_configuration_resources
]

return url_list
