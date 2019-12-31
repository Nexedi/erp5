/*global window, rJS, RSVP*/
/*jslint indent: 2, maxlen: 80 */
(function (window, rJS, RSVP) {
  "use strict";

  var ZONE_LIST = [
    ["GMT-12", "-1200"],
    ["GMT-11", "-1100"],
    ["GMT-10", "-1000"],
    ["GMT-9", "-0900"],
    ["GMT-8", "-0800"],
    ["GMT-7", "-0700"],
    ["GMT-6", "-0600"],
    ["GMT-5", "-0500"],
    ["GMT-4", "-0400"],
    ["GMT-3", "-0300"],
    ["GMT-2", "-0200"],
    ["GMT-1", "-0100"],
    ["GMT", "+0000"],
    ["GMT+1", "+0100"],
    ["GMT+2", "+0200"],
    ["GMT+3", "+0300"],
    ["GMT+4", "+0400"],
    ["GMT+5", "+0500"],
    ["GMT+6", "+0600"],
    ["GMT+7", "+0700"],
    ["GMT+8", "+0800"],
    ["GMT+9", "+0900"],
    ["GMT+10", "+1000"],
    ["GMT+11", "+1100"],
    ["GMT+12", "+1200"]
  ];

  rJS(window)
    .declareAcquiredMethod('getSelectedLanguage', 'getSelectedLanguage')
    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict = {
          value: field_json.value || field_json.default || "",
          editable: field_json.editable,
          required: field_json.required,
          id: field_json.key,
          name: field_json.key,
          key: field_json.key,
          title: field_json.title,
          timezone_style: field_json.timezone_style,
          date_only: field_json.date_only,
          hide_day: field_json.hide_day,
          allow_empty_time: field_json.allow_empty_time,
          ampm_time_style: field_json.ampm_time_style,
          subfield_ampm_key: field_json.subfield_ampm_key,
          subfield_hour_key: field_json.subfield_hour_key,
          subfield_minute_key: field_json.subfield_minute_key,
          hidden_day_is_last_day: field_json.hidden_day_is_last_day,
          subfield_year_key: field_json.subfield_year_key,
          subfield_month_key: field_json.subfield_month_key,
          subfield_day_key: field_json.subfield_day_key,
          subfield_timezone_key: field_json.subfield_timezone_key,
          start_datetime: field_json.start_datetime,
          end_datetime: field_json.end_datetime,
          hidden: field_json.hidden,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var element = this.element.querySelector('.datetimefield'),
        gadget = this,
        date,
        tmp,
        timezone,
        tmp_year,
        tmp_month,
        tmp_date,
        tmp_hour,
        tmp_minute,
        leap_year,
        time = "",
        last_month_date = [
          [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
          [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        ],//leapyear
        queue = new RSVP.Queue(),
        promise_list,
        input_state = {
          name: gadget.state.key,
          editable: gadget.state.editable,
          required: gadget.state.required,
          type: gadget.state.date_only ? "date" : "datetime-local",
          hidden: gadget.state.hidden
        },
        select_state = {
          name: gadget.state.key + '_select',
          value: "+0000",
          item_list: ZONE_LIST,
          editable: gadget.state.editable,
          required: gadget.state.required,
          hidden: gadget.state.hidden
              // name: field_json.key,
              // title: field_json.title
        },
        p_state = {
          tag: "p"
        };

      // Create or fetch sub gadgets
      if (modification_dict.hasOwnProperty('editable') ||
          modification_dict.hasOwnProperty('timezone_style')) {
        if (gadget.state.editable) {
          promise_list = [
            gadget.declareGadget('gadget_html5_input.html', {scope: 'INPUT'})
          ];
          if (gadget.state.timezone_style) {
            promise_list.push(gadget.declareGadget('gadget_html5_select.html',
                                                   {scope: 'SELECT'}));
          }
        } else {
          promise_list = [
            gadget.declareGadget('gadget_html5_element.html', {scope: 'P'})
          ];
        }
        queue
          .push(function () {
            return RSVP.all(promise_list);
          })
          .push(function (result_list) {
            // Clear first to DOM, append after to reduce flickering/manip
            while (element.firstChild) {
              element.removeChild(element.firstChild);
            }
            var i;
            for (i = 0; i < result_list.length; i += 1) {
              element.appendChild(result_list[i].element);
            }
            return result_list;
          });
      } else {
        if (gadget.state.editable) {
          promise_list = [
            gadget.getDeclaredGadget('INPUT')
          ];
          if (gadget.state.timezone_style) {
            promise_list.push(gadget.getDeclaredGadget('SELECT'));
          }
        } else {
          promise_list = [gadget.getDeclaredGadget('P')];
        }
        queue
          .push(function () {
            return RSVP.all(promise_list);
          });
      }

      // Calculate sub gadget states
      //Change type to datetime/datetime local if configured in the field
      if (gadget.state.value) {
        tmp = new Date(gadget.state.value);
        //get date without timezone
        tmp_date = tmp.getUTCDate();
        tmp_month = tmp.getUTCMonth() + 1;
        tmp_year = tmp.getUTCFullYear();

        tmp_hour = tmp.getUTCHours();
        tmp_minute = tmp.getUTCMinutes();

        //timezone required
        //convert time to GMT
        timezone = parseInt(gadget.state.value.slice(-5), 10) / 100;

        if (gadget.state.timezone_style) {
          select_state.value = ZONE_LIST[timezone + 12][1];
        }

        leap_year = (tmp_year % 4 === 0 && tmp_year % 100 !== 0) ? 1 : 0;
        if (timezone !== 0) {
          tmp_hour += timezone;
          if (tmp_hour < 0) {
            tmp_hour += 24;
            tmp_date -= 1;
            if (tmp_date === 0) {
              tmp_month -= 1;
              if (tmp_month === 0) {
                tmp_month = 12;
                tmp_year -= 1;
              }
              tmp_date = last_month_date[leap_year][tmp_month - 1];
            }
          } else if (tmp_hour > 23) {
            tmp_hour -= 24;
            tmp_date += 1;
            if (tmp_date > last_month_date[leap_year][tmp_month - 1]) {
              tmp_date = 1;
              tmp_month += 1;
              if (tmp_month > 12) {
                tmp_month = 1;
                tmp_year += 1;
              }
            }
          }
        }

        if (!gadget.state.date_only) {
          time = "T" + Math.floor(tmp_hour / 10) + tmp_hour % 10 + ":" +
                 Math.floor(tmp_minute / 10) +  (tmp_minute % 10) + ":00";
        }
        date = tmp_year + "-" + Math.floor(tmp_month / 10) +
          (tmp_month % 10) + "-" +
          Math.floor(tmp_date / 10) + (tmp_date % 10);

        input_state.value = date + time;
      }

      // Render
      if (gadget.state.editable) {
        queue
          .push(function (gadget_list) {
            promise_list = [
              gadget_list[0].render(input_state)
            ];
            if (gadget.state.timezone_style) {
              promise_list.push(gadget_list[1].render(select_state));
            }
            return RSVP.all(promise_list);
          });
      } else {
        queue
          .push(function (gadget_list) {
            return RSVP.all([
              gadget.getSelectedLanguage(),
              gadget_list
            ]);
          })
          .push(function (result_list) {
            var language = result_list[0],
              gadget_list = result_list[1],
              text_content = "",
              state_date,
              locale_formatted_state_date,
              offset_time_zone;
            if (gadget.state.value) {
              state_date = new Date(gadget.state.value);
              /* Ideally we would like to use {timeStyle: "short"} as option
               * to hide seconds. Unfortunately it doesn't work in older
               * versions of firefox. Luckily, by using
               *   {hour: "numeric", minute: "numeric"}
               * it hides seconds, and still respects the locale.
               * >> date = new Date(2019, 1, 1, 1, 1)
               * >> date.toLocaleTimeString(
               *      'en', {hour: "numeric", minute: "numeric"}
               *    )
               *    "1:01 AM"
               * >> date.toLocaleTimeString(
               *      'fr', {hour: "numeric", minute: "numeric"}
               *    )
               *    "01:01"
               */
              locale_formatted_state_date = state_date.toLocaleTimeString(
                language,
                {hour: "numeric", minute: "numeric"}
              );
              if (gadget.state.timezone_style) {
                text_content = state_date.toLocaleDateString(language);
                if (!gadget.state.date_only) {
                  text_content += " " + locale_formatted_state_date;
                }
              } else {
                //get timezone difference between server and local browser
                offset_time_zone = timezone + (state_date.getTimezoneOffset() / 60);
                //adjust hour in order to get correct date time string
                state_date.setUTCHours(state_date.getUTCHours() + offset_time_zone);
                text_content = state_date.toLocaleDateString(language);
                if (!gadget.state.date_only) {
                  text_content += " " + locale_formatted_state_date;
                }
              }
            }
            p_state.text_content = text_content;
            // for noneditable element, attach data-date attribute in ISO format
            // so we can use it in tests
            p_state.data = {
              'date': input_state.value
            };
            return gadget_list[0].render(p_state);
          });
      }
      return queue;
    })

    .declareMethod('getContent', function (options) {
      var gadget = this,
        result = {},
        promise_list;
      if (gadget.state.editable) {
        promise_list = [gadget.getDeclaredGadget('INPUT')];
        if (gadget.state.timezone_style) {
          promise_list.push(gadget.getDeclaredGadget('SELECT'));
        }
        return new RSVP.Queue()
          .push(function () {
            return RSVP.all(promise_list);
          })
          .push(function (result_list) {
            var i;
            promise_list = [];
            for (i = 0; i < result_list.length; i += 1) {
              promise_list.push(result_list[i].getContent());
            }
            return RSVP.all(promise_list);
          })
          .push(function (result_list) {
            var value = result_list[0][gadget.state.key],
              timezone = "+0000",
              year,
              month,
              date,
              hour,
              minute,
              j;
            if (gadget.state.timezone_style) {
              timezone = result_list[1][gadget.state.key + '_select'];
            }

            if (options === undefined || options.format === "erp5") {
              if (value !== "") {
                if (gadget.state.date_only === 0) {
                  value += "+0000";
                }
                value = new Date(value);
                year = value.getUTCFullYear();
                month = value.getUTCMonth() + 1;
                date = value.getUTCDate();
                if (gadget.state.hide_day === 1) {
                  date = 1;
                }
                //get time
                if (gadget.state.date_only === 0) {
                  if (gadget.state.allow_empty_time === 1) {
                    hour = 0;
                    minute = 0;
                  } else {
                    hour = value.getUTCHours();
                    minute = value.getUTCMinutes();
                  }
                  if (gadget.state.ampm_time_style === 1) {
                    if (hour > 12) {
                      result[gadget.state.subfield_ampm_key] = "pm";
                      hour -= 12;
                    } else {
                      result[gadget.state.subfield_ampm_key] = "am";
                    }
                  }
                  result[gadget.state.subfield_hour_key] = hour;
                  result[gadget.state.subfield_minute_key] = minute;
                }

                if (gadget.state.hidden_day_is_last_day === 1) {
                  if (month === 12) {
                    year += 1;
                    month = 1;
                  } else {
                    month += 1;
                  }
                }
                result[gadget.state.subfield_year_key] = year;
                result[gadget.state.subfield_month_key] = month;
                result[gadget.state.subfield_day_key] = date;
                if (gadget.state.timezone_style) {
                  //set timezone
                  for (j = 0; j < ZONE_LIST.length; j += 1) {
                    if (timezone === ZONE_LIST[j][1]) {
                      result[gadget.state.subfield_timezone_key] =
                        ZONE_LIST[j][0];
                    }
                  }
                }
              } else {
                //if no value, return empty data
                if (gadget.state.date_only === 0) {
                  result[gadget.state.subfield_hour_key] = "";
                  result[gadget.state.subfield_minute_key] = "";
                }
                result[gadget.state.subfield_year_key] = "";
                result[gadget.state.subfield_month_key] = "";
                result[gadget.state.subfield_day_key] = "";
              }
              return result;
            }
            if (gadget.state.date_only) {
              value += "T00:00";
            }
            result[gadget.state.key] = value + timezone;
            return result;
          });
      }
      return result;
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      var gadget = this;
      if (gadget.state.editable) {
        return gadget.getDeclaredGadget('INPUT')
          .push(function (result) {
            return result.checkValidity();
          });
      }
      return true;
    }, {mutex: 'changestate'});

}(window, rJS, RSVP));