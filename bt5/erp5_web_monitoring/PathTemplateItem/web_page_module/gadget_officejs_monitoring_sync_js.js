/*global window, rJS, RSVP, console, XMLHttpRequest, document */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, console, XMLHttpRequest, document) {
  "use strict";

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props =  {};
    })

    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("jio_repair", "jio_repair")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    .declareMethod("register", function (options) {
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

          xhr.onerror = function () {
            reject({
              status: 'ERROR'
            });
          };

          xhr.open("GET", url, true);
          xhr.send("");
        });
      }

      function syncAllStorage() {
        var has_error = false,
          last_sync_time;
        gadget.props.started = true;
        return new RSVP.Queue()
          .push(function () {
            return gadget.setSetting('sync_start_time', new Date().getTime());
          })
          .push(function () {
            return gadget.notifySubmitting();
          })
          .push(function () {
            return gadget.notifySubmitted({
              message: "Synchronizing Data...",
              status: "success"
            });
          })
          .push(function () {
            // call repair on storage
            return gadget.jio_repair();
          })
          .push(undefined, function (error) {
            // should include error message in error
            has_error = true;
            console.error(error);
            // return false so it will trigger the next run
            return false;
          })
          .push(function () {
            last_sync_time = new Date().getTime();
            return RSVP.all([
              gadget.setSetting('latest_sync_time', last_sync_time),
              gadget.notifySubmitting()
            ]);
          })
          .push(function () {
            var classname = "success",
              message = "Synchronisation finished.";

            if (has_error) {
              classname = "error";
              message = "Synchronisation finished with error(s).";
              message += " \nYou can retry with manual sync.";
            }
            return gadget.notifySubmitted({
              message: message,
              status: classname
            });
          })
          .push(function () {
            gadget.props.started = false;
            /*return $.notify(
              "Last Sync: " + formatDate(new Date(last_sync_time)),
              {
                position: "bottom right",
                autoHide: true,
                className: "success",
                autoHideDelay: 30000
              }
            );*/
          });
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
                .push(undefined, function () {
                  return {status: "ERROR"};
                })
                .push(function (online_result) {
                  if (online_result.status === "OK") {
                    return syncAllStorage();
                  }
                  gadget.props.offline = true;
                });
            }
            return syncAllStorage();
          });
      }

      function syncDataTimer() {
        return new RSVP.Queue()
          .push(function () {
            return RSVP.delay(gadget.props.timer_interval);
          })
          .push(function () {
            return gadget.getSetting('sync_start_time');
          })
          .push(function (start_timestamp) {
            var current_time = new Date().getTime();
            if (start_timestamp !== undefined &&
                (current_time - gadget.props.timer_interval) <=
                start_timestamp) {
              // There was another recent sync don't start a new sync before the time_interval!
              return;
            }
            return gadget.getSetting('sync_lock')
              .push(function (sync_lock) {
                if (!sync_lock) {
                  gadget.props.sync_locked = false;
                  return syncAllStorageWithCheck();
                }
                gadget.props.sync_locked = true;
                return gadget.notifySubmitted({
                  message: "Auto sync is currently locked by another task " +
                    "and will be restarted later...",
                  status: "error"
                });
              });
          })
          .push(function () {
            return gadget.getSetting('sync_data_interval');
          })
          .push(function (timer_interval) {
            if (gadget.props.offline === true ||
                gadget.props.sync_locked === true) {
              // Offline mode detected or sync locked. Next run in 1 minute
              timer_interval = 60000;
            } else if (timer_interval === undefined) {
              timer_interval = gadget.props.default_sync_interval;
            }
            gadget.props.timer_interval = timer_interval;
            return syncDataTimer();
          });
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

}(window, rJS, RSVP, console, XMLHttpRequest, document));