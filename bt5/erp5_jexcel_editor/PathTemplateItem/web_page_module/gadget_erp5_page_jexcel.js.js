/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80*/
/*global window, RSVP, rJS, jIO*/
(function (window, RSVP, rJS, jIO) {
    "use strict";

    rJS(window)
    
    .declareService(function () {
      var gadget = this;
      var options_dict;
      return gadget.getDeclaredGadget("storage")
      .push(function (storage) {
        gadget.storage = storage;
        return storage.getSheet();
      })
      .push(function (result) {
        gadget.state.sheet = result;
        options_dict = {
          editor: "jexcel",
          key: "jexcel",
          maximize: true,
          editable: true,
          value: gadget.state.sheet.config
        };
        return gadget.getDeclaredGadget("editor");
      })
      .push(function (editor) {
        gadget.editor = editor;
        editor.render(options_dict);
      });
    })
  
    .onEvent("click", function (event) {
      var gadget = this;
      if (event.target.className === "save") {
        return gadget.editor.getContent()
        .push(function (content) {
          return gadget.storage.putSheet("sheet1", {config: JSON.parse(content.jexcel)});
        });
      }
    }, false, false);


  }(window, RSVP, rJS, jIO));