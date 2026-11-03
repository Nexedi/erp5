/*jslint indent: 2, nomen: true */
/*global window, rJS, jIO, URL*/
(function (window, rJS, jIO, URL) {
  "use strict";

  rJS(window)
    .declareService(function () {
      var storage = jIO.createJIO({
        type: "indexeddb",
        database: "local_default"
      }),
        gadget = this,
        element_list =
          gadget.element.querySelectorAll("[data-renderjs-configuration]"),
        len = element_list.length,
        i,
        param = {};
      for (i = 0; i < len; i += 1) {
        param[element_list[i].getAttribute('data-renderjs-configuration')] =
          element_list[i].textContent;
      }
      return storage.put('test', {
        'reference': 'test_ooffice_upload',
        'title': 'Test Document',
        'filename': 'test.' + param.format,
        'portal_type': param.portal_type,
        'parent_relative_url': "document_module",
        'content_type': "application/x-asc-" + param.type
      })
      .push(function (id) {
        return jIO.util.ajax({
          type: "GET",
          url: new URL('./test_ooo_' + param.type + '.' + param.format, window.location.href),
          dataType: "blob"
        })
          .then(function (res) {
            return storage.putAttachment(id, 'data', res.target.response);
          });
      })
      .push(function () {
        var div = window.document.createElement('div');
        div.textContent = 'Document Created';
        gadget.element.appendChild(div);
      });
    });
}(window, rJS, jIO, URL));
