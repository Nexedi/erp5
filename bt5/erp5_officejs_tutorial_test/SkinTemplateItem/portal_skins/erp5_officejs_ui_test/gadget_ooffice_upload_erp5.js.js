/*jslint indent: 2, nomen: true */
/*global window, rJS, jIO, URL, RSVP*/
(function (window, rJS, jIO, URL, RSVP) {
  "use strict";

  rJS(window)
    .declareService(function () {
      var storage = jIO.createJIO({
        type: "indexeddb",
        database: "officejs-erp5"
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
      return storage.put('test_ooo_' + param.type, {
        'reference': 'test_ooffice_upload',
        'title': 'Test Document',
        'filename': 'test.' + param.ooo_format,
        'portal_type': param.portal_type,
        'parent_relative_url': "document_module",
        'content_type': "application/x-asc-" + param.type,
        'modification_date': new Date().toISOString()
      })
      .push(function (id) {
        return new RSVP.Queue()
          .push(function () {
            return jIO.util.ajax({
              type: "GET",
              url: new URL('./test_ooo_' + param.type + '.' + param.format, window.location.href),
              dataType: "blob"
            });
          })
          .push(function (res) {
            return storage.putAttachment(id, param.format, res.target.response);
          })
          .push(function () {
            return RSVP.all([
              storage.put(
                'CloudoooConversion/' + id + '/' + param.ooo_format,
                {
                  status: 'convert',
                  from: param.format,
                  to: param.ooo_format,
                  id: id,
                  name: param.format
                }
              ),
              storage.put(
                'CloudoooConversion/' + id + '/' + param.ooo_format,
                {
                  status: 'convert',
                  from: param.format,
                  to: param.ooo_format,
                  id: id,
                  name: param.format
                }
              )
            ]);
          });
      })
      .push(function () {
        var div = window.document.createElement('div');
        div.textContent = 'Document Created';
        gadget.element.appendChild(div);
      });
    });
}(window, rJS, jIO, URL, RSVP));
