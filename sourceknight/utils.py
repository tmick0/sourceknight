import requests
import urllib
import os
import pathlib
import uuid
import mimetypes
import logging
import shutil

from urllib.request import url2pathname


# https://stackoverflow.com/a/27786580
class LocalFileAdapter(requests.adapters.BaseAdapter):
    @staticmethod
    def _chkpath(method, path):
        if method.lower() in ('put', 'delete'):
            return 501, "Not Implemented"  # TODO
        elif method.lower() not in ('get', 'head'):
            return 405, "Method Not Allowed"
        elif os.path.isdir(path):
            return 400, "Path Not A File"
        elif not os.path.isfile(path):
            return 404, "File Not Found"
        elif not os.access(path, os.R_OK):
            return 403, "Access Denied"
        else:
            return 200, "OK"

    def send(self, req, **kwargs):
        path = os.path.normcase(os.path.normpath(url2pathname(req.path_url)))
        response = requests.Response()

        response.status_code, response.reason = self._chkpath(req.method, path)
        if response.status_code == 200 and req.method.lower() != 'head':
            try:
                response.raw = open(path, 'rb')
            except (OSError, IOError) as err:
                response.status_code = 500
                response.reason = str(err)

        if isinstance(req.url, bytes):
            response.url = req.url.decode('utf-8')
        else:
            response.url = req.url

        response.request = req
        response.connection = self

        return response

    def close(self):
        pass


def ensure_path_exists(p):
    pathlib.Path(p).mkdir(parents=True, exist_ok=True)


class filemgr (object):
    def __init__(self, ctx, directory, entire_directory=False):
        self._ctx = ctx
        self._sess = requests.session()
        self._sess.mount("file://", LocalFileAdapter)
        self._tmpfiles = []
        self._path = os.path.join(self._ctx._path, '.sourceknight', directory)
        self._entire_dir = entire_directory
        mimetypes.init()

    def __enter__(self):
        ensure_path_exists(self._path)
        return self

    def __exit__(self, *exc):
        for f in self._tmpfiles:
            try:
                os.unlink(f)
            except OSError:
                pass
        if self._entire_dir:
            shutil.rmtree(self._path)

    def release_dir(self):
        self._entire_dir = False

    def release(self, file):
        self._tmpfiles.remove(file)

    def acquire(self, url):
        logging.info(" Downloading {}...".format(url))
        req = self._sess.get(url)

        ext = mimetypes.guess_extension(req.headers['content-type'])
        if ext is None:
            ext = mimetypes.guess_extension(mimetypes.guess_type(url)[0])
        if ext is None:
            ext = os.path.splitext(urllib.parse.urlparse(url).path)[1]

        tmp = os.path.join(self._path, '{}{}'.format(uuid.uuid4().hex, ext))
        self._tmpfiles.append(tmp)

        with open(tmp, 'wb') as fh:
            fh.write(req.content)

        return tmp
