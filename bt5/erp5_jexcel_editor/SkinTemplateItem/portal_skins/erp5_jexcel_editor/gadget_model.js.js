/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80*/
/*global window, RSVP, rJS, jIO*/
(function (window, RSVP, rJS, jIO) {
    "use strict";
    
    rJS(window)
    
    .ready(function () {
        var gadget = this;
        return this.changeState({storage: jIO.createJIO({
          type: "indexeddb",
          database: "sheets"
        })
       });
      })
  
    .declareMethod("getSheet", function () {
      return this.storage.alldocs()
      .push(function (result) {
        console.log(result);
      });
    });

  }(window, RSVP, rJS, jIO));