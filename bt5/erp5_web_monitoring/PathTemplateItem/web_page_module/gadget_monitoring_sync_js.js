/*global window, rJS, RSVP, $, clearTimeout, setTimeout, console */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, $, console, clearTimeout, setTimeout) {
  "use strict";

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props =  {};
    })
    /*.ready(function (g) {
      return g.getDeclaredGadget('log_gadget')
        .push(function (log_gadget) {
          g.props.log_gadget = log_gadget;
        });
    })*/

    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("jio_repair", "jio_repair")

    .declareMethod("startSync", function (options) {
      var gadget = this;

      function formatDate(d) {
        function addZero(n) {
          return n < 10 ? "0" + n : n.toString();
        }

        return d.getFullYear() + "-" + addZero(d.getMonth() + 1)
          + "-" + addZero(d.getDate()) + " " + addZero(d.getHours())
          + ":" + addZero(d.getMinutes()) + ":" + addZero(d.getSeconds());
      }
      /*
      function getErrorLog(error_list) {
        // Build error msg from failed sync
        var i,
          tmp_url,
          error_message = "";

        for (i = 0; i < error_list.length; i += 1) {
          if (error_list[i].storage_dict.hasOwnProperty('sub_storage')) {
            if (error_list[i].storage_dict.sub_storage.hasOwnProperty('sub_storage')) {
              tmp_url = error_list[i].storage_dict.sub_storage.sub_storage.url;
            } else {
              tmp_url = error_list[i].storage_dict.sub_storage.url;
            }
          } else {
            tmp_url = error_list[i].storage_dict.url;
          }
          error_message += "> " + error_list[i].storage_dict.hosting + " > " +
            error_list[i].storage_dict.title + "\n";
          error_message += "Cannot download file(s) at " + tmp_url + ".\n\n";
        }
        return error_message;
      }

      function updateStatus(gadget, storage_dict, status) {
        var promise_list = [],
          jio_gadget,
          url,
          i;

        return getJioGadget(gadget, storage_dict)
          .push(function (jio_declared_gadget) {
            jio_gadget = jio_declared_gadget;
            return jio_gadget.allDocs({include_docs: true});
          })
          .push(undefined, function (error) {
            console.log(error);
            return {
              data: {
                total_rows: 0
              }
            };
          })
          .push(function (jio_docs) {
            var tmp;
            for (i = 0; i < jio_docs.data.total_rows; i += 1) {
              if (jio_docs.data.rows[i].id.startsWith('_replicate_')) {
                continue;
              }
              tmp = jio_docs.data.rows[i].doc;
              if (storage_dict.storage_type === "rss") {
                if (tmp.category === "WARNING") {
                  continue;
                }
                tmp.category = "WARNING";
              } else if (storage_dict.storage_type === "webdav") {
                if (tmp.status === "WARNING") {
                  continue;
                }
                tmp.status = "WARNING";
              }
              promise_list.push(jio_gadget.put(
                jio_docs.data.rows[i].id,
                tmp
              ));
            }
            return RSVP.all(promise_list);
          })
          .push(undefined, function (error) {
            console.log("ERROR: update status to WARNING");
            console.log(error);
          });
      }*/

      function syncAllStorage() {
        var error_log,
          last_sync_time;
        gadget.props.started = true;
        return new RSVP.Queue()
          .push(function () {
            return gadget.setSetting('sync_start_time', new Date().getTime());
          })
          .push(function () {
            $(".notifyjs-wrapper").remove();
            return $.notify(
              "Synchronizing Data...",
              {
                position: "bottom right",
                autoHide: false,
                className: "info"
              }
            );
          })
          .push(function () {
            // call repair on storage
            return gadget.jio_repair();
          })
          .push(undefined, function (error) {
            error_log = error;
            console.error(error);
            return false;
          })
          .push(function () {
            last_sync_time = new Date().getTime();
            return gadget.setSetting('latest_sync_time', last_sync_time);
          })
          .push(function () {
            var time = 3000,
              classname = "info",
              message = "Synchronisation finished.",
              //log_message = '',
              log_title = "OK: " + message;

            if (error_log !== undefined) {
              classname = "warning";
              time = 5000;
              //log_message = getErrorLog(gadget.props.error_list);
              log_title = "Synchronisation finished with error(s).";
              message = log_title + "\nYou can retry with manual sync.";
            }
            $(".notifyjs-wrapper").remove();
            return RSVP.all([$.notify(
              message,
              {
                position: "bottom right",
                autoHide: true,
                className: classname,
                autoHideDelay: time
              }
            )]);
              /*gadget.props.log_gadget.log({
                message: log_message,
                type: classname,
                title: log_title,
                method: 'Monitoring Sync'
              })*/
          })
          /*.push(function () {
            var promise_list = [],
              i;
            // Update all failures monitoring status to Warning
            for (i = 0; i < gadget.props.error_list.length; i += 1) {
              promise_list.push(updateStatus(
                gadget,
                gadget.props.error_list[i].storage_dict,
                'WARNING'
              ));
            }
            return RSVP.all(promise_list);
          })*/
          .push(function () {
            gadget.props.started = false;
            return $.notify(
              "Last Sync: " + formatDate(new Date(last_sync_time)),
              {
                position: "bottom right",
                autoHide: true,
                className: "success",
                autoHideDelay: 30000
              }
            );
          });
      }

      function syncDataTimer() {
        if (gadget.props.timer) {
          clearTimeout(gadget.props.timer);
        }
        gadget.props.timer = setTimeout(function () {
          return new RSVP.Queue()
            .push(function () {
              return gadget.getSetting('sync_start_time');
            })
            .push(function (start_timestamp) {
              var current_time = new Date().getTime();
              if (start_timestamp !== undefined &&
                  (current_time - gadget.props.timer_interval)
                  <= start_timestamp) {
                // There was a recent sync don't start a new sync before the time_interval!
                return;
              }
              return syncAllStorage();
            })
            .push(undefined, function (error) {
              console.error(error);
              return;
            })
            .push(function () {
              return gadget.getSetting('sync_data_interval');
            })
            .push(function (timer_interval) {
              if (timer_interval === undefined) {
                timer_interval = gadget.props.default_sync_interval;
              }
              gadget.props.timer_interval = timer_interval;
              return syncDataTimer();
            });
        }, gadget.props.timer_interval);
        return gadget.props.timer;
      }


      if (options === undefined) {
        options = {};
      }
      if (options.query === undefined) {
        options.query = {
          include_docs: true
        };
      }

      if (options.now) {
        if (gadget.props.started) {
          // sync is running...
          return;
        }
        return syncAllStorage();
      }
      // Default sync interval to 5 minutes
      gadget.props.default_sync_interval = 300000;
      gadget.props.has_sync_interval = false;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getSetting('sync_data_interval');
        })
        .push(function (timer_interval) {
          if (timer_interval === undefined) {
            // quickly sync because this is the first run!
            gadget.props.timer_interval = 10000;
          } else {
            gadget.props.timer_interval = timer_interval;
            gadget.props.has_sync_interval = true;
          }
          return gadget.getSetting('latest_sync_time');
        })
        .push(function (latest_sync_time) {
          var current_time = new Date().getTime(),
            time_diff;
          if (latest_sync_time !== undefined) {
            time_diff = current_time - latest_sync_time;
            if ((time_diff - 10000) >= gadget.props.timer_interval) {
              // sync in after 10 second
              gadget.props.timer_interval = 10000;
            } else {
              gadget.props.timer_interval = gadget.props.timer_interval - time_diff;
            }
          }
          if (!gadget.props.has_sync_interval) {
            return gadget.setSetting('sync_data_interval',
              gadget.props.default_sync_interval);
          }
        })
        .push(function () {
          return syncDataTimer();
        });
    });

}(window, rJS, RSVP, $, console, clearTimeout, setTimeout));