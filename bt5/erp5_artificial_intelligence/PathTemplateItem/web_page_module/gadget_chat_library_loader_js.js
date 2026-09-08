/*global self, fetch, indexedDB, eval */

(function (self) {
  "use strict";

  var LIBRARY_CATALOG = {
    lodash: {
      url: 'https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js',
      global: '_',
      description: 'General-purpose utility library (collections, arrays, objects, functions).'
    },
    dayjs: {
      url: 'https://cdn.jsdelivr.net/npm/dayjs@1.11.13/dayjs.min.js',
      global: 'dayjs',
      description: 'Date parsing, manipulation and formatting.'
    },
    papaparse: {
      url: 'https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js',
      global: 'Papa',
      description: 'CSV/TSV parse and unparse.'
    },
    'js-yaml': {
      url: 'https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js',
      global: 'jsyaml',
      description: 'YAML parse and dump.'
    },
    jszip: {
      url: 'https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js',
      global: 'JSZip',
      description: 'Read/write .zip archives.'
    }
  };

  var LIBRARY_DB_NAME = 'gadget_chat_library_cache';
  var LIBRARY_DB_STORE = 'libs';

  function openLibraryDb() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(LIBRARY_DB_NAME, 1);
      req.onupgradeneeded = () => { req.result.createObjectStore(LIBRARY_DB_STORE); };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  function libraryDbGet(db, key) {
    return new Promise((resolve, reject) => {
      const req = db.transaction(LIBRARY_DB_STORE, 'readonly').objectStore(LIBRARY_DB_STORE).get(key);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  function libraryDbPut(db, key, value) {
    return new Promise((resolve, reject) => {
      const req = db.transaction(LIBRARY_DB_STORE, 'readwrite').objectStore(LIBRARY_DB_STORE).put(value, key);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  /** Fetch (or reuse a cached copy of) a catalog entry's source text. */
  async function fetchLibrarySource(name) {
    const entry = LIBRARY_CATALOG[name];
    if (!entry) {
      throw new Error(`unknown library "${name}" - use job kind "library_list" to see the catalog`);
    }
    const db = await openLibraryDb();
    const cached = await libraryDbGet(db, name);
    if (cached && cached.url === entry.url) return cached.source;
    const res = await fetch(entry.url);
    if (!res.ok) throw new Error(`fetching "${name}" failed: HTTP ${res.status}`);
    const source = await res.text();
    await libraryDbPut(db, name, { url: entry.url, source, fetched_at: Date.now() });
    return source;
  }

  /**
   * Load and evaluate catalog libraries by name, attaching each one's UMD
   * global onto this worker's global scope (`self`), and return a
   * {name: value} map for code that prefers `lib.lodash` over the bare
   * global `_`.
   */
  async function loadLibraries(names) {
    const lib = {};
    for (const name of names || []) {
      const entry = LIBRARY_CATALOG[name];
      if (!entry) throw new Error(`unknown library "${name}" - use job kind "library_list" to see the catalog`);
      const source = await fetchLibrarySource(name);
      if (self[entry.global] === undefined) {
        (0, eval)(source); // indirect eval: runs as global-scope code, attaches onto self
      }
      lib[name] = self[entry.global];
    }
    return lib;
  }

  self.ChatLibraryLoader = { LIBRARY_CATALOG: LIBRARY_CATALOG, loadLibraries: loadLibraries };
}(self));
