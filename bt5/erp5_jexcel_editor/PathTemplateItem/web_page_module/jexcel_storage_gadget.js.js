/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80*/
/*global window, RSVP, rJS, jIO*/
(function (window, RSVP, rJS, jIO) {
    "use strict";
    
    rJS(window)
    
    .ready(function () {
        var gadget = this;
        return this.changeState({storage: jIO.createJIO({
          type: "indexeddb",
          database: "sheet"
        })
       });
      })

    .declareMethod("getSheet", function () {
        var gadget = this;
        var sheet = {};
        return gadget.state.storage.allDocs({include_docs: true})
        .push(function (result) {
          if (result.data.total_rows > 0) {
            sheet.config = result.data.rows[0].doc.config;
            return sheet;
          }
          else {
            return gadget.state.storage.put("sheet1", {config: ""})
            .push(function () {
              return gadget.state.storage.get("sheet1");
            })
            .push(function (result) {
              sheet.config = result.config;
              return sheet;
            });
          }
        });
      })
  
    .declareMethod("putSheet", function (id, sheet) {
      return this.state.storage.put(id, sheet);
    });

  }(window, RSVP, rJS, jIO));