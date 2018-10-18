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
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.jio_getAttachment(options.url, options.view),
            gadget.getDeclaredGadget('form_list')
          ]);
        })
        .push(function (result_list) {
          // return result_list[1].render(result_list[0]);
          var listbox = result_list[0]._embedded._view.listbox;
          listbox.command = "history_previous";
          listbox.line_icon = true;

          return RSVP.all([
            gadget.changeState({
              proxy_form_id_list: JSON.stringify(
                result_list[0]._embedded._view.proxy_form_id_list
              ),
              view: options.view
            }),
            result_list[1].render({
              erp5_document: {"_embedded": {"_view": {
                "listbox": listbox
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
        proxy_form_id_list = JSON.parse(gadget.state.proxy_form_id_list);
      if (proxy_form_id_list.length <= 1) {
        gadget.element.querySelector(".left").innerHTML = '';
        return;
      }
      return gadget.translateHtml(search_template({
        option_list: proxy_form_id_list,
        value: gadget.state.view
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
        this.state.view = value;
        return this.redirect({
          command: 'change',
          options: {
            view: value
          }
        });
      }
    });

}(window, rJS, RSVP, Handlebars));