import logging
import mimetypes
import os
import pathlib
import shutil
import urllib
import requests
import uuid

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
        self.path = str(os.path.join(self._ctx.path, '.sourceknight', directory))
        self._entire_dir = entire_directory
        mimetypes.init()

    def __enter__(self):
        ensure_path_exists(self.path)
        return self

    def __exit__(self, *exc):
        for f in self._tmpfiles:
            try:
                os.unlink(f)
            except OSError:
                pass
        if self._entire_dir:
            shutil.rmtree(self.path)

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

        tmp = os.path.join(self.path, '{}{}'.format(uuid.uuid4().hex, ext))
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
    fn.already_run = False
    fn.last_res = None
    def wrapped(*args, **kwargs):
        if fn.already_run:
            return fn.last_res
        fn._last_res = fn(*args, **kwargs)
        return fn.last_res
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


def extract_and_copy(drvcls, locations, mgr, tmp):
    from sourceknight.drivers import gitdriver
    for l in locations:
        if l['source'][0] == '/':
            l['source'] = l['source'][1:]
        if l['dest'][0] == '/':
            l['dest'] = l['dest'][1:]

        src = os.path.normpath(os.path.join(tmp.path, str(l['source'])))
        dst = os.path.normpath(os.path.join(mgr.path, str(l['dest'])))

        if isinstance(drvcls, gitdriver):
            src = os.path.normpath(os.path.join(str(drvcls.model.params['location']), l['source']))

        logging.info("Extracting {} to {}".format(src, dst))

        if not os.path.exists(src):
            logging.error("Source path does not exist: {}".format(src))
            continue

        if os.path.isdir(src):
            ensure_path_exists(dst)
            copy_func = shutil.copytree
            copy_args = {'dirs_exist_ok': True}
        else:
            ensure_path_exists(os.path.dirname(dst))
            copy_func = shutil.copy
            copy_args = {}

        try:
            copy_func(src, dst, **copy_args)
        except Exception as e:
            logging.error("Error copying from {} to {}: {}".format(src, dst, e))

    drvcls.ctx.state.update(build={
        drvcls.model.name: drvcls.model.state(driver=drvcls.model.type)
    })


def tar_is_within_directory(directory, target):
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)

    prefix = os.path.commonprefix([abs_directory, abs_target])

    return prefix == abs_directory


def tar_safe_extract(tar, path=".", members=None, *, numeric_owner=False):
    for member in tar.getmembers():
        member_path = os.path.join(path, member.name)
        if not tar_is_within_directory(path, member_path):
            raise Exception("Attempted Path Traversal in Tar File")

    tar.extractall(path, members, numeric_owner=numeric_owner)