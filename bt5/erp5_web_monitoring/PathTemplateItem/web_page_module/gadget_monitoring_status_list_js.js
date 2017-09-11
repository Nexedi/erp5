/*global window, rJS, RSVP, URI, location, $,
    loopEventListener, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, $) {
  "use strict";

  rJS(window)
    .ready(function (gadget) {
      gadget.property_dict = {
        render_deferred: RSVP.defer()
      };
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("listbox")
        .push(function (listbox_gadget) {
          gadget.property_dict.listbox = listbox_gadget;
        });
    })
    .declareMethod('render', function (options) {
      var gadget = this,
        header = {
          "title": 'Monitoring Promises Status'
        },
        listbox_configuration = {
          search_page: 'status_list',
          search: options.search,
          filter: options.filter || '',
          column_list: [{
            title: 'Promise',
            select: 'source'
          }, {
            title: 'Software Instance',
            select: 'channel_item'
          }, {
            title: 'Hosting Subscription',
            select: 'channel'
          }, {
            select: 'lastBuildDate',
            title: 'Promise Date',
            convertDate: true
          }, {
            select: 'comments',
            title: 'Message',
            css_class: 'text-overview'
          }, {
            select: 'category',
            title: 'Status',
            template: ' <span class="label label-{{value}}">{{value}}</span>',
            css_class: 'ui-text-center'
          }],
          filter_column: {select: "category", "title": "Status"},
          query: {
            "limit": [0, 400],
            select_list: ['source', 'channel_item', 'channel', 'category',
              'date', 'comments', 'link', 'lastBuildDate', 'parent_id'],
            query: '(portal_type:"promise") AND (active:true)',
            sort_on: [["category", "ascending"], ["channel", "ascending"]]
          }
        };

      return gadget.updateHeader(header)
        .push(function () {
          if (options.reset_filter === "1") {
            return;
          }
          if (!options.hasOwnProperty('search') || !options.hasOwnProperty('filter')) {
            return gadget.getSetting('status_list_selection_key')
              .push(function (selection) {
                if (selection) {
                  return gadget.redirect({
                    page: 'status_list',
                    filter: options.filter || selection.filter,
                    search: options.search || selection.search
                  });
                }
              });
          }
        })
        .push(function () {
          var selection = {
            filter: options.filter || '',
            search: options.search || ''
          };
          if (options.reset_filter !== "1") {
            return gadget.setSetting('status_list_selection_key', selection);
          } else {
            return '';
          }
        })
        .push(function () {
          gadget.property_dict.options = options;
          return gadget.property_dict.listbox.render(listbox_configuration);
        });
    })
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("renderApplication", "renderApplication")
    .declareService(function () {
      var gadget = this,
        current_sync_date;

      return gadget.getSetting('latest_sync_time')
        .push(function (sync_time) {
          current_sync_date = sync_time;
          return gadget.getSetting('status_list_refresh_id');
        })
        .push(function (timer_id) {
          var new_timer_id;
          if (timer_id) {
            clearInterval(timer_id);
          }
          new_timer_id = setInterval(function(){
            var hash = window.location.toString().split('#')[1],
              scroll_position,
              doc = document.documentElement;
            if (hash.indexOf('page=status_list') >= 0) {
              return gadget.getSetting('latest_sync_time')
                .push(function (sync_time) {
                  if (sync_time > current_sync_date) {
                    scroll_position = (window.pageYOffset || doc.scrollTop)  - (doc.clientTop || 0);
                    current_sync_date = sync_time;
                    return gadget.renderApplication({args: gadget.property_dict.options})
                      .push(function () {
                        $(document).scrollTop(scroll_position);
                      });
                  }
                });
            }
          }, 60000);
          return gadget.setSetting('status_list_refresh_id', new_timer_id);
        });
        
      
    });


}(window, rJS, $));