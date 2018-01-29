/*global window, rJS, RSVP, jIO, DOMParser, Uint8Array */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO, DOMParser, Blob, Uint8Array) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('b64toBlob', function (b64Data, contentType, sliceSize) {
      contentType = contentType || '';
      sliceSize = sliceSize || 512;

      var byteCharacters = window.atob(b64Data);
      var byteArrays = [];

      for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        var slice = byteCharacters.slice(offset, offset + sliceSize);

        var byteNumbers = new Array(slice.length);
        for (var i = 0; i < slice.length; i++) {
          byteNumbers[i] = slice.charCodeAt(i);
        }

        var byteArray = new Uint8Array(byteNumbers);

        byteArrays.push(byteArray);
      }

      var blob = new Blob(byteArrays, {type: contentType});
      return blob;
    })

    .declareMethod('convert', function (file, source_mime_type, destination_mime_type) {
      var xml = '<?xml version="1.0"?><methodCall><methodName>convertFile</methodName><params><param><value><string>' + file +
        '</string></value></param><param><value><string>' + source_mime_type +
        '</string></value></param><param><value><string>' + destination_mime_type +
        '</string></value></param></params></methodCall>';
      return RSVP.Queue()
        .push(function () {
          return jIO.util.ajax({
            type: 'POST',
            url: 'https://softinst88847.host.vifib.net/',
            data: xml
          });
        })
        .push(function (result) {
          return (new DOMParser().parseFromString(
            result.currentTarget.response,
            "application/xml"
          )).getElementsByTagName('string')[0].textContent;
        });
    });
}(window, rJS, RSVP, jIO, DOMParser, Blob, Uint8Array));