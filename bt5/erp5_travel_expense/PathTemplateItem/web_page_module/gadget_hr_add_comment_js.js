/*globals window, rJS, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, loopEventListener, Handlebars) {
  "use strict";
  var waiting_icon  = "responsive ui-btn ui-icon-spinner ui-icon-spin ui-btn-icon-left ui-corner-all ui-shadow-inset ui-disabled",
    gadget_klass = rJS(window),
    source = gadget_klass.__template_element.querySelector(".discussion-template").innerHTML,
    template = Handlebars.compile(source);
  gadget_klass
    .declareAcquiredMethod('post', 'jio_post')
    .declareAcquiredMethod('put', 'jio_put')
    .declareAcquiredMethod("allDocs", "jio_allDocs")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("remove", "jio_remove")
    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;
      if (!options.can_add_discussion && !options.doc.transition_comment) {
        return;
      }
      return gadget.allDocs({
        query: 'portal_type: Person' ,
        select_list: ['first_name', 'last_name'],
        limit: [0, 1]
      })
      .push(function (result) {
        var i,
          content = '',
          transition_comment = {};
        gadget.author = result.data.rows[0].value.first_name + ' ' + result.data.rows[0].value.last_name;
        if (options.doc.transition_comment) {
          transition_comment = JSON.parse(options.doc.transition_comment);
        }
        for (i in transition_comment) {
          content += transition_comment[i].time + ' ';
          content += transition_comment[i].actor + ': ';
          content += transition_comment[i].comment + '\n';
        }
        gadget.transition_comment = transition_comment;
        return template({
          content: content,
          can_add_discussion: options.can_add_discussion
        });
      })
      .push(function (html) {
        gadget.element.querySelector('form').innerHTML = html;
      });
    })
    .declareService(function () {
      var gadget = this,
        submit = gadget.element.querySelector('button'),
        form = gadget.element.querySelector('form');
      if (gadget.options.can_add_discussion) {
        return loopEventListener(
          form,
          'submit',
          false,
          function () {
            var len = Object.keys(gadget.transition_comment).length,
              tmp;
            gadget.transition_comment[len] = {
              'actor': gadget.author,
              'time': new Date().toISOString().slice(0, 10),
              'comment': gadget.element.querySelector('textarea').value
            };
            gadget.options.doc.state = 'Opened';
            gadget.options.doc.transition_comment = JSON.stringify(gadget.transition_comment);
            submit.className = waiting_icon;
            return gadget.post(gadget.options.doc)
              .push(function () {
                /*
                modify data will change hash code,
                which jio will try to push localmodify to erp5
                gadget.options.doc.simulation_state = 'delivered';
                return gadget.put(gadget.options.jio_key, gadget.options.doc);
                */
                return gadget.remove(gadget.options.jio_key);
              })
             .push(function () {
               return gadget.redirect({page: gadget.options.page});
             });
         });
      }
    });
}(window, RSVP, rJS, loopEventListener, Handlebars));