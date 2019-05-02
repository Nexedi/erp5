import os
import sys
import argparse
import posixpath
from gevent import pywsgi, threadpool
from tempfile import TemporaryFile
from io import BytesIO
import socket
import Zope2
from Zope2.Startup.run import make_wsgi_app
import ZConfig
from Products.ERP5Type.patches.WSGIPublisher import publish_module


def app_wrapper(large_file_threshold, use_webdav):
  def app(environ, start_response):
    original_wsgi_input = environ['wsgi.input']
    if not hasattr(original_wsgi_input, 'seek'):
      # Convert environ['wsgi.input'] to a file-like object.
      cl = environ.get('CONTENT_LENGTH')
      cl = int(cl) if cl else 0
      if cl > large_file_threshold:
        new_wsgi_input = environ['wsgi.input'] = TemporaryFile('w+b')
      else:
        new_wsgi_input = environ['wsgi.input'] = BytesIO()

      rest = cl
      chunksize = 1<<20
      try:
        while rest:
          if rest <= chunksize:
            chunk = original_wsgi_input.read(rest)
            rest = 0
          else:
            chunk = original_wsgi_input.read(chunksize)
            rest = rest - chunksize
          new_wsgi_input.write(chunk)
      except (socket.error, IOError):
        msg = b'Not enough data in request or socket error'
        start_response('400 Bad Request', [
          ('Content-Type', 'text/plain'),
          ('Content-Length', str(len(msg))),
          ]
        )
        return [msg]
      new_wsgi_input.seek(0)

    if use_webdav:
      # Munge the request to ensure that we call manage_FTPGet.

      # Set a flag to indicate this request came through the WebDAV source
      # port server.
      environ['WEBDAV_SOURCE_PORT'] = 1

      if environ['REQUEST_METHOD'] == 'GET':
        path_info = environ['PATH_INFO']
        if os.sep != '/':
          path_info =  path_info.replace(os.sep, '/')
        path_info = posixpath.join(path_info, 'manage_DAVget')
        path_info = posixpath.normpath(path_info)
        environ['PATH_INFO'] = path_info

    return publish_module(environ, start_response)
  return app


def runwsgi():
  parser = argparse.ArgumentParser()
  parser.add_argument('-w', '--webdav', action='store_true')
  parser.add_argument('address', help='<ip>:<port>')
  parser.add_argument('zope_conf', help='path to zope.conf')
  args = parser.parse_args()

  startup = os.path.dirname(Zope2.Startup.__file__)
  schema = ZConfig.loadSchema(os.path.join(startup, 'zopeschema.xml'))
  conf, _ = ZConfig.loadConfig(schema, args.zope_conf)

  make_wsgi_app({}, zope_conf=args.zope_conf)

  pywsgi.WSGIServer(
    listener=args.address,
    application=app_wrapper(conf.large_file_threshold, args.webdav),
    spawn=threadpool.ThreadPool(conf.zserver_threads),
    log=conf.access(),  # Z2.log
  ).serve_forever()
