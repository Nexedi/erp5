
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
    var PACKAGE_NAME = 'build/dateutil.data';
    var REMOTE_PACKAGE_BASE = 'dateutil.data';
    if (typeof Module['locateFilePackage'] === 'function' && !Module['locateFile']) {
      Module['locateFile'] = Module['locateFilePackage'];
      Module.printErr('warning: you defined Module.locateFilePackage, that has been renamed to Module.locateFile (using your locateFilePackage for now)');
    }
    var REMOTE_PACKAGE_NAME = typeof Module['locateFile'] === 'function' ?
                              Module['locateFile'](REMOTE_PACKAGE_BASE) :
                              ((Module['filePackagePrefixURL'] || '') + REMOTE_PACKAGE_BASE);
  
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
Module['FS_createPath']('/lib/python3.6/site-packages/dateutil', 'zoneinfo', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/dateutil', 'tz', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/dateutil', 'parser', true, true);

    function DataRequest(start, end, crunched, audio) {
      this.start = start;
      this.end = end;
      this.crunched = crunched;
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

        Module['FS_createDataFile'](this.name, null, byteArray, true, true, true); // canOwn this data in the filesystem, it is a slide into the heap that will never change
        Module['removeRunDependency']('fp ' + that.name);

        this.requests[this.name] = null;
      }
    };

        var files = metadata.files;
        for (var i = 0; i < files.length; ++i) {
          new DataRequest(files[i].start, files[i].end, files[i].crunched, files[i].audio).open('GET', files[i].filename);
        }

  
    function processPackageData(arrayBuffer) {
      Module.finishedDataFileDownloads++;
      assert(arrayBuffer, 'Loading data file failed.');
      assert(arrayBuffer instanceof ArrayBuffer, 'bad input to processPackageData');
      var byteArray = new Uint8Array(arrayBuffer);
      var curr;
      
        // copy the entire loaded file into a spot in the heap. Files will refer to slices in that. They cannot be freed though
        // (we may be allocating before malloc is ready, during startup).
        if (Module['SPLIT_MEMORY']) Module.printErr('warning: you should run the file packager with --no-heap-copy when SPLIT_MEMORY is used, otherwise copying into the heap may fail due to the splitting');
        var ptr = Module['getMemory'](byteArray.length);
        Module['HEAPU8'].set(byteArray, ptr);
        DataRequest.prototype.byteArray = Module['HEAPU8'].subarray(ptr, ptr+byteArray.length);
  
          var files = metadata.files;
          for (var i = 0; i < files.length; ++i) {
            DataRequest.prototype.requests[files[i].filename].onload();
          }
              Module['removeRunDependency']('datafile_build/dateutil.data');

    };
    Module['addRunDependency']('datafile_build/dateutil.data');
  
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
 loadPackage({"files": [{"audio": 0, "start": 0, "crunched": 0, "end": 116, "filename": "/lib/python3.6/site-packages/dateutil/_version.py"}, {"audio": 0, "start": 116, "crunched": 0, "end": 64983, "filename": "/lib/python3.6/site-packages/dateutil/rrule.py"}, {"audio": 0, "start": 64983, "crunched": 0, "end": 89476, "filename": "/lib/python3.6/site-packages/dateutil/relativedelta.py"}, {"audio": 0, "start": 89476, "crunched": 0, "end": 91317, "filename": "/lib/python3.6/site-packages/dateutil/utils.py"}, {"audio": 0, "start": 91317, "crunched": 0, "end": 91376, "filename": "/lib/python3.6/site-packages/dateutil/tzwin.py"}, {"audio": 0, "start": 91376, "crunched": 0, "end": 92308, "filename": "/lib/python3.6/site-packages/dateutil/_common.py"}, {"audio": 0, "start": 92308, "crunched": 0, "end": 94992, "filename": "/lib/python3.6/site-packages/dateutil/easter.py"}, {"audio": 0, "start": 94992, "crunched": 0, "end": 95214, "filename": "/lib/python3.6/site-packages/dateutil/__init__.py"}, {"audio": 0, "start": 95214, "crunched": 0, "end": 96933, "filename": "/lib/python3.6/site-packages/dateutil/zoneinfo/rebuild.py"}, {"audio": 0, "start": 96933, "crunched": 0, "end": 236013, "filename": "/lib/python3.6/site-packages/dateutil/zoneinfo/dateutil-zoneinfo.tar.gz"}, {"audio": 0, "start": 236013, "crunched": 0, "end": 241902, "filename": "/lib/python3.6/site-packages/dateutil/zoneinfo/__init__.py"}, {"audio": 0, "start": 241902, "crunched": 0, "end": 253220, "filename": "/lib/python3.6/site-packages/dateutil/tz/win.py"}, {"audio": 0, "start": 253220, "crunched": 0, "end": 309600, "filename": "/lib/python3.6/site-packages/dateutil/tz/tz.py"}, {"audio": 0, "start": 309600, "crunched": 0, "end": 311034, "filename": "/lib/python3.6/site-packages/dateutil/tz/_factories.py"}, {"audio": 0, "start": 311034, "crunched": 0, "end": 323926, "filename": "/lib/python3.6/site-packages/dateutil/tz/_common.py"}, {"audio": 0, "start": 323926, "crunched": 0, "end": 324429, "filename": "/lib/python3.6/site-packages/dateutil/tz/__init__.py"}, {"audio": 0, "start": 324429, "crunched": 0, "end": 380187, "filename": "/lib/python3.6/site-packages/dateutil/parser/_parser.py"}, {"audio": 0, "start": 380187, "crunched": 0, "end": 393032, "filename": "/lib/python3.6/site-packages/dateutil/parser/isoparser.py"}, {"audio": 0, "start": 393032, "crunched": 0, "end": 394759, "filename": "/lib/python3.6/site-packages/dateutil/parser/__init__.py"}], "remote_package_size": 394759, "package_uuid": "315da47b-6ab5-4ee1-9c56-1c74dbf3d986"});

})();
