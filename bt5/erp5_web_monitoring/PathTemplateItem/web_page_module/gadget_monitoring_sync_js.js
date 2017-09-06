/*global window, rJS, RSVP, $, clearTimeout, setTimeout, console, XMLHttpRequest, document */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, $, console, clearTimeout, setTimeout,
  XMLHttpRequest, document) {
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

      function testOnline(url) {
        return new RSVP.Promise(function (resolve, reject) {
          var xhr = new XMLHttpRequest();

          xhr.onload = function (event) {
            var response = event.target;
            if (response.status === 302 || response.status === 200) {
              resolve({status: 'OK'});
            } else {
              reject({
                status: 'ERROR'
              });
            }
          };

          xhr.onerror = function (e) {
            reject({
              status: 'ERROR'
            });
          };

          xhr.open("GET", url, true);
          xhr.send("");
        });
      }

      function formatDate(d) {
        function addZero(n) {
          return n < 10 ? "0" + n : n.toString();
        }

        return d.getFullYear() + "-" + addZero(d.getMonth() + 1)
          + "-" + addZero(d.getDate()) + " " + addZero(d.getHours())
          + ":" + addZero(d.getMinutes()) + ":" + addZero(d.getSeconds());
      }

      function syncAllStorageWithCheck() {
        gadget.props.offline = false;
        return gadget.getSetting('sync_check_offline', 'true')
          .push(function (check_offline) {
            var parser;
            if (check_offline === 'true') {
              parser = document.createElement("a");
              parser.href = document.URL;
              return new RSVP.Queue()
                .push(function () {
                  return testOnline(parser.origin);
                })
                .push(undefined, function() {
                  return {status: "ERROR"};
                })
                .push(function (online_result) {
                  if (online_result.status === "OK") {
                    return syncAllStorage();
                  }
                  gadget.props.offline = true;
                  return $.notify(
                    "Sync aborted, no internet access...",
                    {
                      position: "bottom right",
                      autoHide: true,
                      className: "error",
                      autoHideDelay: 10000
                    }
                  );
                });
            }
            return syncAllStorage();
          });
      }

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
              return syncAllStorageWithCheck();
            })
            .push(undefined, function (error) {
              console.error(error);
              return;
            })
            .push(function () {
              return gadget.getSetting('sync_data_interval');
            })
            .push(function (timer_interval) {
              if (gadget.props.offline === true) {
                // Offline mode detected, next check will be in 3 minutes
                timer_interval = 180000;
              } else if (timer_interval === undefined) {
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
        return syncAllStorageWithCheck();
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

}(window, rJS, RSVP, $, console, clearTimeout, setTimeout, XMLHttpRequest,
  document));