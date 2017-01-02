/*globals window, rJS, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, loopEventListener) {
  "use strict";
  var comment_icon = 'responsive ui-btn ui-icon-comment ui-btn-icon-left ui-corner-all ui-shadow-inset',
    waiting_icon  = "responsive ui-btn ui-icon-spinner ui-icon-spin ui-btn-icon-left ui-corner-all ui-shadow-inset ui-disabled";
  rJS(window)
    .declareAcquiredMethod('allDocs', 'jio_allDocs')
    .declareAcquiredMethod('post', 'jio_post')
    .declareAcquiredMethod('put', 'jio_put')
    .declareAcquiredMethod("repair", "jio_repair")
    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;
      return gadget.allDocs({
        query: 'portal_type: Person' ,
        select_list: ['first_name', 'last_name'],
        limit: [0, 1]
      })
      .push(function (result) {
        gadget.author = result.data.rows[0].value['first_name'] + ' ' + result.data.rows[0].value['last_name'];
        return gadget.allDocs({
          query: options.query ,
          select_list: options.select_list,
          sort_on: [['int_index', "ascending"]], 
          limit: [0, 1000]
        });
      })
      .push(function (result) {
        var i,
          content = '';
        gadget.total_rows = result.data.total_rows;
        for (i = 0; i < result.data.total_rows; i += 1) {
          content += result.data.rows[i].value[options.select_list[2]] + ' ';
          content += result.data.rows[i].value[options.select_list[0]] + ': ';
          content += result.data.rows[i].value[options.select_list[1]] + '\n';
        }
        gadget.element.querySelector('pre').innerHTML = content;
        gadget.element.querySelector('button').className = comment_icon;
        gadget.element.querySelector('textarea').value = "";
      });
    })
    .declareMethod("readyToSync", function (ops) {
      var i = 0,
        list = [],
        data,
        gadget = this;
      return gadget.allDocs({
          query: gadget.options.query ,
          select_list: ['parent_relative_url', 'portal_type', 'title', 'description', 'contributor_title', 'creation_date',
            'int_index', 'source_reference','destination_reference'],
          limit: [0, 1000]
        })
        .push(function (result) {
          for (i = 0; i < result.data.total_rows; i += 1) {
            data = result.data.rows[i].value;
            data.portal_type = 'Text Post';
            data.title = ops.title;
            list.push(gadget.put(result.data.rows[i].id, data));
          }
          return RSVP.all(list);
        });
     
    })
    .declareService(function () {
      var gadget = this,
        submit = gadget.element.querySelector('button'),
        form;
      form = gadget.element.querySelector('form');
      return loopEventListener(
        form,
        'submit',
        false,
        function () {
          var doc = {
            parent_relative_url: "post_message_module",
            portal_type: gadget.options.sync? "Text Post" : "Text Post Tmp",
            title: gadget.options.title,
            description: gadget.element.querySelector('textarea').value,
            contributor_title: gadget.author,
            creation_date: new Date().toISOString().slice(0, 10),
            int_index: gadget.total_rows,
            source_reference: 'expense_validation_record',
            destination_reference: gadget.options.destination_reference
          };
          return gadget.post(doc)
            .push(function () {
              submit.className = waiting_icon;
              if (gadget.options.sync) {
                return gadget.repair();
              }
            })
            .push(function () {
               return gadget.render(gadget.options);
            });
        });
    });
}(window, RSVP, rJS, loopEventListener));