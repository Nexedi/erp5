/*global window, rJS, RSVP, document, loopEventListener */
/*jslint indent: 2 */
(function (window, rJS, RSVP, document, loopEventListener) {
  "use strict";
  rJS(window)
    .ready(function (gadget) {
      return gadget.getElement()
        .push(function (element) {
          gadget.element = element;
          gadget.props = {};
        });
    })
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareMethod('getTextContent', function () {
      return this.element.querySelector('input').getAttribute('value') || "";
    })
    .declareMethod('render', function (options) {
      var input = this.element.querySelector('input'),
        date,
        tmp,
        timezone,
        tmp_year,
        tmp_month,
        tmp_date,
        tmp_hour,
        tmp_minute,
        select,
        time = "",
        leapyear,
        i,
        field_json = options.field_json || {},
        lastDateOfMonth = [[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
                           [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]],//leapyear
        select_options = ["GMT-12", "GMT-11", "GMT-10", "GMT-9", "GMT-8", "GMT-7", "GMT-6",
                   "GMT-5", "GMT-4", "GMT-3", "GMT-2", "GMT-1", "GMT", "GMT+1",
                   "GMT+2", "GMT+3", "GMT+4", "GMT+5", "GMT+6", "GMT+7", "GMT+8",
                   "GMT+9", "GMT+10", "GMT+11", "GMT+12"],
        select_option,
        value = field_json.value || field_json.default || "";
      this.props.field_json = field_json;


      if (field_json.timezone_style) {
        //change date to local
        select = document.createElement("select");
        for (i = 0; i < select_options.length; i += 1) {
          select_option = document.createElement("option");
          select_option.value = select_options[i];
          select_option.innerHTML = select_options[i];
          select.appendChild(select_option);
        }
        select.setAttribute("class", "gmt_select");
        select.selectedIndex = 12;
        this.element.appendChild(select);
      }
      if (field_json.date_only === 0) {
        input.setAttribute("type", "datetime-local");
      }
      //Change type to datetime/datetime local if configured in the field
      if (value !== "") {
        tmp = new Date(value);
        //get date without timezone
        tmp_date = tmp.getUTCDate();
        tmp_month = tmp.getUTCMonth() + 1;
        tmp_year = tmp.getUTCFullYear();

        tmp_hour = tmp.getUTCHours();
        tmp_minute = tmp.getUTCMinutes();

        //timezone required
        //convert time to GMT
        timezone = parseInt(value.slice(-5), 10) / 100;

        if (field_json.timezone_style) {
          select.selectedIndex = timezone + 12;
        }
        leapyear = (tmp_year % 4 === 0 && tmp_year % 100 !== 0) ? 1 : 0;
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
              tmp_date = lastDateOfMonth[leapyear][tmp_month - 1];
            }
          } else if (tmp_hour > 23) {
            tmp_hour -= 24;
            tmp_date += 1;
            if (tmp_date > lastDateOfMonth[leapyear][tmp_month - 1]) {
              tmp_date = 1;
              tmp_month += 1;
              if (tmp_month > 12) {
                tmp_month = 1;
                tmp_year += 1;
              }
            }
          }
        }
        if (field_json.date_only === 0) {
          time = "T" + Math.floor(tmp_hour / 10) + tmp_hour % 10 + ":"
              + Math.floor(tmp_minute / 10) +  (tmp_minute % 10) + ":00";
        }
        date = tmp_year + "-" + Math.floor(tmp_month / 10) + (tmp_month % 10) + "-"
               +  Math.floor(tmp_date / 10) + (tmp_date % 10);

        input.setAttribute(
          'value',
          date + time
        );
      }
      input.setAttribute('name', field_json.key);
      input.setAttribute('title', field_json.title);
      if (field_json.required === 1) {
        input.setAttribute('required', 'required');
      }
      if (field_json.editable !== 1) {
        input.setAttribute('readonly', 'readonly');
        input.setAttribute('data-wrapper-class', 'ui-state-disabled ui-state-readonly');
        input.setAttribute('disabled', 'disabled');
      }
    })
    .declareMethod('getContent', function (options) {
      var input = this.element.querySelector('input'),
        result = {},
        select,
        year,
        month,
        field_json = this.props.field_json,
        date,
        hour,
        minute,
        timezone,
        zone_list = {"GMT-12": "-1200", "GMT-11": "-1100",
                   "GMT-9": "-0900", "GMT-8": "-0800",
                   "GMT-7": "-0700", "GMT-6": "-0600",
                   "GMT-5": "-0500", "GMT-4": "-0400",
                   "GMT-3": "-0300", "GMT-2": "-0200",
                   "GMT-1": "-0100", "GMT": "+0000",
                   "GMT+1": "+0100", "GMT+2": "+0200",
                   "GMT+3": "+0300", "GMT+4": "+0400",
                   "GMT+5": "+0500", "GMT+6": "+0600",
                   "GMT+7": "+0700", "GMT+8": "+0800",
                   "GMT+9": "+0900", "GMT+10": "+1000",
                   "GMT+11": "+1100", "GMT+12": "+1200"},
        value = input.value;
      if (options === undefined || options.format === "erp5") {
        if (value !== "") {
          if (field_json.date_only === 0) {
            value += "+0000";
          }
          value = new Date(value);
          year = value.getUTCFullYear();
          month = value.getUTCMonth() + 1;
          date = value.getUTCDate();
          if (field_json.hide_day === 1) {
            date = 1;
          }
          //get time
          if (field_json.date_only === 0) {
            if (field_json.allow_empty_time === 1) {
              hour = 0;
              minute = 0;
            } else {
              hour = value.getUTCHours();
              minute = value.getUTCMinutes();
            }
            if (field_json.ampm_time_style === 1) {
              if (hour > 12) {
                result[field_json.subfield_ampm_key] = "pm";
                hour -= 12;
              } else {
                result[field_json.subfield_ampm_key] = "am";
              }
            }
            result[field_json.subfield_hour_key] = hour;
            result[field_json.subfield_minute_key] = minute;
          }

          if (field_json.hidden_day_is_last_day === 1) {
            if (month === 12) {
              year += 1;
              month = 1;
            } else {
              month += 1;
            }
          }
          result[field_json.subfield_year_key] = year;
          result[field_json.subfield_month_key] = month;
          result[field_json.subfield_day_key] = date;
          if (field_json.timezone_style) {
            //set timezone
            select = this.element.querySelector("select");
            result[field_json.subfield_timezone_key] = select.options[select.selectedIndex].value;
          }
        } else {
          //if no value, return empty data
          if (field_json.date_only === 0) {
            result[field_json.subfield_hour_key] = "";
            result[field_json.subfield_minute_key] = "";
          }
          result[field_json.subfield_year_key] = "";
          result[field_json.subfield_month_key] = "";
          result[field_json.subfield_day_key] = "";
        }
        return result;
      }
      if (field_json.date_only_style) {
        result[field_json.key] = value;
        return result;
      }
      if (field_json.date_only) {
        value += "T00:00";
      }
      if (field_json.timezone_style) {
        //set timezone
        select = this.element.querySelector("select");
        timezone = select.options[select.selectedIndex].value;
      } else {
        timezone = "GMT";
      }
      result[field_json.key] = value + zone_list[timezone];
      return result;
    })
    .declareMethod('checkValidity', function () {
      var gadget = this,
        valide = true,
        start_datetime = false,
        end_datetime = false,
        datetime_string,
        select = gadget.element.querySelector("select"),
        datetime,
        input = gadget.element.querySelector('input'),
        field_json = gadget.props.field_json;
      if (!input.checkValidity()) {
        return false;
      }
      return new RSVP.Queue()
        .push(function () {
          return gadget.notifyValid();
        })
        .push(function () {
          return gadget.getContent();
        })
        .push(function (result) {
          datetime_string = result[field_json.subfield_month_key];
          datetime_string += "," + result[field_json.subfield_day_key];
          datetime_string += "," + result[field_json.subfield_year_key];
          if (field_json.date_only === 0) {
            if (result[field_json.subfield_ampm_key] === "pm") {
              result[field_json.subfield_hour_key] += 12;
            }
            datetime_string += " " + result[field_json.subfield_hour_key];
            datetime_string += ":" + result[field_json.subfield_minute_key] + ":00";
            datetime_string += "+0000";
          }
          if (datetime_string.indexOf("NaN") !== -1) {
            valide = false;
            return gadget.notifyInvalid("Invalide DateTime");
          }
          if (field_json.start_datetime) {
            start_datetime = Date.parse(field_json.start_datetime);
          }
          if (field_json.end_datetime) {
            end_datetime = Date.parse(field_json.end_datetime);
          }
          if ((start_datetime === false) && (end_datetime === false)) {
            return;
          }
          datetime = Date.parse(datetime_string);
          datetime -= (select.selectedIndex - 12) * 60 * 60 * 1000;
          if (start_datetime) {
            if (start_datetime > datetime) {
              valide = false;
              return gadget.notifyInvalid("The date and time you entered earlier than the start time");
            }
          }
          if (end_datetime) {
            if (end_datetime <= datetime) {
              valide = false;
              return gadget.notifyInvalid("The date and time you entered later than the end time");
            }
          }
        })
        .push(function () {
          return valide;
        });
    })
     .declareService(function () {
      ////////////////////////////////////
      // Inform when the field input is invalid
      ////////////////////////////////////
      var field_gadget = this;

      function notifyInvalid(evt) {
        return field_gadget.notifyInvalid(evt.target.validationMessage);
      }

      // Listen to input change
      return loopEventListener(
        field_gadget.element.querySelector('input'),
        'invalid',
        false,
        notifyInvalid
      );
    });

}(window, rJS, RSVP, document, loopEventListener));