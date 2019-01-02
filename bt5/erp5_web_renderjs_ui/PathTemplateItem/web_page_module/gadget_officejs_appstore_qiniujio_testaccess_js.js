/*global document, QUnit, jIO */
/*jslint indent: 2, maxlen: 80, nomen: true, unparam: true, bitwise: true */
(function (document, jIO, QUnit) {
  "use strict";
  var test = QUnit.test,
    stop = QUnit.stop,
    start = QUnit.start,
    ok = QUnit.ok,
    equal = QUnit.equal,
//     throws = QUnit.throws,
    deepEqual = QUnit.deepEqual,
//     module = QUnit.module,

    // XXX Hardcoded informations
    qiniu_jio = jIO.createJIO({
      "type": "qiniu",
      "bucket": "uth6nied",
      "access_key": "34-UvLpN41_iMmJV388Hdp757yI3z_UBn5H9-wlJ",
      "secret_key": "ANzxRx1BxocCHCNTicBvhcvdIHmNJUlQKOeeGlpV"
    });

  QUnit.config.testTimeout = 60000;

  test('Create a file', function () {
    var key = "created_file";
    stop();
    qiniu_jio
      .post({_id: key})
      .then(function (result) {
        deepEqual(result, {
          "id": "created_file",
          "method": "post",
          "result": "success",
          "status": 201,
          "statusText": "Created"
        });
      })
      .fail(function (e) {
        ok(false, e);
      })
      .always(function () {
        start();
      });
  });

  test('Update a file', function () {
    var key = "updated_file";
    stop();
    qiniu_jio
      .post({_id: key})
      .then(function () {
        return qiniu_jio.put({_id: key});
      })
      .then(function (result) {
        equal(result.id, "updated_file");
        equal(result.method, "put");
        equal(result.result, "success");
        equal(result.status, 204);
        equal(result.statusText, "No Content");
      })
      .fail(function (e) {
        ok(false, e);
      })
      .always(function () {
        start();
      });
  });

  test('Download a new file', function () {
    var key = "downloaded_file";
    stop();
    qiniu_jio
      .post({_id: key})
      .then(function () {
        return qiniu_jio.get({_id: key});
      })
      .then(function (result) {
        deepEqual(result, {
          "data": {
            "_id": "downloaded_file"
          },
          "id": "downloaded_file",
          "method": "get",
          "result": "success",
          "status": 200,
          "statusText": "Ok"
        });
      })
      .fail(function (e) {
        ok(false, e);
      })
      .always(function () {
        start();
      });
  });

  test('Download an updated new file', function () {
    var key = "downloaded_updated_file";
    stop();
    qiniu_jio
      .post({_id: key, value: "foo"})
      .then(function () {
        return qiniu_jio.get({_id: key});
      })
      .then(function (result) {
        deepEqual(result, {
          "data": {
            "_id": "downloaded_updated_file",
            "value": "foo"
          },
          "id": "downloaded_updated_file",
          "method": "get",
          "result": "success",
          "status": 200,
          "statusText": "Ok"
        });
      })
      .then(function () {
        return qiniu_jio.get({_id: key, value: "bar"});
      })
      .then(function () {
        return qiniu_jio.get({_id: key});
      })
      .then(function (result) {
        deepEqual(result, {
          "data": {
            "_id": "downloaded_updated_file",
            "value": "bar"
          },
          "id": "downloaded_updated_file",
          "method": "get",
          "result": "success",
          "status": 200,
          "statusText": "Ok"
        });
      })
      .fail(function (e) {
        ok(false, e);
      })
      .always(function () {
        start();
      });
  });

  test('Delete a file', function () {
    var key = "file_to_delete";
    stop();
    qiniu_jio
      .post({_id: key})
      .then(function () {
        return qiniu_jio.remove({_id: key});
      })
      .then(function (result) {
        ok(true, result);
      })
      .fail(function (e) {
        ok(false);
      })
      .always(function () {
        start();
      });
  });

  test('List all files', function () {
    var key = "file_to_list";
    stop();
    qiniu_jio
      .post({_id: key})
      .then(function () {
        return qiniu_jio.allDocs();
      })
      .then(function (result) {
        ok(true, result);
      })
      .fail(function (e) {
        ok(false);
      })
      .always(function () {
        start();
      });
  });

}(document, jIO, QUnit));
