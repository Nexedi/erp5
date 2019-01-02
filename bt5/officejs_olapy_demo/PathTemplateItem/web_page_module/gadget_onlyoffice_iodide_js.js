/*jslint indent: 2*/
/*global rJS, window, RSVP, jIO */
(function (rJS, window, RSVP, jIO) {
  "use strict";

  rJS(window)
  .allowPublicAcquisition('notifyChange', function (options) {
    window.console.warn(options);
  })
  .allowPublicAcquisition('submitContent', function () {
    window.console.warn(arguments);
  })
  .ready(function (gadget) {
    return gadget.render();
  })
  .onStateChange(function (modif_dict) {
    var gadget = this;
    if (modif_dict.hasOwnProperty("script")) {
      gadget.element.querySelector('.script').value = gadget.state.script;
    }
    if (modif_dict.hasOwnProperty("result")) {
      gadget.element.querySelector('.result').value = gadget.state.result;
    }
  })
  .declareMethod("render", function () {
    var gadget = this;
    return gadget.changeState({
      script:
        'var dataframes_paths = ["olapy-data/cubes/sales/Facts.csv","olapy-data/cubes/sales/Product.csv","olapy-data/cubes/sales/Geography.csv"]\n' +
        '\n' +
        'var mdx_query = "SELECT  FROM [sales] WHERE ([Measures].[Amount]) CELL PROPERTIES VALUE, FORMAT_STRING, LANGUAGE, BACK_COLOR, FORE_COLOR, FONT_FLAGS"\n' +
        '\n' +
        '\n' +
        'callFunction({"fun": "get_olapy_response", argument_list: [dataframes_paths,mdx_query]})',
      result: ""
    })
      .push(function () {
        return RSVP.all([
          gadget.getDeclaredGadget('iodide'),
          jIO.util.ajax({
            url: "gadget_onlyoffice_iodide.jsmd"
          })
        ]);
      })
      .push(function (result) {
        return result[0].render({
          key: 'script',
          value: result[1].target.response
        });
      });
  })
  .onEvent('click', function (evt) {
    var gadget = this, script;
    if (evt.target.tagName === 'BUTTON') {
      return gadget.getDeclaredGadget('iodide')
        .push(function (iodide) {
          script = gadget.element.querySelector('.script').value;
          return iodide.evalCode(script);
        })
        .push(function (result) {
          return gadget.changeState({"script" : script, "result": result});
        }, function (error) {
          return gadget.changeState({"script" : script, "result": error});
        });
    }
  });

}(rJS, window, RSVP, jIO));
