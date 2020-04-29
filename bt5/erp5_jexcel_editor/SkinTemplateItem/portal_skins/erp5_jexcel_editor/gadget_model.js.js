/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80*/
/*global window, RSVP, rJS, jIO*/
(function (window, RSVP, rJS, jIO) {
    "use strict";
    
    rJS(window)
    
    .ready(function () {
        var gadget = this;
        return this.changeState({storage: jIO.createJIO({
              type: "uuid",
              sub_storage: {
                  type: "indexeddb",
                  database: "sheet"
              }
        })
       });
    })

    .declareMethod("getSheet", function () {
        var gadget = this;
        var sheet = {};
        var id_save;
        return gadget.state.storage.allDocs({include_docs: true})
        .push(function (result) {
            if(result.data.total_rows == 1){
                sheet.id = result.data.rows[0].id;
                sheet.config = result.data.rows[0].doc.config;
                return sheet;
            }
            else {
              return gadget.state.storage.post({config: ""})
              .push(function (id) {
                id_save = id;
                return gadget.state.storage.get(id);
              })
              .push(function (result) {
                sheet.id = id_save;
                sheet.config = result.config;
                return sheet;
              })
            };
      });
    })
  
    .declareMethod("putSheet", function (id, sheet) {
      return this.state.storage.put(id, sheet);
    })

    .declareMethod("postSheet", function (config) {
        var gadget = this;
        return gadget.state.storage.post({
            config: config
        })
    });

  }(window, RSVP, rJS, jIO));