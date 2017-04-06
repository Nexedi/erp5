/*globals window, RSVP, rJS, loopEventListener, URL, document
  FileReader, console */
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, jIO) {
  "use strict";

  function exportZip(gadget) {
    var cache_file = gadget.props.element.querySelector(
            'form input[name="cachefile"]').value,
        site_url = gadget.props.element.querySelector(
            'form input[name="site_url"]').value;
    return gadget.exportZip(cache_file, site_url)
      .push(function (zip_file) {
        var element = gadget.props.element,
          a = document.createElement("a"),
          url = URL.createObjectURL(zip_file),
          zip_name = gadget.props.element.querySelector(
            'form input[name="filename"]').value || "source_code";
        element.appendChild(a);
        a.style = "display: none";
        a.href = url;
        a.download = zip_name + ".zip";
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
    .declareMethod("exportZip", function (cache_file, site_url) {
      var gadget = this,
        file_storage = jIO.createJIO({
        type: "replicate",
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
            manifest: cache_file,
            url: site_url
          }
        },
        signature_storage: {
          type: "memory"
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
            gadget.props.element.querySelector('form.export-form'),
            'submit',
            true,
            function (event) {
              return exportZip(gadget);
            }
          );
        });
    });

}(window, RSVP, rJS, jIO));