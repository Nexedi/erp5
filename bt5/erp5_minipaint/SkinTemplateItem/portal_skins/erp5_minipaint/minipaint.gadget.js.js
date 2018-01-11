/*global window, rJS, jIO, Blob*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, RSVP, jIO, Blob) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (options) {
      return this.changeState({
        key: options.key,
        value: options.value
      });
    })
    .onStateChange(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          if (gadget.state.value.blob.split('data:')[1] === '') {
            return '';
          }
          return jIO.util.dataURItoBlob(gadget.state.value.blob);
        })
        .push(function (blob) {
          if (!blob) {
            blob = new Blob([''], {type: 'image/png'});
          }
          blob.name = gadget.state.value.name;
          FILE.open_handler({target: {files: [blob]}});
          return;
      });
    })

    .declareMethod('getContent', function () {
      var result = {}, gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return FILE.save({name: gadget.state.key, type: 'BLOB'});
        })
        .push(function (blob) {
          return jIO.util.readBlobAsDataURL(blob);
        })
        .push(function (datauri) {
          var result = {};
          result[gadget.state.key] = datauri.target.result;
          return result;
        });
    });

}(rJS, RSVP, jIO, Blob));