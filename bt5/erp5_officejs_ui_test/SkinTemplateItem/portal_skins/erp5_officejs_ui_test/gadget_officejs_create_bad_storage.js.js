/*jslint indent: 2, nomen: true */
/*global window, rJS, jIO, document*/
(function (window, rJS, jIO) {
  "use strict";

  rJS(window)
    .declareService(function () {
      var storage = jIO.createJIO({
        type: "indexeddb",
        database: "setting"
      }),
        gadget = this;
      return storage.put(
        'setting/Discussion Tool',
        {'jio_storage_description': {type: 'unknownstorage'}}
      )
      .push(function () {
        var div = document.createElement('div');
        div.textContent = 'Storage Created';
        gadget.element.appendChild(div);
      });
    });
}(window, rJS, jIO, document));
