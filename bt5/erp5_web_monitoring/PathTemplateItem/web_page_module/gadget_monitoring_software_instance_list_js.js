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
      return gadget.getDeclaredGadget("listview")
        .push(function (listbox_gadget) {
          gadget.property_dict.listview = listbox_gadget;
        });
    })
    .declareMethod('render', function (options) {
      var gadget = this,
        header = {
          "title": 'Software Instances List'
        },
        listview_options = {
          search_page: 'software_instance_list',
          search: options.search,
          filter: options.filter,
          selection: '',
          view: 'software_instance_view',
          filter_column: {select: "status", "title": "Status"},
          column_list: [{
            select: 'status',
            title: 'Status',
            template: ' <span class="label label-{{value}}">{{value}}</span>',
            css_class: 'ui-text-center'
          }, {
            title: 'Software Instance',
            select: 'title'
          }, {
            title: 'Hosting Subscription',
            select: 'hosting-title'
          }, {
            select: 'date',
            title: 'Status Date',
            convertDate: false
          }],
          query: {
            select_list: ['title', 'status', 'date', 'hosting-title'],
            query: '(portal_type:"global") AND (active:true)',
            sort_on: [["hosting-title", "ascending"]]
          }
        };

      gadget.property_dict.options = options;
      return gadget.updateHeader(header)
        .push(function () {
          return gadget.property_dict.listview.render(listview_options);
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("renderApplication", "renderApplication")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
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
            if (hash.indexOf('page=software_instance_list') >= 0) {
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