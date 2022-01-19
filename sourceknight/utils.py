from re import L
import requests
import urllib
import os
import pathlib
import uuid
import mimetypes
import logging
import shutil
import logging

from importlib.metadata import version
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


class cd (object):
    def __init__(self, path):
        self._path = path
    def __enter__(self):
        self._prev = os.getcwd()
        os.chdir(self._path)
    def __exit__(self, *exc):
        os.chdir(self._prev)


def once(fn):
    fn._already_run = False
    fn._last_res = None
    def wrapped(*args, **kwargs):
        if fn._already_run:
            return fn._last_res
        fn._last_res = fn(*args, **kwargs)
        return fn._last_res
    return wrapped


class skversion (object):

    class compat (object):
        major = False
        newer = False

    def __init__(self, v):
        v = str(v)
        self.major, self.minor = map(int, v.split('.', 2))
    
    def compatibility(self, other):
        res = skversion.compat()
        if self.major != other.major:
            res.major = True
        elif self.minor < other.minor:
            res.newer = True
        return res

    def __str__(self):
        return "{:d}.{:d}".format(self.major, self.minor)


@once
def check_version(defs):
    try:
        ver = defs['project']['sourceknight']
    except KeyError:
        logging.warning("No version detected in manifest, defaulting to 0.1. In the future, a version will be required in the manifest.")
        ver = "0.1"
    ver = skversion(ver)
    cur = skversion(version('sourceknight'))
    err = RuntimeError("this version of sourceknight is incompatible with this manifest")
    compat = cur.compatibility(ver)
    if compat.major:
        logging.error("This manifest is from a different major version of sourceknight than what is currently installed ({} vs {})".format(ver, cur))
        raise err
    if compat.newer:
        logging.error("This manifest requires a newer version of sourceknight than is currently installed ({} vs {})".format(ver, cur))
        raise err
