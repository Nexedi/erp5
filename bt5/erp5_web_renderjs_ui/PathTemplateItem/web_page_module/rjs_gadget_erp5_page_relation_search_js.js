/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
/*global window, rJS, RSVP, Handlebars*/
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    search_source = gadget_klass.__template_element
                         .getElementById("search-template")
                         .innerHTML,
    search_template = Handlebars.compile(search_source);

  Handlebars.registerHelper('equal', function (left_value,
    right_value, options) {
    if (arguments.length < 3) {
      throw new Error("Handlebars Helper equal needs 2 parameters");
    }
    if (left_value !== right_value) {
      return options.inverse(this);
    }
    return options.fn(this);
  });


  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function (param_list) {
      var gadget = this;
      return gadget.getUrlFor({command: 'history_previous'})
        .push(function (back_url) {
          return gadget.updateHeader({
            page_title: param_list[0].page_title,
            back_url: back_url,
            filter_action: true
          });
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this,
        select_template = options.select_template || "";
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.jio_getAttachment(options.url, options.view),
            gadget.getDeclaredGadget('form_list')
          ]);
        })
        .push(function (result_list) {
          var field = result_list[0]._embedded._view[
            options.back_field.slice("field_".length)
          ],
            listbox = field.listbox,
            listbox_key_list = Object.keys(field.listbox);

          if (listbox_key_list.length > 1) {
            if (select_template === "") {
              select_template = listbox_key_list[0];
            }
          } else {
            select_template = listbox_key_list[0];
          }
          listbox[select_template].command = "history_previous";
          listbox[select_template].line_icon = true;

          return RSVP.all([
            gadget.changeState({options: JSON.stringify(listbox_key_list),
                                select_template: select_template}),
            result_list[1].render({
              erp5_document: {"_embedded": {"_view": {
                "listbox": listbox[select_template]
              }},
                "title": result_list[0].title,
                "_links": result_list[0]._links
                },
              form_definition: {
                group_list: [[
                  "bottom",
                  [["listbox"]]
                ]]
              }
            })
          ]);
        });

    })
    .onStateChange(function () {
      var gadget = this,
        option_list = JSON.parse(gadget.state.options);
      if (option_list.length <= 1) {
        gadget.element.querySelector(".left").innerHTML = '';
        return;
      }
      return gadget.translateHtml(search_template({
        options: option_list,
        select_template: gadget.state.select_template
      }))
        .push(function (html) {
          gadget.element.querySelector(".left").innerHTML = html;
        });
    })
    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_list')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })
    .onEvent('change', function (evt) {
      var target = evt.target,
        value;
      if (target.nodeName === 'SELECT') {
        value = target.options[target.selectedIndex].value;
        this.state.select_template = value;
        return this.redirect({
          command: 'change',
          options: {
            select_template: value
          }
        });
      }
    });

}(window, rJS, RSVP, Handlebars));