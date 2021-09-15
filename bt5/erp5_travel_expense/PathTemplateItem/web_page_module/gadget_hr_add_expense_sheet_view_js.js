/*globals window, rJS, Handlebars, RSVP, console*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, loopEventListener, promiseEventListener, alertify) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".view-expense-sheet-template")
                              .innerHTML,
    template = Handlebars.compile(source);
  function drawSvgString(title, number) {
    var i = 0,
      default_x = -2473.00382,
      default_rotate_y = -867.000793457031,
      step = 80,
      max = 1970,
      string_title_number = '',
      base = '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="2100"><g><title>' + (title + ' ' + number)+ '</title><rect x="-1" y="-1" width="100%" height="2102" id="canvas_background" fill="#b2b2b2"/><rect id="svg" width="100%" height="100%" x="0" y="0" stroke-width="0" fill="url(#gridpattern)"/></g><g>';
    if (! title && !number) {
      return '';
    }
    while(string_title_number.length < 500) {
      string_title_number += title + ' ' + number + ' ';
   }
   if (window.innerWidth > max) {
     max = window.innerWidth;
   }
    for (i = 0; i < max*2 / step; i += 1){
      base += '<text fill="#000000" stroke="#000" stroke-width="0" x=' + (default_x + i * step) + ' y="977.99989" id="svg_' + i + '" font-size="24" font-family="Helvetica, Arial, sans-serif" text-anchor="start" xml:space="preserve" opacity="0.45" transform="rotate(-45,' + (default_rotate_y + i * step) +',971.9843750000001) ">';
      base  += string_title_number + '</text>';
    }
    return base + '</g></svg>';
  }
  gadget_klass
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          alertify.set({ delay: 1500 });
          g.props = {};
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("get", "jio_get")
    .declareAcquiredMethod("put", "jio_put")
    .declareAcquiredMethod("post", "jio_post")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod('jio_remove', 'jio_remove')
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('setSetting', 'setSetting')
    .declareMethod('triggerSubmit', function () {
      return this.props.element.querySelector('button').click();
    })
    .declareMethod("render", function (options) {
      var gadget = this,
       sync_checked,
       state = window.getWorkflowState(options),
       not_sync_checked;
      gadget.options = options;
      return new RSVP.Queue()
        .push(function () {
          var ops;
          if (options.doc.sync_flag === '1') {
            sync_checked = 'checked';
          } else {
            not_sync_checked = 'checked';
          }
          ops = {
            title: options.doc.title,
            number: options.doc.number,
            sync_checked:  sync_checked,
            not_sync_checked: not_sync_checked,
            not_readonly: !state.readonly
          };
          return gadget.translateHtml(template(ops));
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          gadget.props.element.querySelector('.svg').innerHTML = options.doc.text_content || '';//drawSvgString(options.doc.title || '',  options.doc.number || '');

          return gadget.updateHeader({
            title: gadget.options.jio_key,
            save_action: !state.readonly,
            breadcrumb_url: '#page=expense_sheet_list'
          });
        })
        .push(function () {
          gadget.props.deferred.resolve();
        });
    })
    .declareService(function () {
      var gadget = this,
        form = gadget.props.element.querySelector('form.view-expense-sheet-form');
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            form,
            'submit',
            false,
            function (submit_event) {
              var i,
                doc = {
                  parent_relative_url: "expense_sheet_module",
                  portal_type: "Expense Sheet",
                  modification_date: new Date().toISOString().slice(0, 10).replace(/-/g, "/")
              };
              for (i = 0; i < submit_event.target.length; i += 1) {
                 if ((form[i].type == "radio") && !form[i].checked){
                   continue;
                 }
                 if (submit_event.target[i].value) {
                   doc[submit_event.target[i].name] = submit_event.target[i].value;
                 }
              }
              doc.text_content =  gadget.props.element.querySelector('.svg').innerHTML;
              if (doc.sync_flag === '1'){
                doc.reference = 'expense_sheet';
              }
              return gadget.put(gadget.options.jio_key, doc)
                .push(function () {
                  alertify.success("Saved");
                  if (doc.sync_flag === '1') {
                    return gadget.redirect();
                  }
                });
            });
      });
  })
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return RSVP.any([
            loopEventListener(
              gadget.props.element.querySelector('.title'),
              'input',
              false,
              function (event) {
                gadget.props.element.querySelector('.svg').innerHTML = drawSvgString(event.target.value, gadget.props.element.querySelector('.number').value);

              }),
            loopEventListener(
              gadget.props.element.querySelector('.number'),
              'input',
              false,
              function (event) {
                gadget.props.element.querySelector('.svg').innerHTML = drawSvgString(gadget.props.element.querySelector('.title').value, event.target.value);
              })]);
      });
  });
}(window, document, RSVP, rJS, Handlebars, rJS.loopEventListener, promiseEventListener, alertify));