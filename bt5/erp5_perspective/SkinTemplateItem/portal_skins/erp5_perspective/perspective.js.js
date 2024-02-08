import 'https://cdn.jsdelivr.net/npm/@finos/perspective-viewer@2.7.1/dist/cdn/perspective-viewer.js';
import 'https://cdn.jsdelivr.net/npm/@finos/perspective-viewer-datagrid@2.7.1/dist/cdn/perspective-viewer-datagrid.js';
import 'https://cdn.jsdelivr.net/npm/@finos/perspective-viewer-d3fc@2.7.1/dist/cdn/perspective-viewer-d3fc.js';

import {
  worker
} from "https://cdn.jsdelivr.net/npm/@finos/perspective@2.7.1/dist/cdn/perspective.js";

var WORKER = worker();
(function (window, rJS) {
  "use strict";
  rJS(window)
    .declareMethod("getTable", function (data) {
      return WORKER.table(data);
    });

}(window, rJS));