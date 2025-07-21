/*global window, rJS, nj */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, nj) {
  "use strict";

  // parse dict in string in python pprint.pfromat
  function parserPythonPformatDict(s) {
    s = s
      .replace(/False/g, "false")
      .replace(/True/g, "true")
      .replace(/\(/g, "[")
      .replace(/\)/g, "]")
      .replace(/, }/g, "}")
      .replace(/\'/g, '"')
    return JSON.parse(s);
  }

  // Initial idea from https://github.com/BillMills/numpychuck/blob/master/helpers.js
  // https://github.com/numpy/numpy/blob/master/doc/neps/npy-format.rst#format-specification-version-10
  function unpackNPY(dv) {
    return new RSVP.Queue()
      .push(function () {
        var HEADER_LEN = dv.getUint16(8, true),
          offset = HEADER_LEN + 10, 
          dataLength = dv.byteLength - offset,
          i,
          header_string = '',
          char,
          header_dict,
          value_length,
          getValue,
          shape = [],
          array = [],
          value;

        for (i = 10; i <= offset; i ++) {
          char = String.fromCharCode(dv.getUint8(i, true));
          header_string += char;
          if (char == '}') {
            break;
          }
        }
        header_dict = parserPythonPformatDict(header_string);
        return unpackArray(dv, header_dict, offset);
    });
  }

  // Initial idea from https://github.com/BillMills/numpychuck/blob/master/helpers.js
  // https://github.com/numpy/numpy/blob/master/doc/neps/npy-format.rst#format-specification-version-10
  function unpackArray(dv, header_dict, offset) {
    var i,
      array = [];
    if (offset === undefined) {
      offset = 0;
    }
    return new RSVP.Queue()
      .push(function () {
        if ((header_dict.descr === "<i8")
            & (header_dict.fortran_order == false)) {
          for (i = 0; i < dv.byteLength - offset - 1; i += 8) {
            array.push(dv.getUint8(i + offset, true))
          }
        } else if (header_dict.descr == "<f8"
            & (header_dict.fortran_order == false)) {
          for (i = 0; i < dv.byteLength - offset - 1; i += 8) {
            array.push(dv.getFloat64(i + offset, true))
          }
        } else {
          throw("Unsupported dtype: " + header_dict.descr +
            " with fortran_order = " + header_dict.fortran_order);
        }
        return nj.ndarray(array, header_dict.shape);
    });
  }

  rJS(window)

    .ready(function (gadget) {
    })

    .declareMethod('unpackNPY', function () {
      return unpackNPY(arguments[0]);
    })

    .declareMethod('unpackArray', function () {
      return unpackArray(arguments[0], arguments[1]);
    })


}(window, rJS, nj));