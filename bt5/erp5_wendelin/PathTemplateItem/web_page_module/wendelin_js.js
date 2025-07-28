 /*globals rJS, RSVP, Float32Array, Float64Array, URI, nj, location, $*/
/*jslint indent: 2, nomen: true, maxlen: 80*/

(function(window){
  'use strict';

  function define_wendelin () {
    var wendelin = {},
      hateoas_url = "hateoas/",
      ARRAY_VALUE_LENGTH = 8,
      DTYPE_DICT = {
        'float64' : Float64Array,
        'float32' : Float32Array
      };
    wendelin.ARRAY_TYPE_DICT = {
      'STRUCTURE_ARRAY': 'STRUCTURE_ARRAY',
      'NORMAL_ARRAY'   : 'NORMAL_ARRAY'
    };
    wendelin.DATE_FORMAT = {
      'NumpyDateTime64'       : 'NumPyDateTime64',
      'SpecialInteger64Time'  : 'SpecialInteger64Time'
    };
    wendelin.RESOLUTION_DICT = {
      '1_min' : 1000 * 60,
      '5_min' : 1000 * 60 * 5,
      '10_min' : 1000 * 60 * 10,
      '15_min' : 1000 * 60 * 15,
      '30_min' : 1000 * 60 * 30,
      '60_min' : 1000 * 60 * 60,
      '1_day' : 1000 * 60 * 60 * 24
    };
    wendelin.TIME_PRECISION = 16;
    wendelin.ARRAY_DATA_PRECISION = 7;
    wendelin.RELATED_RESOLUTION_DICT = {
      'S' : 1000
      //xxx to be defined
    };

   function convertNumpyDateTime64ToPandasDateIndex(date_position, array, array_length, array_width, Dtype) {
     var line,
       Uint32,
       msb,
       lsb,
       value_list;
     function convertFromBaseToBase(str, fromBase, toBase){
       var num = parseInt(str, fromBase);
       return num.toString(toBase);
     }
     if (Dtype !== DTYPE_DICT.float64) {
       //not yet test with float32
       return;
     }
     Uint32 = Uint32Array;
     for (line = 0; line < array_length; line += 1) {
       value_list = new Uint32(new Dtype([array[line* array_width + date_position]]).buffer);
       lsb = convertFromBaseToBase(value_list[0], 10, 2);
       //overflow of number
       while(lsb.length < 32) {
         lsb = '0' + lsb;
       }
       msb = convertFromBaseToBase(value_list[1] , 10, 2);
       array[line* array_width + date_position] = convertFromBaseToBase(msb + lsb , 2, 10);
     }
    }

    function generateNumberFormat(array, array_length, array_width) {
      var line,
        i,
        position,
        value;
      for (line = 0; line < array_length; line += 1) {
        for (position = 0; position < array_width; position += 1) {
           value = array[line* array_width + position];
           if (value % 1 !== 0) {
             //float
             i = 0;
             if (Math.abs(value) < 1) {
               while(Math.abs(value) < 1) {
                 i += 1;
                 value *= 10;
               }
               i -= 1;
             }
             if (i > 17) {
               i = 17;
             }
             array[line* array_width + position] = array[line* array_width + position].toFixed(3 + i);
           }
        }
      }
    }

    wendelin.asNormalArray = function (doc, column_list) {
      var i,
        include_name = false,
        array_dtype,
        array_width,
        isFloat64Array = false,
        tmp_value,
        include_dtype_length_list = [],
        array_column = [];
      doc.date_index_list = [];
      //numpy "structured array"
      if (!doc.array_dtype) {
        //XXXXXXXXXXX REMOVE
        doc.array_dtype = "[('date', '<M8[ns]')]";
        doc.array_shape = [0];
      }
      if (DTYPE_DICT[doc.array_dtype] === undefined) {
        array_dtype = doc.array_dtype;
        if (array_dtype.substring(0, 9) === "{'names':") {
          // array_dtype = {'names':[..], 'formats':[...], 'offsets':[...], 'itemsize': }
          array_dtype = array_dtype.replace(new RegExp("'", 'g'), '"');
          array_dtype = JSON.parse(array_dtype);
          for (i = 0; i < array_dtype.names.length; i += 1) {
            array_column.push([array_dtype.names[i], array_dtype.names[i]]);
            if (array_dtype.formats[i] === '<f8') {
              isFloat64Array = true;
            }
            //<M8[ns], <M8[ms]........
            if (array_dtype.formats[i].indexOf('<M8') === 0) {
              doc.date_format = wendelin.DATE_FORMAT.NumpyDateTime64;
              doc.date_index_list.push(array_dtype.names[i]);
            }
          }
        } else {
          //remove [ ]
          array_dtype = doc.array_dtype.substring(1, doc.array_dtype.length - 1);
          if (array_dtype[0] === '(' && array_dtype[1] === '(') {
            include_name = true;
          }
          //remove ( ) ' and get array
          //array_dtype = ["'date'", "'<f8'", "'mdbs.eis'", "'<f8'"......]
          array_dtype = array_dtype.replace(/\(/g, '').replace(/\)/g, '').replace(/\'/g, '').split(', ');
          
          if (include_name) {
             for (i = 0; i < array_dtype.length; i += 3) {
              array_column.push([array_dtype[i+1], array_dtype[i]]);
              if (array_dtype[i + 2] === '<f8') {
                isFloat64Array = true;
              }
              if (array_dtype[i + 2].indexOf('<M8') === 0) {
                doc.date_format = wendelin.DATE_FORMAT.NumpyDateTime64;
                doc.date_index_list.push(array_dtype[i+1]);
              }
            }
          } else {
            
            for (i = 0; i < array_dtype.length; i += 2) {
              array_column.push([array_dtype[i], array_dtype[i]]);
              //a multi array dtype, like: "('event_begin', '<M8[ns]'), ('event_end', '<M8[ns]'), ('Terz', [('1,0_Hz', '<f8'), ('1,26_Hz', '<f8')], (3,))"
              if (array_dtype[i + 1].indexOf('[') === 0) {
                tmp_value = 0;
                for (i += 1; i < array_dtype.length; i += 2) {
                  tmp_value += 1;
                  if (array_dtype[i + 1] === '<f8') {
                    isFloat64Array = true;
                  } else { 
                    // ('1,26_Hz', '<f8')], (3,))
                    if (array_dtype[i + 1].endsWith(']')) {
                      //(3,)
                      i += 2;
                      tmp_value *= parseInt(array_dtype[i]);
                      tmp_value -= 1;
                      include_dtype_length_list.push(tmp_value);
                    }
                  }
                  
                }
                
              } else {
                if (array_dtype[i + 1] === '<f8') {
                  isFloat64Array = true;
                }
                else if (array_dtype[i + 1].indexOf('<M8') === 0) {
                  doc.date_format = wendelin.DATE_FORMAT.NumpyDateTime64;
                  doc.date_index_list.push(array_dtype[i]);
                }
                else if (array_dtype[i + 1].indexOf('<i8') === 0 && column_list && (column_list[0] === "date" || column_list[0] === "start_date")) { // add extra check for column list
                  isFloat64Array = true;
                  doc.date_format = wendelin.DATE_FORMAT.SpecialInteger64Time;
                  doc.date_index_list.push(array_dtype[i]);
                }
                else if(column_list !== undefined && column_list[0] != "date" && column_list[0] != "start_date") {  ///// ETERI maybe else if every where!! 
                  isFloat64Array = false;
                }
              }
            }
          }
        }

        if (isFloat64Array) {
          doc.array_dtype = 'float64';
        } else {
          doc.array_dtype = 'float32';
        }
        doc.array_shape.push(array_column.length + include_dtype_length_list.reduce(function(a, b) { return a + b; }, 0));
        doc.array_column = array_column;
        doc.array_type =  wendelin.ARRAY_TYPE_DICT.STRUCTURE_ARRAY;
      } else {
        array_column = [['date', 'Date']];
        if (doc.array_shape.length == 1) {
          array_width = 1;
        } else {
          array_width = doc.array_shape[1];
        }
        for (i = 1; i < array_width; i += 1) {
            array_column.push([i.toString(), i.toString()]);
        }
        doc.array_column = array_column;
        doc.array_type = wendelin.ARRAY_TYPE_DICT.NORMAL_ARRAY;
      }
      return doc;
    };
    wendelin.getMultiArraySlice = function (
      gadget,
      key_list,
      start_date_list,
      stop_date_list,
      column_list,
      time_zone_offset_list = [],
      ) {
        var Dtype_list = [],
        date_format_list = [],
        date_index_list = [],
        frequency,
        frequency_unit,
        array_start_date,
        array_width_list = [],
        start_index,
        stop_index,
        array_length,
        start,
        end,
        length,
        array,
        i,
        j,
        start_date_tmp,
        stop_date_tmp,
        list,
        result_list,
        missing_list = [],
        today = (new Date()).getTime(),
        url_list = [];
      return gadget.getSetting("hateoas_url")
        .push(function (hateoas_url) {
          list = [];
          for (i = 0; i < key_list.length; i += 1) {
            url_list.push(
               (new URI(hateoas_url)).absoluteTo(location.href).toString() + key_list[i] +
            //add timestamp to url to not hit browser cache
            ((/\?/).test(url_list[i]) ? "&" : "?") + today
            );
            list.push(gadget.jio_get(key_list[i]));
          }
          return RSVP.all(list);
        })
        .push(function (doc_list) {
          result_list = doc_list;
          list = [];
          for (i = 0; i < doc_list.length; i += 1) {
            if (!doc_list[i].related_variation) {
              missing_list.push(i);
              //get first two raws
              list.push(wendelin.getArrayRawSlice(gadget, key_list[i], 0, 1));
              list.push(wendelin.getArrayRawSlice(gadget, key_list[i], 1, 2));
            }
          }
          return RSVP.all(list);
        })
        .push(function (raws_list) {
          for (i = 0; i < missing_list.length; i += 1) {
            result_list[missing_list[i]].related_variation = (raws_list[i * 2 + 1].data[0] - raws_list[i * 2 ].data[0]) / 1000 + " S";
          }
          return result_list;
        })
        .push(function (doc_list) {
          list = [];
          for (i = 0; i < doc_list.length;  i += 1) {
            doc_list[i] = wendelin.asNormalArray(doc_list[i]);
            date_index_list.push(doc_list[i].date_index_list);
            Dtype_list.push(DTYPE_DICT[doc_list[i].array_dtype]);
            date_format_list.push(doc_list[i].date_format);
            [frequency, frequency_unit] = doc_list[i].related_variation.split(' ');
            frequency_unit = wendelin.RELATED_RESOLUTION_DICT[frequency_unit];
            array_start_date = new Date(doc_list[i].start_date);
            if (doc_list[i].array_shape.length == 1) {
              array_width_list.push(1);
            } else if (doc_list[i].array_shape.length == 2) {
              array_width_list.push(doc_list[i].array_shape[1]);
            }
            url_list[i] += ((/\?/).test(url_list[i]) ? "&" : "?") + (new Date()).getTime();


            if(time_zone_offset_list[i]) {
              start_date_list[i].setUTCHours(start_date_list[i].getUTCHours() - time_zone_offset_list[i]);
              stop_date_list[i].setUTCHours(stop_date_list[i].getUTCHours() - time_zone_offset_list[i]);
            }

            if (start_date_list[i] < array_start_date) {
                stop_date_tmp = new Date(array_start_date.valueOf() +
                                 stop_date_list[i].valueOf() - start_date_list[i].valueOf());
                start_date_tmp = array_start_date;
            } else {
              stop_date_tmp = stop_date_list[i];
              start_date_tmp = start_date_list[i];
            }
            start_index = Math.floor((start_date_tmp - array_start_date) / (frequency_unit * frequency));
            stop_index= Math.floor((stop_date_tmp - array_start_date) / (frequency_unit * frequency) + 1);
            url_list[i] +=  "&slice_index.start:records:int=" + start_index + "&slice_index.stop:records:int=" + stop_index;

            if (doc_list[i].array_type === wendelin.ARRAY_TYPE_DICT.STRUCTURE_ARRAY && column_list[i].length) {
              array_width_list[i] = column_list[i].length;
              for (j = 0; j < column_list[i].length; j += 1) {
                url_list[i] += "&list_index:list=" + column_list[i][j];
              }
            }
            list.push(gadget.jio_getAttachment("erp5", url_list[i], {
               format : "array_buffer"
            }));
          }
           return RSVP.all(list);
        })
        .push(function (buffer_list) {
          var result_list = [],
            index,
            k,
            array;
          for (i = 0; i < buffer_list.length; i += 1) {
             array_length = Math.floor(
               buffer_list[i].byteLength / array_width_list[i] / Dtype_list[i].BYTES_PER_ELEMENT
             );
             array = new Dtype_list[i](buffer_list[i]);
             if (date_format_list[i] === wendelin.DATE_FORMAT.NumpyDateTime64) {
               for (j = 0; j < column_list[i].length; j += 1) {
                 if (date_index_list[i].indexOf(column_list[i][j]) !== -1) {
                   convertNumpyDateTime64ToPandasDateIndex(j, array, array_length, array_width_list[i], Dtype_list[i]);
                 }
               }
             }
             generateNumberFormat(array, array_length, array_width_list[i]);
             result_list.push(nj.ndarray(array, [array_length, array_width_list[i]]));
          }
         return result_list;
        })
        .push(undefined, function (error) {
          if (! (error instanceof RSVP.CancellationError)) {
            console.error("following data array is not good: ");
            console.error(key_list);
          }
          return [nj.ndarray([0], [1, 1])];
        });
      };
    wendelin.getArraySlice = function (
      gadget,
      key,
      start_date,
      stop_date
    ) {
      var Dtype,
        resolution,
        array_start_date,
        array_width,
        start_index,
        stop_index,
        array_length,
        start,
        end,
        length,
        array,
        url;
      return gadget.getSetting("hateoas_url")
        .push(function (hateoas_url) {
          url =
            (new URI(hateoas_url)).absoluteTo(location.href).toString() + key +
            //add timestamp to url to not hit browser cache
            ((/\?/).test(url) ? "&" : "?") + (new Date()).getTime();
          return gadget.jio_get(key);
        })
        .push(function (doc) {
          doc = wendelin.asNormalArray(doc);
          Dtype = DTYPE_DICT[doc.array_dtype];
          resolution = wendelin.RESOLUTION_DICT[doc.resolution];
          array_start_date = new Date(doc.start_date);
          if (doc.array_shape.length == 1) {
            array_width = 1;
          } else if (doc.array_shape.length == 2) {
            array_width = doc.array_shape[1];
          }
          url += ((/\?/).test(url) ? "&" : "?") + (new Date()).getTime();
          if (start_date < array_start_date) {
            stop_date = new Date(array_start_date.valueOf() +
                                 stop_date.valueOf() - start_date.valueOf());
            start_date = array_start_date;
          }
          start_index = Math.floor((start_date - array_start_date) / resolution);
          stop_index = Math.floor((stop_date - array_start_date) / resolution);
          start = start_index * array_width * Dtype.BYTES_PER_ELEMENT;
          end = (stop_index + 1) * array_width * Dtype.BYTES_PER_ELEMENT;
          return gadget.jio_getAttachment("erp5", url, {
            start : start,
            end : end -1,
            format : "array_buffer"
          });
        })
        .push(function (buffer) {
          array_length = Math.floor(
            buffer.byteLength / array_width / Dtype.BYTES_PER_ELEMENT
          );
          length = buffer.byteLength - (buffer.byteLength % Dtype.BYTES_PER_ELEMENT);
          if (length === buffer.byteLength) {
            array = new Dtype(buffer);
          } else {
            array = new Dtype(buffer, 0, length);
          }
          return nj.ndarray(array, [array_length, array_width]);
        });
    };

 wendelin.getArrayRawSlice = function (gadget, key, start, end, column_list, Dtype) {
      var url,
        i,
        j,
        date_index_list,
        array_column,
        date_format,
        array_width;
      return gadget.getSetting("hateoas_url")
        .push(function (hateoas_url) {
          url =
            (new URI(hateoas_url)).absoluteTo(location.href).toString() + key +
            //add timestamp to url to not hit browser cache
            ((/\?/).test(url) ? "&" : "?") + (new Date()).getTime();
          return gadget.jio_get(key);
        })
        .push(function (doc) {

          doc = wendelin.asNormalArray(doc, column_list);
          date_index_list = doc.date_index_list;
          array_column = doc.array_column;
          date_format = doc.date_format;
          if (Dtype === undefined) {
            Dtype = DTYPE_DICT[doc.array_dtype];
          }
          array_width = doc.array_shape[1];

          if (column_list != undefined && column_list.length < array_column.length){
            url += ((/\?/).test(url) ? "&" : "?") + (new Date()).getTime();
            url +=  "&slice_index.start:records:int=" + start;
            if(end){
              url += "&slice_index.stop:records:int=" + end;
            }
            if (doc.array_type === wendelin.ARRAY_TYPE_DICT.STRUCTURE_ARRAY && column_list.length) {
              array_width = column_list.length;
              for (j = 0; j < column_list.length; j += 1) {
                url += "&list_index:list=" + column_list[j];
              }
            }
            return gadget.jio_getAttachment("erp5", url, {
              format : "array_buffer"
            });
          }
          else{
            if (end) {
              return gadget.jio_getAttachment("erp5", url, {
                start: start * array_width * Dtype.BYTES_PER_ELEMENT,
                end: end * array_width * Dtype.BYTES_PER_ELEMENT -1,
                format : "array_buffer"
              });
            }
            return gadget.jio_getAttachment("erp5", url, {
              start: start * array_width * Dtype.BYTES_PER_ELEMENT,
              format : "array_buffer"
            });
         }
        })
        .push(function (buffer) {
          var array,
            array_length = Math.floor(
              buffer.byteLength / array_width / Dtype.BYTES_PER_ELEMENT
            ),
            length = buffer.byteLength - (buffer.byteLength % Dtype.BYTES_PER_ELEMENT);
          if (length === buffer.byteLength) {
            array = new Dtype(buffer);
          } else {
            array = new Dtype(buffer, 0, length);
          }
          if(date_format === wendelin.DATE_FORMAT.NumpyDateTime64) {
            
            if(column_list){
              if (column_list.includes("date") || column_list.includes("start_date") || column_list.includes("stop_date") ){
                for (i = 0; i < date_index_list.length; i += 1) {
                  for (j = 0; j < column_list.length; j += 1) {
                    if (array_column[j][0] === date_index_list[i]) {
                      convertNumpyDateTime64ToPandasDateIndex(j, array, array_length, array_width, Dtype);
                    }
                  }
                }
              }
            }
            else{
              for (i = 0; i < date_index_list.length; i += 1) {
                for (j = 0; j < array_column.length; j += 1) {
                  if (array_column[j][0] === date_index_list[i]) {
                    convertNumpyDateTime64ToPandasDateIndex(j, array, array_length, array_width, Dtype);
                  }
                }
              }
            }
          }
          if(date_format === wendelin.DATE_FORMAT.SpecialInteger64Time) {
            for (i = 0; i < date_index_list.length; i += 1) {
              for (j = 0; j < column_list.length; j += 1) {
                if (array_column[j][0] === date_index_list[i]) {
                  convertNumpyDateTime64ToPandasDateIndex(j, array, array_length, array_width, Dtype);
                }
              }
            }
            for (var k = 0; k < array.length; k += 1){
              array[k] = (array[k] - 116444736000000000) / 1e4
            }
          }
          generateNumberFormat(array, array_length, array_width);
          return nj.ndarray(array, [array_length, array_width]);
        })
        .push(undefined, function (error) {
          if (!(error instanceof RSVP.CancellationError)) {
            console.error("following data array is not good: ");
            console.error(key);
          }
          return nj.ndarray([0], [1, 1]);
        });
    };

 wendelin.getArrayDateSlice = function (gadget, key, start_date, stop_date, column_list) {
      var url,
        Dtype,
        i,
        j,
        date_index_list,
        array_column,
        date_format,
        array_width;
      return gadget.getSetting("hateoas_url")
        .push(function (hateoas_url) {
          url =
            (new URI(hateoas_url)).absoluteTo(location.href).toString() + key +
            //add timestamp to url to not hit browser cache
            ((/\?/).test(url) ? "&" : "?") + (new Date()).getTime();
          return gadget.jio_get(key);
        })
        .push(function (doc) {

          doc = wendelin.asNormalArray(doc, column_list);
          date_index_list = doc.date_index_list;
          array_column = doc.array_column;
          date_format = doc.date_format;
          Dtype = DTYPE_DICT[doc.array_dtype];
          array_width = doc.array_shape[1];

          if (column_list != undefined && column_list.length < array_column.length){
            url += ((/\?/).test(url) ? "&" : "?") + (new Date()).getTime();
            url +=  "&start_date:string=" + start_date;
            url += "&stop_date:string=" + stop_date;

            if (doc.array_type === wendelin.ARRAY_TYPE_DICT.STRUCTURE_ARRAY && column_list.length) {
              array_width = column_list.length;
              for (j = 0; j < column_list.length; j += 1) {
                url += "&list_index:list=" + column_list[j];
              }
            }
            return gadget.jio_getAttachment("erp5", url, {
              format : "array_buffer"
            });
          }
        })
        .push(function (buffer) {
          var array,
            array_length = Math.floor(
              buffer.byteLength / array_width / Dtype.BYTES_PER_ELEMENT
            ),
            length = buffer.byteLength - (buffer.byteLength % Dtype.BYTES_PER_ELEMENT);
          if (length === buffer.byteLength) {
            array = new Dtype(buffer);
          } else {
            array = new Dtype(buffer, 0, length);
          }
          if(date_format === wendelin.DATE_FORMAT.NumpyDateTime64) {
            for (i = 0; i < date_index_list.length; i += 1) {
              for (j = 0; j < array_column.length; j += 1) {
                if (column_list[j] === date_index_list[i]) {
                  convertNumpyDateTime64ToPandasDateIndex(j, array, array_length, array_width, Dtype);
                }
              }
            }
          }
          if(date_format === wendelin.DATE_FORMAT.SpecialInteger64Time) {
            for (i = 0; i < date_index_list.length; i += 1) {
              for (j = 0; j < column_list.length; j += 1) {
                if (column_list[j] === date_index_list[i]) {
                  convertNumpyDateTime64ToPandasDateIndex(j, array, array_length, array_width, Dtype);
                }
              }
            }
            for (var k = 0; k < array.length; k += 1){
              array[k] = (array[k] - 116444736000000000) / 1e4
            }
          }
          generateNumberFormat(array, array_length, array_width);
          return nj.ndarray(array, [array_length, array_width]);
        })
        .push(undefined, function (error) {
          if (!(error instanceof RSVP.CancellationError)) {
            console.error("following data array is not good: ");
            console.error(key);
          }
          return nj.ndarray([0], [1, 1]);
        });
    };

    wendelin.getArrayLastRow = function (gadget, key) {
      return wendelin.getArrayRawSlice(gadget, key, -1);
    };

    wendelin.toLocaleDateString = function (date_float) {
      // return datetime like iso string
      // but in local timezone and without trailing 'Z'
      // this string format can be set to inpout type 'datetime-local'
      var date = new Date(date_float);
      date = new Date(date - date.getTimezoneOffset() * 60 * 1000);
      // strip trailing "Z"
      return date.toISOString().substr(0, 19);
    };

    wendelin.fromLocaleDateFloat = function (date_float) {
      return date_float + new Date(date_float).getTimezoneOffset() * 60 * 1000;
    };

    wendelin.fromLocaleDateString = function (date_string) {
      var date_float = new Date(date_string).valueOf();
      return new Date(wendelin.fromLocaleDateFloat(date_float));
    };
    
    wendelin.getTimeZoneOffset = function(time_zone_string, reference = new Date()) {
      var target_time = parseInt(reference.toLocaleTimeString('nl', {timeZone: time_zone_string }).substring(0, 2)),
        target_date = new Date(reference.toLocaleDateString('en-US', {timeZone: time_zone_string})),
        reference_time = parseInt(reference.toLocaleTimeString('nl').substring(0, 2)),
        reference_date = new Date(reference.toLocaleDateString('en-US')),
        reference_time_zone_offset = reference.getTimezoneOffset() / 60;
      if (target_date > reference_date) {
       target_time += 24;
      } else if (target_date < reference_date) {
        reference_time += 24;
      }
      
      return target_time - reference_time + (-1 * reference_time_zone_offset);
      
    };
    wendelin.dateValueFormater = function (ms) {
      var date = new Date(ms);
      return date.toISOString().substr(0, 10).replace(/-/g, '/') +  " " + date.toISOString().substr(11, 8);
    };

    wendelin.labelFormater = function (number) {
      var value = number.toString(),
        len_after_point = 0;
      if (value.indexOf('.') !== -1) {
        len_after_point = value.split('.')[1].length;
      } else {
        value += '.';
      }
      while (len_after_point < 3) {
        value += '0';
        len_after_point += 1;
      }
      return value;
    };
    /*function ndConvertFirstAxisToDate(array) {
      var i;
      // with pandas.DateIndex use / 1000000
      // with numpy.datetime64 use + 1428795657000
      for (i = 0; i < array.shape[0]; i += 1) {
        array.set(i, 0, new Date(array.get(i, 0) / 1000000));
      }
      return array;
    }*/

    wendelin.convertFirstColToDate = function (array, time_zone_offset = 0) {
      var i;
      // with pandas.DateIndex use / 1000000
      // with numpy.datetime64 use + 1428795657000
      for (i = 0; i < array.length; i += 1) {
        array[i][0] = new Date(array[i][0] / 1000000 +  time_zone_offset * 60 * 60 *1000);
      }
      return array;
    };

    wendelin.highlight_weekend = function (canvas, area, g) {

      canvas.fillStyle = "rgba(8,80,120, 0.1)";

      function highlight_period(x_start, x_end) {
        var canvas_left_x = g.toDomXCoord(x_start),
          canvas_right_x = g.toDomXCoord(x_end),
          canvas_width = canvas_right_x - canvas_left_x;
        canvas.fillRect(canvas_left_x, area.y, canvas_width, area.h);
      }

      var n,
        night_start_hour = 22,
        night_stop_hour = 6,
        night_span = 24 - night_start_hour + night_stop_hour,
        min_data_x = g.getValue(0, 0),
        max_data_x = g.getValue(g.numRows() - 1, 0),
        start_date = new Date(min_data_x),
        stop_date = new Date(min_data_x),
        start_x_highlight,
        end_x_highlight;

      if (night_span > 24) {
        night_span = night_stop_hour - night_start_hour;
      }

      // starting at night we find the day
      if (start_date.getHours() >= night_start_hour) {
        stop_date.setDate(stop_date.getDate() + 1);
        stop_date.setHours(night_stop_hour);
        stop_date.setMinutes(0);
        stop_date.setSeconds(0);
        stop_date.setMilliseconds(0);
        highlight_period(min_data_x, stop_date.getMilliseconds());
        start_date = stop_date;
      } else if (start_date.getHours() < night_stop_hour) {
        stop_date.setHours(night_stop_hour);
        stop_date.setMinutes(0);
        stop_date.setSeconds(0);
        stop_date.setMilliseconds(0);
        highlight_period(min_data_x, stop_date.getMilliseconds());
      }

      // set to start of first night
      start_date.setHours(night_start_hour);
      start_date.setMinutes(0);
      start_date.setSeconds(0);
      start_date.setMilliseconds(0);
      n = start_date.valueOf();
      while (n < max_data_x) {
        start_x_highlight = n;
        end_x_highlight = n + night_span * 3600 * 1000;
        // make sure we don't try to plot outside the graph
        if (start_x_highlight < min_data_x) {
          start_x_highlight = min_data_x;
        }
        if (end_x_highlight > max_data_x) {
          end_x_highlight = max_data_x;
        }
        highlight_period(start_x_highlight, end_x_highlight);
        // calculate start of highlight for next night
        n += 24 * 3600 * 1000;
      }
    };

    wendelin.syncArray = function (gadget,
                                   key,
                                   Dtype,
                                   resolution,
                                   array_start_date,
                                   array_width,
                                   start_date, stop_date) {
      var start_index,
        stop_index,
        array_length,
        start,
        end,
        length,
        array,
        prefix = "local_",
        url;
      resolution = wendelin.RESOLUTION_DICT[resolution];
      if (start_date < array_start_date) {
        stop_date = new Date(
          array_start_date.valueOf() +
          stop_date.valueOf() -
          start_date.valueOf()
        );
        start_date = array_start_date;
      }
      start_index = Math.floor((start_date - array_start_date) / resolution);
      stop_index = Math.floor((stop_date - array_start_date) / resolution);
      start = start_index * array_width * ARRAY_VALUE_LENGTH;
      end = stop_index * array_width * ARRAY_VALUE_LENGTH;
      return gadget.getSetting("hateoas_url")
        .push(function (hateoas_url) {
          url =
            (new URI(hateoas_url)).absoluteTo(location.href).toString() + key +
            //add timestamp to url to not hit browser cache
            ((/\?/).test(url) ? "&" : "?") + (new Date()).getTime();
          return RSVP.all([
            gadget.jio_.put(prefix + key, {"start_date": '' + start_date}),
            gadget.jio_getAttachment("erp5", url, {
              start : start,
              end : end - 1,
              format : "blob"
            })
          ]);
        })
        .push(function (result_list) {
          var blob = result_list[1];
          return gadget.jio_putAttachment(
            key,
            "array",
            blob
          );
        })
        .push(function () {
          return gadget.jio_getAttachment(prefix + key, "array", {
            format : "array_buffer"
          }
          );
        })
        .push(function (buffer) {
          array_length = Math.floor(
            buffer.byteLength / array_width / ARRAY_VALUE_LENGTH
          );
          length = buffer.byteLength - (buffer.byteLength % ARRAY_VALUE_LENGTH);
          if (length === buffer.byteLength) {
            array = new Dtype(buffer);
          } else {
            array = new Dtype(buffer, 0, length);
          }
          window.ndarray = nj.ndarray(array, [array_length, array_width]);
        });
    };

    return wendelin;
  }

  //define globally if it doesn't already exist
  if (typeof(wendelin) === 'undefined') {
    window.wendelin = define_wendelin();
  }

}(window));