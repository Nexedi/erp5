/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";


  rJS(window)
    .ready(function (gadget) {
      gadget.props = {};
      return gadget.getDeclaredGadget("jio_gadget")
        .push(function (jio_gadget) {
          gadget.props.jio_gadget = jio_gadget;
          gadget.props.parameters = {};
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.jio_gadget.createJio({
            type: "query",
            sub_storage: {
              type: "drivetojiomapping",
              sub_storage: {
                type: "dav",
                url: options.url,
                basic_login: options.basic_login
              }
            }
          });
        })
        .push(function () {
          return gadget.changeState({
            parameter_list: options.parameters,
            save_to: 'config.tmp',
            document_key: 'config',
            url: options.url,
            title: options.title || '',
            key: new Date().getUTCMilliseconds()
          });
        });
    })

    .onStateChange(function (change_dict) {
      var gadget = this;
      // render parameter form
      if (!change_dict.hasOwnProperty('key')) {
        return;
      }
      gadget.element.querySelector('.parameter-box-title').textContent =
        gadget.state.title;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          var i,
            parameter_dict = {},
            group_list = [
              ["left", []],
              ["right", []]
            ];
          for (i = 0; i < gadget.state.parameter_list.length; i += 1) {
            parameter_dict[gadget.state.parameter_list[i].title] = {
              "description": "",
              "title": gadget.state.parameter_list[i].title.replace(/-/g, ' '),
              "default": gadget.state.parameter_list[i].value,
              "css_class": "",
              "required": 0,
              "editable": (gadget.state.parameter_list[i].key === '' ||
                gadget.state.parameter_list[i].key === "monitor-password") ? 0 : 1,
              "key": gadget.state.key + '_' +
                gadget.state.parameter_list[i].title,
              "hidden": 0,
              "type": "StringField" // for now everything are stringField
            };
            group_list[i % 2][1].push([gadget.state.parameter_list[i].title]);
          }
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": parameter_dict},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: group_list
            }
          });
        });
    })
    .declareMethod("getLiveParameters", function () {
      var gadget = this;
      return this.props.jio_gadget.get(this.state.document_key)
        .push(function (result) {
          return gadget.changeState({parameter_list: result})
            .push(function () {
              return {status: "OK", doc: result};
            });
        }, function (error) {
          return {status: "ERROR", code: error.target.status,
                  url: gadget.state.url, stage: "Getting file"};
        });
    })
    .declareMethod("getContent", function () {
      return this.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.getContent();
        });
    })
    .declareMethod("saveContent", function () {
      var gadget = this;
      return this.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (doc) {
          var key,
            parameter_list = JSON.parse(JSON.stringify(gadget.state.parameter_list)),
            i;
          for (i = 0; i < parameter_list.length; i += 1) {
            key = gadget.state.key + '_' + parameter_list[i].title;
            if (doc.hasOwnProperty(key)) {
              parameter_list[i].value = doc[key];
            }
          }
          return gadget.props.jio_gadget.put(gadget.state.save_to, parameter_list);
        })
        .push(function () {
          return {status: 'OK'};
        }, function (error) {
          //console.log(error);
          return {status: 'ERROR', code: error.target.status,
                  url: gadget.state.url, stage: "Saving file"};
        });
    });

}(window, rJS, RSVP));