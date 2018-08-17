
var Module = typeof pyodide !== 'undefined' ? pyodide : {};

if (!Module.expectedDataFileDownloads) {
  Module.expectedDataFileDownloads = 0;
  Module.finishedDataFileDownloads = 0;
}
Module.expectedDataFileDownloads++;
(function() {
 var loadPackage = function(metadata) {

    var PACKAGE_PATH;
    if (typeof window === 'object') {
      PACKAGE_PATH = window['encodeURIComponent'](window.location.pathname.toString().substring(0, window.location.pathname.toString().lastIndexOf('/')) + '/');
    } else if (typeof location !== 'undefined') {
      // worker
      PACKAGE_PATH = encodeURIComponent(location.pathname.toString().substring(0, location.pathname.toString().lastIndexOf('/')) + '/');
    } else {
      throw 'using preloaded data can only be done on a web page or in a web worker';
    }
    var PACKAGE_NAME = '/home/nexedir/pyodide/packages/python-dateutil/build/python-dateutil.data';
    var REMOTE_PACKAGE_BASE = 'python-dateutil.data';
    if (typeof Module['locateFilePackage'] === 'function' && !Module['locateFile']) {
      Module['locateFile'] = Module['locateFilePackage'];
      err('warning: you defined Module.locateFilePackage, that has been renamed to Module.locateFile (using your locateFilePackage for now)');
    }
    var REMOTE_PACKAGE_NAME = Module['locateFile'] ? Module['locateFile'](REMOTE_PACKAGE_BASE, '') : REMOTE_PACKAGE_BASE;
  
    var REMOTE_PACKAGE_SIZE = metadata.remote_package_size;
    var PACKAGE_UUID = metadata.package_uuid;
  
    function fetchRemotePackage(packageName, packageSize, callback, errback) {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', packageName, true);
      xhr.responseType = 'arraybuffer';
      xhr.onprogress = function(event) {
        var url = packageName;
        var size = packageSize;
        if (event.total) size = event.total;
        if (event.loaded) {
          if (!xhr.addedTotal) {
            xhr.addedTotal = true;
            if (!Module.dataFileDownloads) Module.dataFileDownloads = {};
            Module.dataFileDownloads[url] = {
              loaded: event.loaded,
              total: size
            };
          } else {
            Module.dataFileDownloads[url].loaded = event.loaded;
          }
          var total = 0;
          var loaded = 0;
          var num = 0;
          for (var download in Module.dataFileDownloads) {
          var data = Module.dataFileDownloads[download];
            total += data.total;
            loaded += data.loaded;
            num++;
          }
          total = Math.ceil(total * Module.expectedDataFileDownloads/num);
          if (Module['setStatus']) Module['setStatus']('Downloading data... (' + loaded + '/' + total + ')');
        } else if (!Module.dataFileDownloads) {
          if (Module['setStatus']) Module['setStatus']('Downloading data...');
        }
      };
      xhr.onerror = function(event) {
        throw new Error("NetworkError for: " + packageName);
      }
      xhr.onload = function(event) {
        if (xhr.status == 200 || xhr.status == 304 || xhr.status == 206 || (xhr.status == 0 && xhr.response)) { // file URLs can return 0
          var packageData = xhr.response;
          callback(packageData);
        } else {
          throw new Error(xhr.statusText + " : " + xhr.responseURL);
        }
      };
      xhr.send(null);
    };

    function handleError(error) {
      console.error('package error:', error);
    };
  
      var fetchedCallback = null;
      var fetched = Module['getPreloadedPackage'] ? Module['getPreloadedPackage'](REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE) : null;

      if (!fetched) fetchRemotePackage(REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE, function(data) {
        if (fetchedCallback) {
          fetchedCallback(data);
          fetchedCallback = null;
        } else {
          fetched = data;
        }
      }, handleError);
    
  function runWithFS() {

    function assert(check, msg) {
      if (!check) throw msg + new Error().stack;
    }
Module['FS_createPath']('/', 'lib', true, true);
Module['FS_createPath']('/lib', 'python3.6', true, true);
Module['FS_createPath']('/lib/python3.6', 'site-packages', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages', 'dateutil', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/dateutil', 'tz', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/dateutil', 'parser', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/dateutil', 'zoneinfo', true, true);

    function DataRequest(start, end, audio) {
      this.start = start;
      this.end = end;
      this.audio = audio;
    }
    DataRequest.prototype = {
      requests: {},
      open: function(mode, name) {
        this.name = name;
        this.requests[name] = this;
        Module['addRunDependency']('fp ' + this.name);
      },
      send: function() {},
      onload: function() {
        var byteArray = this.byteArray.subarray(this.start, this.end);
        this.finish(byteArray);
      },
      finish: function(byteArray) {
        var that = this;

        Module['FS_createPreloadedFile'](this.name, null, byteArray, true, true, function() {
          Module['removeRunDependency']('fp ' + that.name);
        }, function() {
          if (that.audio) {
            Module['removeRunDependency']('fp ' + that.name); // workaround for chromium bug 124926 (still no audio with this, but at least we don't hang)
          } else {
            err('Preloading file ' + that.name + ' failed');
          }
        }, false, true); // canOwn this data in the filesystem, it is a slide into the heap that will never change

        this.requests[this.name] = null;
      }
    };

        var files = metadata.files;
        for (var i = 0; i < files.length; ++i) {
          new DataRequest(files[i].start, files[i].end, files[i].audio).open('GET', files[i].filename);
        }

  
    function processPackageData(arrayBuffer) {
      Module.finishedDataFileDownloads++;
      assert(arrayBuffer, 'Loading data file failed.');
      assert(arrayBuffer instanceof ArrayBuffer, 'bad input to processPackageData');
      var byteArray = new Uint8Array(arrayBuffer);
      var curr;
      
        // copy the entire loaded file into a spot in the heap. Files will refer to slices in that. They cannot be freed though
        // (we may be allocating before malloc is ready, during startup).
        if (Module['SPLIT_MEMORY']) err('warning: you should run the file packager with --no-heap-copy when SPLIT_MEMORY is used, otherwise copying into the heap may fail due to the splitting');
        var ptr = Module['getMemory'](byteArray.length);
        Module['HEAPU8'].set(byteArray, ptr);
        DataRequest.prototype.byteArray = Module['HEAPU8'].subarray(ptr, ptr+byteArray.length);
  
          var files = metadata.files;
          for (var i = 0; i < files.length; ++i) {
            DataRequest.prototype.requests[files[i].filename].onload();
          }
              Module['removeRunDependency']('datafile_/home/nexedir/pyodide/packages/python-dateutil/build/python-dateutil.data');

    };
    Module['addRunDependency']('datafile_/home/nexedir/pyodide/packages/python-dateutil/build/python-dateutil.data');
  
    if (!Module.preloadResults) Module.preloadResults = {};
  
      Module.preloadResults[PACKAGE_NAME] = {fromCache: false};
      if (fetched) {
        processPackageData(fetched);
        fetched = null;
      } else {
        fetchedCallback = processPackageData;
      }
    
  }
  if (Module['calledRun']) {
    runWithFS();
  } else {
    if (!Module['preRun']) Module['preRun'] = [];
    Module["preRun"].push(runWithFS); // FS is not initialized yet, wait for it
  }

 }
 loadPackage({"files": [{"start": 0, "audio": 0, "end": 116, "filename": "/lib/python3.6/site-packages/dateutil/_version.py"}, {"start": 116, "audio": 0, "end": 338, "filename": "/lib/python3.6/site-packages/dateutil/__init__.py"}, {"start": 338, "audio": 0, "end": 1270, "filename": "/lib/python3.6/site-packages/dateutil/_common.py"}, {"start": 1270, "audio": 0, "end": 3111, "filename": "/lib/python3.6/site-packages/dateutil/utils.py"}, {"start": 3111, "audio": 0, "end": 5795, "filename": "/lib/python3.6/site-packages/dateutil/easter.py"}, {"start": 5795, "audio": 0, "end": 5854, "filename": "/lib/python3.6/site-packages/dateutil/tzwin.py"}, {"start": 5854, "audio": 0, "end": 70721, "filename": "/lib/python3.6/site-packages/dateutil/rrule.py"}, {"start": 70721, "audio": 0, "end": 95214, "filename": "/lib/python3.6/site-packages/dateutil/relativedelta.py"}, {"start": 95214, "audio": 0, "end": 106532, "filename": "/lib/python3.6/site-packages/dateutil/tz/win.py"}, {"start": 106532, "audio": 0, "end": 162912, "filename": "/lib/python3.6/site-packages/dateutil/tz/tz.py"}, {"start": 162912, "audio": 0, "end": 164346, "filename": "/lib/python3.6/site-packages/dateutil/tz/_factories.py"}, {"start": 164346, "audio": 0, "end": 164849, "filename": "/lib/python3.6/site-packages/dateutil/tz/__init__.py"}, {"start": 164849, "audio": 0, "end": 177741, "filename": "/lib/python3.6/site-packages/dateutil/tz/_common.py"}, {"start": 177741, "audio": 0, "end": 233499, "filename": "/lib/python3.6/site-packages/dateutil/parser/_parser.py"}, {"start": 233499, "audio": 0, "end": 235226, "filename": "/lib/python3.6/site-packages/dateutil/parser/__init__.py"}, {"start": 235226, "audio": 0, "end": 248071, "filename": "/lib/python3.6/site-packages/dateutil/parser/isoparser.py"}, {"start": 248071, "audio": 0, "end": 387151, "filename": "/lib/python3.6/site-packages/dateutil/zoneinfo/dateutil-zoneinfo.tar.gz"}, {"start": 387151, "audio": 0, "end": 393040, "filename": "/lib/python3.6/site-packages/dateutil/zoneinfo/__init__.py"}, {"start": 393040, "audio": 0, "end": 394759, "filename": "/lib/python3.6/site-packages/dateutil/zoneinfo/rebuild.py"}], "remote_package_size": 394759, "package_uuid": "614b64f0-c002-400b-a8f6-3463a8dfc734"});

})();
