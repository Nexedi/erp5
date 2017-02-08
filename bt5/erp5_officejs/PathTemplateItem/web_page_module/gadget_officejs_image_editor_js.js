/*global window, rJS, jIO, Blob*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, RSVP, jIO, Blob) {
  "use strict";

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          var textarea = element.querySelector('textarea');
          g.props.element = element;
          g.props.blob_defer = RSVP.defer();
        });
    })
    .declareAcquiredMethod("submitContent", "triggerSubmit")
    .declareMethod('render', function (options) {
      this.props.key = options.key || "text_content";
      return new RSVP.Queue()
      .push(function () {
        if (options.value.split('data:')[1] === '') {
          return '';
        }
        return jIO.util.dataURItoBlob(options.value);
      })
      .push(function (blob) {
        if (!blob) {
          blob = new Blob([''], {type: 'image/png'});
        }
        blob.name = options.name;
        FILE.open_handler({target: {files: [blob]}});
        return {};
      });
    })

    .declareMethod('getContent', function () {
      var result = {},
        gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return FILE.save({name: gadget.props.key, type: 'BLOB'});
        })
        .push(function (blob) {
          return jIO.util.readBlobAsDataURL(blob);
        })
        .push(function (datauri) {
          return datauri.target.result;
        });
    });

}(rJS, RSVP, jIO, Blob));