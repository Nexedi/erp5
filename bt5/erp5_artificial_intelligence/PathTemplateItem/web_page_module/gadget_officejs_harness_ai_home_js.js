/*global window, rJS, RSVP, document, SimpleQuery */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, document, SimpleQuery) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    .allowPublicAcquisition('getCommentPostList', function () {
      return [];
    })
    .allowPublicAcquisition('postComment', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0],
        form_data_json = argument_list[1];
      return gadget.jio_putAttachment(document_id,
        gadget.hateoas_url + document_id + "/ArtificialTaskModule_startNewArtificialTask",
        form_data_json);
    })

    .declareMethod('renderHistory', function () {
      var gadget = this;
      return gadget.jio_allDocs({
        query: new SimpleQuery({
          key: "portal_type",
          operator: "=",
          type: "simple",
          value: "Artificial Task"
        }),
        sort_on: [["modification_date", "descending"]],
        limit: [0, 20]
      })
        .push(function (result) {
          return RSVP.all((result.data.rows || []).map(function (row) {
            return gadget.getUrlFor({
              command: 'display',
              options: {jio_key: row.id}
            })
              .push(function (url) {
                return {url: url, title: row.value.title || row.id};
              });
          }));
        })
        .push(function (link_list) {
          var ul = gadget.element.querySelector('.harness-home-history-list'),
            i,
            li,
            a;
          ul.textContent = "";
          for (i = 0; i < link_list.length; i += 1) {
            li = document.createElement('li');
            a = document.createElement('a');
            a.href = link_list[i].url;
            a.textContent = link_list[i].title;
            li.appendChild(a);
            ul.appendChild(li);
          }
        })
        .push(undefined, function () {
          return;
        });
    })

    .declareMethod('render', function () {
      var gadget = this;
      gadget.options = {'jio_key': 'artificial_task_module'};
      return gadget.getSetting('hateoas_url')
        .push(function (hateoas_url) {
          gadget.hateoas_url = hateoas_url;
        })
        .push(function () {
          return gadget.changeState({id: 'artificial_task_module'});
        });
    })
    .onStateChange(function () {
      var gadget = this;
      return RSVP.all([
        gadget.getDeclaredGadget("gadget_chat")
          .push(function (chat) {
            return chat.render({
              'hateoas_url': gadget.hateoas_url,
              'jio_key': gadget.options.jio_key,
              'editor_options': {
                editor: 'gadget_editor.html',
                options: {
                  value: "",
                  key: "comment",
                  portal_type: "Artificial Task Line",
                  editable: true,
                  editor: 'codemirror',
                  maximize: true
                }
              }
            });
          }),
        gadget.renderHistory()
      ]);
    });
}(window, rJS, RSVP, document, SimpleQuery));
