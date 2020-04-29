/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, RSVP, jexcel) {
    "use strict";
  
    rJS(window)
    
      //////////// WIP
      .ready(function () {
        var gadget = this;
        console.log("ready12");
        return gadget.getDeclaredGadget("model")
        .push(function (model) {
            gadget.storage = model;
          });
      })
 
      /////////////////
  
      .declareAcquiredMethod("notifySubmit", "notifySubmit")
      .declareJob("deferNotifySubmit", function () {
        // Ensure error will be correctly handled
        return this.notifySubmit();
      })
  
      .declareAcquiredMethod("notifyChange", "notifyChange")
      .declareJob("deferNotifyChange", function () {
        // Ensure error will be correctly handled
        var gadget = this;
            gadget.state.sheet.config = JSON.parse(JSON.stringify(this.table.getConfig()));
            return this.storage.putSheet(gadget.state.sheet.id, {config: gadget.state.sheet.config});
        //return this.notifyChange();
      })
  
      .declareMethod("render", function (options) {
        var gadget = this;
        return gadget.storage.getSheets()
        .push(function (sheet) {
            gadget.state.sheet = sheet;
        })
        .push(function () {
            return gadget.changeState(options);
        })
      })
  
      .declareJob("updateSheet", function () {
            var gadget = this;
            gadget.state.sheet.config = this.table.getConfig();
            console.log("update");
            return this.storage.putSheet(gadget.state.sheet.id, {config: this.state.sheet.config});
        })
  
      .onStateChange(function (modification_dict) {
        var gadget = this;
        var table;
        gadget.deferNotifyChangeBinded = gadget.deferNotifyChange.bind(gadget);
        if (modification_dict.hasOwnProperty('value') && modification_dict.value !== "") {
          table = jexcel(gadget.element.querySelector(".spreadsheet"), Object.assign(this.state.value, {
            editable: gadget.state.editable,
            onchange: gadget.deferNotifyChangeBinded, 
            onafterchanges: gadget.updateValue, 
            toolbar: [
              {
                type: 'i',
                content: 'undo',
                id: "undo",
                onclick: function () {
                  table.undo();
                }
              },
              {
                type: 'i',
                content: 'redo',
                onclick: function () {
                    table.redo();
                  }
              },
              {
                type: 'select',
                k: 'font-family',
                v: ['Arial', 'Arial Black', 'Verdana', 'Impact', 'Comic Sans MS', 'Tahoma', 'Trebuchet MS']
              },
              {
                type: 'select',
                k: 'font-size',
                v: ['20px', '21px', '22px', '23px', '24px', '25px', '26px', '27px', '28px', '29px', '30px', '32px', '34px', '36px', '38px', '40px']
              },
              {
                type: 'i',
                content: 'format_align_left',
                k: 'text-align',
                v: 'left'
              },
              {
                type: 'i',
                content: 'format_align_center',
                k: 'text-align',
                v: 'center'
              },
              {
                type: 'i',
                content: 'format_align_right', 
                k: 'text-align',
                v: 'right'
              },
              {
                type: 'i',
                content: 'format_bold',
                k: 'font-weight',
                v: 'bold'
              },
              {
                type: 'color',
                content: 'format_color_text',
                k: 'color'
              },
              {
                type: 'color',
                content: 'format_color_fill',
                k: 'background-color'
              }
            ]
          }));
          this.table = table;
        }
        else if (gadget.state.sheet.config !== "") {
            table = jexcel(gadget.element.querySelector(".spreadsheet"), Object.assign(this.state.sheet.config, {
                editable: gadget.state.editable,
                onchange: gadget.deferNotifyChangeBinded, 
                onafterchanges: gadget.updateValue, 
                toolbar: [
                  {
                    type: 'i',
                    content: 'undo',
                    id: "undo",
                    onclick: function () {
                      table.undo();
                    }
                  },
                  {
                    type: 'i',
                    content: 'redo',
                    onclick: function () {
                        table.redo();
                      }
                  },
                  {
                    type: 'select',
                    k: 'font-family',
                    v: ['Arial', 'Arial Black', 'Verdana', 'Impact', 'Comic Sans MS', 'Tahoma', 'Trebuchet MS']
                  },
                  {
                    type: 'select',
                    k: 'font-size',
                    v: ['20px', '21px', '22px', '23px', '24px', '25px', '26px', '27px', '28px', '29px', '30px', '32px', '34px', '36px', '38px', '40px']
                  },
                  {
                    type: 'i',
                    content: 'format_align_left',
                    k: 'text-align',
                    v: 'left'
                  },
                  {
                    type: 'i',
                    content: 'format_align_center',
                    k: 'text-align',
                    v: 'center'
                  },
                  {
                    type: 'i',
                    content: 'format_align_right', 
                    k: 'text-align',
                    v: 'right'
                  },
                  {
                    type: 'i',
                    content: 'format_bold',
                    k: 'font-weight',
                    v: 'bold'
                  },
                  {
                    type: 'color',
                    content: 'format_color_text',
                    k: 'color'
                  },
                  {
                    type: 'color',
                    content: 'format_color_fill',
                    k: 'background-color'
                  }
                ]
              }));
              this.table = table;
        }
        else {
          table = jexcel(this.element.querySelector(".spreadsheet"), {
            editable: this.state.editable,
            minDimensions: [26, 200],
            defaultColWidth: 100,
            fullscreen: true,
            allowComments: true,
            search: true,
            rowResize: true,
            tableOverflow: true,
            lazyLoading: true,
            loadingSpin: true,
            parseFormulas: false,
            onchange: gadget.deferNotifyChangeBinded,
            //onchange: gadget.updateSheet,
            toolbar: [
              {
                type: 'i',
                content: 'undo',
                id: "undo",
                onclick: function () {
                  table.undo();
                }
              },
              {
                type: 'i',
                content: 'redo',
                onclick: function () {
                    table.redo();
                  }
              },
              {
                type: 'select',
                k: 'font-family',
                v: ['Arial', 'Arial Black', 'Verdana', 'Impact', 'Comic Sans MS', 'Tahoma', 'Trebuchet MS']
              },
              {
                type: 'select',
                k: 'font-size',
                v: ['20px', '21px', '22px', '23px', '24px', '25px', '26px', '27px', '28px', '29px', '30px', '32px', '34px', '36px', '38px', '40px']
              },
              {
                type: 'i',
                content: 'format_align_left',
                k: 'text-align',
                v: 'left'
              },
              {
                type: 'i',
                content: 'format_align_center',
                k: 'text-align',
                v: 'center'
              },
              {
                type: 'i',
                content: 'format_align_right', 
                k: 'text-align',
                v: 'right'
              },
              {
                type: 'i',
                content: 'format_bold',
                k: 'font-weight',
                v: 'bold'
              },
              {
                type: 'color',
                content: 'format_color_text',
                k: 'color'
              },
              {
                type: 'color',
                content: 'format_color_fill',
                k: 'background-color'
              }
            ]
          });
          this.table = table;
        }
      })
  
      .declareMethod('getContent', function () {
        var form_data = {};
        if (this.state.editable) {
          form_data[this.state.key] = this.table.getConfig();
          this.state.value = form_data[this.state.key];
        }
        return form_data;
      })
    
      ;
  
  }(window, rJS, RSVP, jexcel));